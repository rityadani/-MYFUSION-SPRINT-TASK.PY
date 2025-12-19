"""
Safety Constraints - Structural enforcement for RL actions
"""
import json
from datetime import datetime

class SafetyConstraints:
    """Structural safety enforcement for RL actions"""
    
    def __init__(self, schema_path="safety_schema.json"):
        # Load schema-enforced constraints
        self.schema = self._load_safety_schema(schema_path)
        self.constraints = self.schema['constraints']
        self.action_history = []
        self.policy_violations = []
    
    def _load_safety_schema(self, schema_path):
        """Load safety schema with structural enforcement"""
        default_schema = {
            "version": "1.0",
            "constraints": {
                "max_workers_global": 10,
                "max_workers_per_app": 3,
                "min_uptime_before_action": 30,
                "max_actions_per_minute": 5,
                "forbidden_prod_actions": ["stop"],
                "required_approval_actions": ["scale_up"]
            },
            "enforcement_level": "STRICT"
        }
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default_schema
    
    def enforce_constraints(self, action, app_name, env, app_spec, current_state):
        """Structurally enforce safety constraints with schema validation"""
        violations = []
        
        # Schema-level validation first
        schema_violations = self._validate_against_schema(action, app_name, env, app_spec)
        violations.extend(schema_violations)
        
        # If schema violations exist and enforcement is STRICT, block immediately
        if schema_violations and self.schema.get('enforcement_level') == 'STRICT':
            self._log_policy_violation(action, app_name, env, schema_violations)
            return violations
        
        # Check worker limits
        if action in ['scale_up', 'deploy']:
            current_workers = current_state.get('workers', 1)
            max_allowed = min(
                self.constraints['max_workers_per_app'],
                app_spec.get('scaling', {}).get('max_workers', 3)
            )
            if current_workers >= max_allowed:
                violations.append(f"Worker limit exceeded: {current_workers} >= {max_allowed}")
        
        # Check production environment restrictions
        if env == 'prod' and action in self.constraints['forbidden_prod_actions']:
            violations.append(f"Action '{action}' forbidden in production environment")
        
        # Check minimum uptime
        uptime = current_state.get('uptime', 0)
        if uptime < self.constraints['min_uptime_before_action'] and action != 'deploy':
            violations.append(f"Minimum uptime not met: {uptime}s < {self.constraints['min_uptime_before_action']}s")
        
        # Check action frequency
        recent_actions = self._get_recent_actions(app_name, env, 60)  # Last minute
        if len(recent_actions) >= self.constraints['max_actions_per_minute']:
            violations.append(f"Action frequency limit exceeded: {len(recent_actions)} actions in last minute")
        
        # Log action attempt
        self._log_action_attempt(action, app_name, env, violations)
        
        return violations
    
    def _get_recent_actions(self, app_name, env, seconds):
        """Get recent actions for rate limiting"""
        cutoff = datetime.now().timestamp() - seconds
        return [
            a for a in self.action_history 
            if a['app_name'] == app_name and a['env'] == env and a['timestamp'] > cutoff
        ]
    
    def _log_action_attempt(self, action, app_name, env, violations):
        """Log action attempt for audit trail"""
        self.action_history.append({
            'action': action,
            'app_name': app_name,
            'env': env,
            'timestamp': datetime.now().timestamp(),
            'violations': violations,
            'allowed': len(violations) == 0
        })
        
        # Keep only last 1000 actions
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-1000:]
    
    def get_safe_fallback_action(self, original_action, app_name, env, current_state):
        """Get safe fallback when original action violates constraints"""
        # If scaling up is blocked, try restart
        if original_action == 'scale_up':
            return 'restart'
        
        # If stop is blocked in prod, try scale_down
        if original_action == 'stop' and env == 'prod':
            return 'scale_down'
        
        # Default safe action
        if current_state.get('status') != 'healthy':
            return 'restart'
        else:
            return 'deploy'  # No-op deploy
    
    def validate_policy_constraints(self, q_table):
        """Validate learned policy against safety constraints"""
        violations = []
        
        for (state, action), q_value in q_table.items():
            # Check if high Q-values are assigned to unsafe actions
            if q_value > 5.0:  # High Q-value threshold
                if 'prod' in state and action == 'stop':
                    violations.append(f"High Q-value for unsafe action: {state} -> {action}")
        
        return violations
    
    def _validate_against_schema(self, action, app_name, env, app_spec):
        """Schema-level validation of actions"""
        violations = []
        
        # Validate action exists in app spec
        valid_actions = app_spec.get('actions', [])
        if action not in valid_actions:
            violations.append(f"Action '{action}' not in app spec valid actions: {valid_actions}")
        
        # Validate environment constraints
        env_constraints = app_spec.get('environment_constraints', {})
        if env in env_constraints:
            forbidden = env_constraints[env].get('forbidden_actions', [])
            if action in forbidden:
                violations.append(f"Action '{action}' forbidden in environment '{env}' by app spec")
        
        return violations
    
    def _log_policy_violation(self, action, app_name, env, violations):
        """Log policy-level violations for audit"""
        self.policy_violations.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'app_name': app_name,
            'env': env,
            'violations': violations,
            'enforcement_level': self.schema.get('enforcement_level')
        })

# Global safety enforcer
safety_enforcer = SafetyConstraints()

def enforce_safety(action, app_name, env, app_spec, current_state):
    """Enforce safety with structural validation"""
    violations = safety_enforcer.enforce_constraints(action, app_name, env, app_spec, current_state)
    if violations:
        raise SafetyViolationError(f"Action blocked: {violations}")
    return True

def get_safe_fallback(action, app_name, env, current_state):
    return safety_enforcer.get_safe_fallback_action(action, app_name, env, current_state)

class SafetyViolationError(Exception):
    """Raised when safety constraints are violated"""
    pass