"""
App Action Space - Defines valid actions per app-spec
"""

def get_valid_actions(app_spec):
    """Extract valid actions from app specification"""
    actions = []
    
    # Standard actions available for all apps
    base_actions = ['deploy', 'stop', 'restart']
    actions.extend(base_actions)
    
    # Check if app supports scaling
    if app_spec.get('scaling', {}).get('enabled', False):
        actions.extend(['scale_up', 'scale_down'])
    
    # Check for custom actions in spec
    custom_actions = app_spec.get('custom_actions', [])
    actions.extend(custom_actions)
    
    return actions

def is_action_safe(action, current_state, app_spec):
    """Validate if action is safe to execute"""
    # Safety rules
    if action == 'scale_up':
        current_workers = current_state.get('workers', 1)
        max_workers = app_spec.get('scaling', {}).get('max_workers', 3)
        if current_workers >= max_workers:
            return False
    
    if action == 'scale_down':
        current_workers = current_state.get('workers', 1)
        if current_workers <= 1:
            return False
    
    if action == 'stop':
        # Don't stop production apps unless critical
        if current_state.get('env') == 'prod' and current_state.get('status') == 'healthy':
            return False
    
    return True

def get_fallback_action(invalid_action):
    """Return safe fallback action"""
    return 'restart'
