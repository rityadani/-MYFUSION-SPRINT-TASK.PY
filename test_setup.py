"""
Quick setup test - Verifies all components are working
"""
import os
import sys

def test_imports():
    """Test all imports work"""
    print("Testing imports...")
    try:
        from rl.universal_controller import UniversalRLController
        from rl.app_state_mapper import extract_state
        from rl.app_action_space import get_valid_actions
        from rl.orchestrator_wrapper import OrchestratorAPI
        print("[OK] All imports successful")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_directory_structure():
    """Test required directories exist"""
    print("\nTesting directory structure...")
    dirs = ['rl', 'logs', 'logs/rl_universal', 'reports', 'app_specs']
    all_exist = True
    for d in dirs:
        if os.path.exists(d):
            print(f"[OK] {d}/")
        else:
            print(f"[FAIL] {d}/ missing")
            all_exist = False
    return all_exist

def test_files_exist():
    """Test required files exist"""
    print("\nTesting files...")
    files = [
        'rl/universal_controller.py',
        'rl/app_state_mapper.py',
        'rl/app_action_space.py',
        'rl/orchestrator_wrapper.py',
        'run_universal_rl_cycle.py',
        'multi_app_rl_test.py',
        'universal_dashboard.py',
        'requirements.txt',
        'README.md'
    ]
    all_exist = True
    for f in files:
        if os.path.exists(f):
            print(f"[OK] {f}")
        else:
            print(f"[FAIL] {f} missing")
            all_exist = False
    return all_exist

def test_controller_basic():
    """Test basic controller functionality"""
    print("\nTesting RL Controller...")
    try:
        from rl.universal_controller import UniversalRLController
        controller = UniversalRLController()
        
        # Test reward computation
        pre = {'status': 'failed', 'error_rate': 0.8}
        post = {'status': 'healthy', 'error_rate': 0.1}
        reward = controller.compute_reward(pre, post)
        print(f"[OK] Reward computation works: {reward}")
        
        # Test Q-table update
        state = "test_state"
        action = "restart"
        controller.update_rl_table(state, action, reward, state, [action])
        print(f"[OK] Q-table update works")
        
        # Test policy save
        controller.save_policy()
        print(f"[OK] Policy save works")
        
        return True
    except Exception as e:
        print(f"[FAIL] Controller test failed: {e}")
        return False

def main():
    print("="*60)
    print("UNIVERSAL RL SETUP TEST")
    print("="*60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Directory Structure", test_directory_structure()))
    results.append(("Files", test_files_exist()))
    results.append(("Controller", test_controller_basic()))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n*** ALL TESTS PASSED - Setup Complete! ***")
        print("\nNext steps:")
        print("1. Run: python run_universal_rl_cycle.py --app sample_backend --env stage")
        print("2. Run: python multi_app_rl_test.py")
        print("3. Run: streamlit run universal_dashboard.py")
    else:
        print("\n*** Some tests failed - check errors above ***")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
