"""
Orchestrator API Wrapper - Calls Shivam's orchestrator functions
"""
import json
import os

class OrchestratorAPI:
    """Wrapper for Shivam's orchestrator APIs"""
    
    def __init__(self):
        # Import Shivam's real orchestrator
        try:
            from shivam_real_orchestrator import deploy, stop, scale, get_status, get_metrics
            self.deploy_func = deploy
            self.stop_func = stop
            self.scale_func = scale
            self.status_func = get_status
            self.metrics_func = get_metrics
            self.real_orchestrator = True
            print("[INFO] Using Shivam's real orchestrator")
        except ImportError:
            # Fallback to simulated orchestrator
            try:
                from shivam_orchestrator import deploy, stop, scale, get_status, get_metrics
                self.deploy_func = deploy
                self.stop_func = stop
                self.scale_func = scale
                self.status_func = get_status
                self.metrics_func = get_metrics
                self.real_orchestrator = True
                print("[INFO] Using Shivam's simulated orchestrator")
            except ImportError:
                self.real_orchestrator = False
                print("[WARN] No orchestrator found, using mock")
        
        self.max_workers = 3
    
    def deploy_app(self, app_name, env):
        """Deploy application using Shivam's orchestrator"""
        if self.real_orchestrator:
            return self.deploy_func(app_name, env)
        else:
            return {
                'status': 'success',
                'message': 'App deployed successfully (mock)'
            }
    
    def stop_app(self, app_name, env):
        """Stop application using Shivam's orchestrator"""
        if self.real_orchestrator:
            return self.stop_func(app_name, env)
        else:
            return {
                'status': 'success',
                'message': 'App stopped successfully (mock)'
            }
    
    def scale(self, app_name, env, direction="up", workers=None):
        """Scale application using Shivam's orchestrator"""
        if direction == "up" and workers is None:
            workers = 2
        elif direction == "down" and workers is None:
            workers = 1
        
        workers = min(workers, self.max_workers)
        workers = max(workers, 1)
        
        if self.real_orchestrator:
            return self.scale_func(app_name, env, workers)
        else:
            return {
                'status': 'success',
                'message': f'App scaled {direction} to {workers} workers (mock)'
            }
    
    def get_status(self, app_name, env):
        """Get current app status from Shivam's orchestrator"""
        if self.real_orchestrator:
            return self.status_func(app_name, env)
        else:
            return {
                'status': 'healthy',
                'app_name': app_name,
                'env': env,
                'workers': 1
            }
    
    def get_metrics(self, app_name, env):
        """Get app metrics from Shivam's orchestrator"""
        if self.real_orchestrator:
            return self.metrics_func(app_name, env)
        else:
            return {
                'status': 'healthy',
                'error_rate': 0.0,
                'response_time': 100
            }
