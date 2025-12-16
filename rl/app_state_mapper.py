"""
App State Mapper - Converts logs/metrics to RL states
"""
import json
import os
from datetime import datetime

def extract_state(app_name, env):
    """Extract current state from Nilesh's build registry + Shivam's orchestrator"""
    try:
        # Get real metrics from Nilesh's build registry
        from nilesh_build_registry import get_app_metrics
        metrics = get_app_metrics(app_name, env)
        
        state = {
            'app_name': app_name,
            'env': env,
            'status': metrics.get('status', 'unknown'),
            'error_rate': metrics.get('error_rate', 0.0),
            'response_time': metrics.get('response_time', 0),
            'cpu_usage': metrics.get('cpu_usage', 0.0),
            'memory_usage': metrics.get('memory_usage', 0.0),
            'timestamp': metrics.get('timestamp', datetime.now().isoformat())
        }
    except ImportError:
        # Fallback to Shivam's orchestrator
        try:
            from shivam_orchestrator import get_metrics
            metrics = get_metrics(app_name, env)
            state = {
                'app_name': app_name,
                'env': env,
                'status': metrics.get('status', 'unknown'),
                'error_rate': metrics.get('error_rate', 0.0),
                'response_time': metrics.get('response_time', 0),
                'cpu_usage': metrics.get('cpu_usage', 0.0),
                'memory_usage': metrics.get('memory_usage', 0.0),
                'timestamp': metrics.get('timestamp', datetime.now().isoformat())
            }
        except ImportError:
            # Final fallback
            state = {
                'app_name': app_name,
                'env': env,
                'status': 'healthy',
                'error_rate': 0.0,
                'response_time': 100,
                'cpu_usage': 0.5,
                'memory_usage': 0.4,
                'timestamp': datetime.now().isoformat()
            }
    
    # Discretize state for Q-table
    state_key = f"{app_name}_{env}_{state['status']}_err{int(state['error_rate']*100)}"
    return state_key

def parse_log_to_metrics(log_file):
    """Parse raw logs to extract metrics"""
    metrics = {
        'error_rate': 0.0,
        'response_time': 0,
        'status': 'healthy'
    }
    
    if not os.path.exists(log_file):
        return metrics
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
        error_count = sum(1 for line in lines if 'ERROR' in line or 'FAIL' in line)
        total_lines = len(lines)
        
        if total_lines > 0:
            metrics['error_rate'] = error_count / total_lines
        
        if error_count > total_lines * 0.5:
            metrics['status'] = 'failed'
        elif error_count > 0:
            metrics['status'] = 'degraded'
    
    return metrics
