"""
Fix Static States - Integration patch for dynamic state detection
"""
from rl.dynamic_state_detector import get_dynamic_state
from rl.advanced_rewards import advanced_reward_calculator

def patch_app_state_mapper():
    """Patch existing app_state_mapper to use dynamic detection"""
    import rl.app_state_mapper as mapper
    
    # Replace static extraction with dynamic
    original_extract = mapper.extract_state if hasattr(mapper, 'extract_state') else None
    
    def dynamic_extract_state(app_name, env):
        """Dynamic state extraction replacing static fallbacks"""
        return get_dynamic_state(app_name, env)
    
    # Monkey patch
    mapper.extract_state = dynamic_extract_state
    return "✅ State mapper patched for dynamic detection"

def patch_universal_controller():
    """Patch RL controller to use advanced rewards"""
    try:
        import rl.universal_controller as controller
        
        # Replace reward calculation
        if hasattr(controller, 'UniversalRLController'):
            original_calc = controller.UniversalRLController.calculate_reward
            
            def advanced_calculate_reward(self, prev_state, action, new_state, app_name):
                return advanced_reward_calculator.calculate_reward(prev_state, action, new_state, app_name)
            
            controller.UniversalRLController.calculate_reward = advanced_calculate_reward
            return "✅ RL controller patched for advanced rewards"
    except ImportError:
        return "⚠️ Universal controller not found - manual integration needed"

def validate_fixes():
    """Validate that fixes work correctly"""
    # Test dynamic state detection
    test_state = get_dynamic_state("sample_backend", "stage")
    
    if test_state.get('status') != 'unknown' or test_state.get('error_rate') != 0.0:
        print("✅ Dynamic state detection working")
    else:
        print("❌ Still getting static fallback values")
    
    # Test advanced rewards
    prev_state = {'status': 'degraded', 'avg_latency': 200, 'error_rate': 0.05}
    new_state = {'status': 'healthy', 'avg_latency': 150, 'error_rate': 0.01}
    
    reward = advanced_reward_calculator.calculate_reward(prev_state, 'restart', new_state, 'test_app')
    
    if reward > 0:
        print(f"✅ Advanced rewards working: {reward:.2f}")
    else:
        print(f"❌ Reward calculation issue: {reward:.2f}")

if __name__ == "__main__":
    print("🔧 Applying fixes for static states and limited rewards...")
    
    # Apply patches
    result1 = patch_app_state_mapper()
    result2 = patch_universal_controller()
    
    print(result1)
    print(result2)
    
    # Validate fixes
    print("\n🧪 Validating fixes...")
    validate_fixes()
    
    print("\n✅ Fixes applied - RL should now use dynamic states and advanced rewards")