"""
Advanced Reward Functions - Latency gradients, partial degradation, long-term penalties
"""
import numpy as np

class AdvancedRewardCalculator:
    def __init__(self):
        self.latency_history = {}
        self.degradation_penalties = {}
    
    def calculate_reward(self, prev_state, action, new_state, app_name):
        """Calculate comprehensive reward reflecting true app health"""
        # Multi-dimensional reward calculation
        stability_reward = self._stability_reward(prev_state, new_state)
        performance_reward = self._performance_reward(prev_state, new_state)
        efficiency_reward = self._efficiency_reward(new_state, action)
        reliability_reward = self._reliability_reward(new_state, app_name)
        
        # Weighted combination
        total_reward = (
            stability_reward * 0.3 +
            performance_reward * 0.25 +
            efficiency_reward * 0.25 +
            reliability_reward * 0.2
        )
        
        return max(-10, min(10, total_reward))
    
    def _stability_reward(self, prev_state, new_state):
        """Reward for maintaining/improving stability"""
        prev_status = prev_state.get('status', 'unknown')
        new_status = new_state.get('status', 'unknown')
        
        status_values = {'failed': 0, 'degraded': 1, 'healthy': 2}
        prev_val = status_values.get(prev_status, 0)
        new_val = status_values.get(new_status, 0)
        
        improvement = new_val - prev_val
        if improvement > 0:
            return improvement * 3.0  # Reward improvement
        elif improvement < 0:
            return improvement * 2.0  # Penalize degradation
        else:
            return 1.0 if new_status == 'healthy' else 0.0  # Maintain healthy
    
    def _performance_reward(self, prev_state, new_state):
        """Reward for performance improvements"""
        prev_latency = prev_state.get('avg_latency', 100)
        new_latency = new_state.get('avg_latency', 100)
        prev_error = prev_state.get('error_rate', 0)
        new_error = new_state.get('error_rate', 0)
        
        # Latency improvement reward
        latency_improvement = (prev_latency - new_latency) / prev_latency
        latency_reward = latency_improvement * 4.0
        
        # Error rate improvement reward
        error_improvement = prev_error - new_error
        error_reward = error_improvement * 10.0
        
        return latency_reward + error_reward
    
    def _efficiency_reward(self, new_state, action):
        """Reward for resource efficiency"""
        cpu = new_state.get('cpu_usage', 0)
        memory = new_state.get('memory_usage', 0)
        
        # Optimal resource usage (60-80% CPU, 50-70% memory)
        cpu_efficiency = 1.0 - abs(cpu - 0.7) if 0.6 <= cpu <= 0.8 else -abs(cpu - 0.7)
        memory_efficiency = 1.0 - abs(memory - 0.6) if 0.5 <= memory <= 0.7 else -abs(memory - 0.6)
        
        # Penalize resource-intensive actions if resources are already high
        action_penalty = 0
        if action in ['scale_up', 'deploy'] and (cpu > 0.8 or memory > 0.8):
            action_penalty = -2.0
        
        return (cpu_efficiency + memory_efficiency) * 2.0 + action_penalty
    
    def _reliability_reward(self, new_state, app_name):
        """Reward for system reliability"""
        uptime = new_state.get('uptime', 0)
        workers = new_state.get('workers', 1)
        
        # Uptime reward (logarithmic)
        uptime_reward = min(2.0, uptime / 3600)  # Max 2 points for 1+ hour uptime
        
        # Worker stability (penalize too few or too many)
        worker_stability = 1.0 if 1 <= workers <= 3 else -abs(workers - 2) * 0.5
        
        return uptime_reward + worker_stability
    
    def _latency_gradient_penalty(self, prev_state, new_state, app_name):
        """Penalize latency increases with gradient-based calculation"""
        prev_latency = prev_state.get('avg_latency', 100)
        new_latency = new_state.get('avg_latency', 100)
        
        # Store latency history for trend analysis
        if app_name not in self.latency_history:
            self.latency_history[app_name] = []
        self.latency_history[app_name].append(new_latency)
        
        # Keep only last 10 measurements
        if len(self.latency_history[app_name]) > 10:
            self.latency_history[app_name] = self.latency_history[app_name][-10:]
        
        # Calculate gradient penalty
        latency_increase = new_latency - prev_latency
        if latency_increase > 0:
            # Exponential penalty for latency increases
            return min(3.0, (latency_increase / 50) ** 1.5)
        return 0.0
    
    def _partial_degradation_penalty(self, new_state):
        """Penalize partial service degradation"""
        error_rate = new_state.get('error_rate', 0)
        cpu_usage = new_state.get('cpu_usage', 0)
        memory_usage = new_state.get('memory_usage', 0)
        
        penalty = 0.0
        
        # Error rate penalty (gradual)
        if error_rate > 0.01:  # > 1%
            penalty += min(2.0, error_rate * 100)
        
        # Resource usage penalty (gradual)
        if cpu_usage > 0.8:  # > 80%
            penalty += (cpu_usage - 0.8) * 5
        if memory_usage > 0.9:  # > 90%
            penalty += (memory_usage - 0.9) * 10
        
        return penalty
    
    def _long_term_penalty(self, action, app_name):
        """Apply long-term penalties for frequent disruptive actions"""
        if app_name not in self.degradation_penalties:
            self.degradation_penalties[app_name] = {'restart_count': 0, 'stop_count': 0}
        
        # Increment counters
        if action == 'restart':
            self.degradation_penalties[app_name]['restart_count'] += 1
        elif action == 'stop':
            self.degradation_penalties[app_name]['stop_count'] += 1
        
        # Calculate long-term penalty
        restart_penalty = min(2.0, self.degradation_penalties[app_name]['restart_count'] * 0.1)
        stop_penalty = min(3.0, self.degradation_penalties[app_name]['stop_count'] * 0.2)
        
        return restart_penalty + stop_penalty

# Global instance
advanced_reward_calculator = AdvancedRewardCalculator()