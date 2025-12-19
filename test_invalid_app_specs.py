"""
Negative Tests for Invalid App Specs - Universality validation
"""
import json
import pytest
from rl.universal_controller import UniversalRLController
from rl.safety_constraints import SafetyViolationError

class TestInvalidAppSpecs:
    def setup_method(self):
        self.rl_controller = UniversalRLController()
    
    def test_malformed_json_spec(self):
        """Test rejection of malformed JSON app spec"""
        malformed_spec = '{"app_name": "test", "actions": ['  # Invalid JSON
        
        with pytest.raises(json.JSONDecodeError):
            self.rl_controller.load_app_spec_from_string(malformed_spec)
    
    def test_missing_required_fields(self):
        """Test rejection of app spec missing required fields"""
        invalid_specs = [
            {},  # Empty spec
            {"app_name": "test"},  # Missing actions
            {"actions": ["deploy"]},  # Missing app_name
            {"app_name": "test", "actions": []},  # Empty actions
        ]
        
        for spec in invalid_specs:
            with pytest.raises(ValueError, match="Invalid app spec"):
                self.rl_controller.validate_app_spec(spec)
    
    def test_invalid_action_types(self):
        """Test rejection of invalid action types"""
        spec = {
            "app_name": "test",
            "actions": ["deploy", "invalid_action", "stop"],
            "states": ["healthy", "failed"]
        }
        
        with pytest.raises(ValueError, match="Invalid action"):
            self.rl_controller.validate_app_spec(spec)
    
    def test_conflicting_environment_constraints(self):
        """Test rejection of conflicting environment constraints"""
        spec = {
            "app_name": "test",
            "actions": ["deploy", "stop"],
            "states": ["healthy", "failed"],
            "environment_constraints": {
                "prod": {
                    "forbidden_actions": ["stop"],
                    "required_actions": ["stop"]  # Conflict!
                }
            }
        }
        
        with pytest.raises(ValueError, match="Conflicting constraints"):
            self.rl_controller.validate_app_spec(spec)
    
    def test_safety_violation_on_invalid_spec(self):
        """Test safety system blocks actions from invalid specs"""
        # Valid spec structure but invalid action
        spec = {
            "app_name": "test",
            "actions": ["deploy", "restart"],  # Missing 'stop'
            "states": ["healthy", "failed"]
        }
        
        current_state = {"status": "healthy", "workers": 1}
        
        # Should raise safety violation when trying 'stop' action not in spec
        with pytest.raises(SafetyViolationError, match="not in app spec valid actions"):
            self.rl_controller.execute_action("stop", "test", "prod", spec, current_state)
    
    def test_universality_with_minimal_spec(self):
        """Test universality works with minimal valid spec"""
        minimal_spec = {
            "app_name": "minimal_test",
            "actions": ["deploy"],
            "states": ["healthy"]
        }
        
        # Should not raise any errors
        self.rl_controller.validate_app_spec(minimal_spec)
        
        # Should be able to run RL cycle
        result = self.rl_controller.run_single_cycle(minimal_spec, "stage")
        assert result is not None
    
    def test_spec_schema_validation(self):
        """Test app spec against JSON schema"""
        invalid_specs = [
            {"app_name": 123, "actions": ["deploy"]},  # Wrong type
            {"app_name": "test", "actions": "deploy"},  # Wrong type
            {"app_name": "test", "actions": ["deploy"], "scaling": {"max_workers": "invalid"}},  # Wrong type
        ]
        
        for spec in invalid_specs:
            with pytest.raises((TypeError, ValueError)):
                self.rl_controller.validate_app_spec_schema(spec)

if __name__ == "__main__":
    # Run negative tests
    test_suite = TestInvalidAppSpecs()
    test_suite.setup_method()
    
    try:
        test_suite.test_malformed_json_spec()
        print("❌ FAIL: Should have raised JSONDecodeError")
    except json.JSONDecodeError:
        print("✅ PASS: Malformed JSON rejected")
    
    try:
        test_suite.test_missing_required_fields()
        print("❌ FAIL: Should have raised ValueError")
    except ValueError:
        print("✅ PASS: Missing required fields rejected")
    
    try:
        test_suite.test_safety_violation_on_invalid_spec()
        print("❌ FAIL: Should have raised SafetyViolationError")
    except SafetyViolationError:
        print("✅ PASS: Safety system blocks invalid spec actions")
    
    print("\n🔍 Negative test validation complete")