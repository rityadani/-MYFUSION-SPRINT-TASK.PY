"""
Universal RL Cycle Runner - Single cycle test
Usage: python run_universal_rl_cycle.py --app sample_backend --env stage
"""
import argparse
import json
import time
from rl.universal_controller import UniversalRLController
from rl.orchestrator_wrapper import OrchestratorAPI
from rl.app_action_space import get_valid_actions, is_action_safe, get_fallback_action

def run_rl_cycle(app_name, env, cycles=5):
    """Run RL decision cycle for an app"""
    print(f"\n=== Starting RL Cycle for {app_name} in {env} ===\n")
    
    # Initialize
    controller = UniversalRLController()
    orchestrator = OrchestratorAPI()
    
    # Load app spec
    try:
        app_spec = controller.load_app_spec(app_name)
        print(f"[OK] Loaded app spec: {app_name}")
    except FileNotFoundError:
        print(f"[WARN] App spec not found. Creating default spec...")
        create_default_spec(app_name)
        app_spec = controller.load_app_spec(app_name)
    
    # Load existing policy if available
    controller.load_policy()
    
    total_reward = 0.0
    
    for cycle in range(cycles):
        print(f"\n--- Cycle {cycle + 1}/{cycles} ---")
        
        # 1. Get current state
        state = controller.get_state(app_name, env)
        print(f"State: {state}")
        
        # 2. Choose action
        action = controller.choose_action(state, app_spec)
        print(f"Action chosen: {action}")
        
        # 3. Safety check
        valid_actions = get_valid_actions(app_spec)
        if action not in valid_actions:
            print(f"[WARN] Invalid action, using fallback")
            action = get_fallback_action(action)
        
        # 4. Execute action
        print(f"Executing: {action}...")
        result = controller.execute_action(action, app_name, env, orchestrator)
        print(f"Result: {result.get('message', 'Done')}")
        
        # Wait for state to stabilize
        time.sleep(1)
        
        # 5. Get new state
        next_state = controller.get_state(app_name, env)
        print(f"Next state: {next_state}")
        
        # 6. Compute reward
        # Convert state keys back to dicts for reward computation
        pre_state_dict = {'status': 'unknown', 'error_rate': 0.0}
        post_state_dict = {'status': 'healthy', 'error_rate': 0.0}
        
        if 'failed' in next_state:
            post_state_dict['status'] = 'failed'
        elif 'healthy' in next_state:
            post_state_dict['status'] = 'healthy'
        
        reward = controller.compute_reward(pre_state_dict, post_state_dict)
        print(f"Reward: {reward:.2f}")
        total_reward += reward
        
        # 7. Update Q-table
        next_valid_actions = get_valid_actions(app_spec)
        q_value = controller.update_rl_table(state, action, reward, next_state, next_valid_actions)
        print(f"Q-value updated: {q_value:.4f}")
    
    # Save policy
    controller.save_policy()
    print(f"\n[OK] Policy saved")
    print(f"[OK] Total reward: {total_reward:.2f}")
    print(f"[OK] Logs saved to: {controller.log_file}")
    
    return {
        'app_name': app_name,
        'env': env,
        'cycles': cycles,
        'total_reward': total_reward,
        'final_q_table_size': len(controller.q_table)
    }

def create_default_spec(app_name):
    """Create a default app spec for testing"""
    import os
    os.makedirs('app_specs', exist_ok=True)
    
    spec = {
        'name': app_name,
        'type': 'backend',
        'scaling': {
            'enabled': True,
            'min_workers': 1,
            'max_workers': 3
        },
        'health_check': {
            'enabled': True,
            'endpoint': '/health'
        },
        'custom_actions': []
    }
    
    with open(f'app_specs/{app_name}.json', 'w') as f:
        json.dump(spec, f, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Universal RL Cycle')
    parser.add_argument('--app', required=True, help='App name')
    parser.add_argument('--env', required=True, help='Environment (dev/stage/prod)')
    parser.add_argument('--cycles', type=int, default=5, help='Number of cycles')
    
    args = parser.parse_args()
    
    result = run_rl_cycle(args.app, args.env, args.cycles)
    print(f"\n=== Cycle Complete ===")
    print(json.dumps(result, indent=2))
