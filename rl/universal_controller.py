"""
Universal RL Controller - Manages any app via app-spec
Handles: state extraction, action selection, reward computation, policy updates
"""
import json
import csv
import os
from datetime import datetime
from pathlib import Path

class UniversalRLController:
    def __init__(self, specs_dir="app_specs", logs_dir="logs/rl_universal"):
        self.specs_dir = specs_dir
        self.logs_dir = logs_dir
        self.q_table = {}
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2
        Path(logs_dir).mkdir(parents=True, exist_ok=True)
        self.log_file = f"{logs_dir}/rl_events.csv"
        self._init_log()
    
    def _init_log(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'app_name', 'env', 'state', 'action', 'reward', 'q_value'])
    
    def load_app_spec(self, app_name):
        """Load and validate app specification"""
        spec_path = f"{self.specs_dir}/{app_name}.json"
        if not os.path.exists(spec_path):
            raise FileNotFoundError(f"App spec not found: {spec_path}")
        
        with open(spec_path, 'r') as f:
            spec = json.load(f)
        
        # Validate app spec schema
        if not self._validate_app_spec(spec):
            raise ValueError(f"Invalid app spec for {app_name}: Schema validation failed")
        
        return spec
    
    def _validate_app_spec(self, spec):
        """Validate app spec against required schema"""
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in spec:
                return False
        
        # Validate scaling configuration
        if 'scaling' in spec:
            scaling = spec['scaling']
            if 'max_workers' in scaling and scaling['max_workers'] > 10:
                return False  # Safety constraint
            if 'min_workers' in scaling and scaling['min_workers'] < 1:
                return False
        
        # Validate custom actions
        if 'custom_actions' in spec:
            allowed_actions = ['deploy', 'stop', 'restart', 'scale_up', 'scale_down', 'rollback']
            for action in spec['custom_actions']:
                if action not in allowed_actions:
                    return False
        
        return True
    
    def get_state(self, app_name, env):
        from rl.app_state_mapper import extract_state
        return extract_state(app_name, env)
    
    def choose_action(self, state, app_spec):
        from rl.app_action_space import get_valid_actions
        import random
        
        valid_actions = get_valid_actions(app_spec)
        
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        
        q_values = {a: self.q_table.get((state, a), 0.0) for a in valid_actions}
        max_q = max(q_values.values())
        best_actions = [a for a, q in q_values.items() if q == max_q]
        return random.choice(best_actions)
    
    def execute_action(self, action, app_name, env, orchestrator_api):
        if action == "deploy":
            return orchestrator_api.deploy_app(app_name, env)
        elif action == "stop":
            return orchestrator_api.stop_app(app_name, env)
        elif action == "scale_up":
            return orchestrator_api.scale(app_name, env, direction="up")
        elif action == "scale_down":
            return orchestrator_api.scale(app_name, env, direction="down")
        elif action == "restart":
            orchestrator_api.stop_app(app_name, env)
            return orchestrator_api.deploy_app(app_name, env)
        else:
            return {"status": "unknown_action"}
    
    def compute_reward(self, pre_state, post_state):
        """Advanced reward function with latency gradients and long-term penalties"""
        reward = 0.0
        
        # Status transition rewards
        if post_state.get('status') == 'healthy' and pre_state.get('status') != 'healthy':
            reward += 15.0
        elif post_state.get('status') == 'failed':
            reward -= 20.0
        elif post_state.get('status') == 'degraded':
            reward -= 5.0
        
        # Latency gradient rewards (fine-grained)
        pre_latency = pre_state.get('response_time', 1000)
        post_latency = post_state.get('response_time', 1000)
        latency_improvement = (pre_latency - post_latency) / pre_latency if pre_latency > 0 else 0
        reward += latency_improvement * 10.0
        
        # Partial degradation penalties
        pre_error = pre_state.get('error_rate', 0.0)
        post_error = post_state.get('error_rate', 0.0)
        error_delta = post_error - pre_error
        if error_delta > 0:
            reward -= error_delta * 25.0
        else:
            reward += abs(error_delta) * 15.0
        
        # Long-term stability penalties
        if post_state.get('status') == 'healthy':
            uptime = post_state.get('uptime', 0)
            if uptime < 300:
                reward -= 3.0
            elif uptime > 3600:
                reward += 2.0
        
        # Resource efficiency rewards
        cpu_usage = post_state.get('cpu_usage', 0.5)
        memory_usage = post_state.get('memory_usage', 0.5)
        if cpu_usage < 0.3 and memory_usage < 0.4:
            reward += 1.0
        elif cpu_usage > 0.8 or memory_usage > 0.8:
            reward -= 2.0
        
        return round(reward, 2)
    
    def update_rl_table(self, state, action, reward, next_state, valid_next_actions):
        current_q = self.q_table.get((state, action), 0.0)
        
        max_next_q = max([self.q_table.get((next_state, a), 0.0) for a in valid_next_actions], default=0.0)
        
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action)] = new_q
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                state.split('_')[0] if isinstance(state, str) else 'unknown',
                state.split('_')[1] if isinstance(state, str) and len(state.split('_')) > 1 else 'unknown',
                str(state),
                action,
                f"{reward:.2f}",
                f"{new_q:.4f}"
            ])
        
        return new_q
    
    def save_policy(self, output_path="rl/policy_runtime.json"):
        policy_data = {
            "q_table": {f"{k[0]}_{k[1]}": v for k, v in self.q_table.items()},
            "metadata": {
                "alpha": self.alpha,
                "gamma": self.gamma,
                "epsilon": self.epsilon,
                "last_updated": datetime.now().isoformat()
            }
        }
        with open(output_path, 'w') as f:
            json.dump(policy_data, f, indent=2)
    
    def load_policy(self, input_path="rl/policy_runtime.json"):
        if os.path.exists(input_path):
            with open(input_path, 'r') as f:
                data = json.load(f)
                self.q_table = {tuple(k.split('_', 1)): v for k, v in data.get('q_table', {}).items()}
