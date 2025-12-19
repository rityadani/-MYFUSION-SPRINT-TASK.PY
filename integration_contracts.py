"""
Integration Contracts - Schema validation for external API interfaces
"""
import json
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ContractValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]

class IntegrationContracts:
    """Contract validation for external integrations"""
    
    def __init__(self):
        self.schemas = self._load_integration_schemas()
    
    def _load_integration_schemas(self):
        """Load API contract schemas"""
        return {
            'orchestrator': {
                'deploy_app': {
                    'required_params': ['app_name', 'env', 'build_path'],
                    'optional_params': ['workers', 'config'],
                    'return_schema': {'status': str, 'deployment_id': str}
                },
                'stop_app': {
                    'required_params': ['app_name', 'env'],
                    'return_schema': {'status': str, 'stopped_at': str}
                },
                'scale': {
                    'required_params': ['app_name', 'env', 'workers'],
                    'return_schema': {'status': str, 'current_workers': int}
                }
            },
            'build_registry': {
                'get_latest_build': {
                    'required_params': ['app_name', 'branch'],
                    'return_schema': {'build_path': str, 'build_id': str, 'timestamp': str}
                },
                'get_build_status': {
                    'required_params': ['build_id'],
                    'return_schema': {'status': str, 'artifacts': list}
                }
            },
            'qa_logs': {
                'inject_failure': {
                    'required_params': ['app_name', 'failure_type', 'duration'],
                    'return_schema': {'injection_id': str, 'status': str}
                }
            }
        }
    
    def validate_orchestrator_call(self, method: str, params: Dict[str, Any]) -> ContractValidationResult:
        """Validate orchestrator API call against contract"""
        return self._validate_contract('orchestrator', method, params)
    
    def validate_build_registry_call(self, method: str, params: Dict[str, Any]) -> ContractValidationResult:
        """Validate build registry API call against contract"""
        return self._validate_contract('build_registry', method, params)
    
    def validate_qa_logs_call(self, method: str, params: Dict[str, Any]) -> ContractValidationResult:
        """Validate QA logs API call against contract"""
        return self._validate_contract('qa_logs', method, params)
    
    def _validate_contract(self, service: str, method: str, params: Dict[str, Any]) -> ContractValidationResult:
        """Generic contract validation"""
        errors = []
        warnings = []
        
        if service not in self.schemas:
            errors.append(f"Unknown service: {service}")
            return ContractValidationResult(False, errors, warnings)
        
        if method not in self.schemas[service]:
            errors.append(f"Unknown method: {service}.{method}")
            return ContractValidationResult(False, errors, warnings)
        
        schema = self.schemas[service][method]
        
        # Check required parameters
        for required_param in schema['required_params']:
            if required_param not in params:
                errors.append(f"Missing required parameter: {required_param}")
        
        # Check parameter types (basic validation)
        for param, value in params.items():
            if param not in schema['required_params'] + schema.get('optional_params', []):
                warnings.append(f"Unexpected parameter: {param}")
        
        return ContractValidationResult(len(errors) == 0, errors, warnings)
    
    def validate_response_schema(self, service: str, method: str, response: Dict[str, Any]) -> ContractValidationResult:
        """Validate API response against expected schema"""
        errors = []
        warnings = []
        
        if service not in self.schemas or method not in self.schemas[service]:
            errors.append(f"Cannot validate response for unknown {service}.{method}")
            return ContractValidationResult(False, errors, warnings)
        
        expected_schema = self.schemas[service][method]['return_schema']
        
        for field, expected_type in expected_schema.items():
            if field not in response:
                errors.append(f"Missing response field: {field}")
            elif not isinstance(response[field], expected_type):
                errors.append(f"Wrong type for {field}: expected {expected_type.__name__}, got {type(response[field]).__name__}")
        
        return ContractValidationResult(len(errors) == 0, errors, warnings)

# Contract validation stubs for integration testing
class MockOrchestratorAPI:
    """Mock orchestrator with contract validation"""
    
    def __init__(self):
        self.contracts = IntegrationContracts()
    
    def deploy_app(self, app_name: str, env: str, build_path: str, **kwargs):
        # Validate contract
        params = {'app_name': app_name, 'env': env, 'build_path': build_path, **kwargs}
        validation = self.contracts.validate_orchestrator_call('deploy_app', params)
        
        if not validation.valid:
            raise ValueError(f"Contract violation: {validation.errors}")
        
        # Mock response
        return {'status': 'deployed', 'deployment_id': f'dep_{app_name}_{env}'}
    
    def stop_app(self, app_name: str, env: str):
        params = {'app_name': app_name, 'env': env}
        validation = self.contracts.validate_orchestrator_call('stop_app', params)
        
        if not validation.valid:
            raise ValueError(f"Contract violation: {validation.errors}")
        
        return {'status': 'stopped', 'stopped_at': '2024-01-01T12:00:00Z'}
    
    def scale(self, app_name: str, env: str, workers: int):
        params = {'app_name': app_name, 'env': env, 'workers': workers}
        validation = self.contracts.validate_orchestrator_call('scale', params)
        
        if not validation.valid:
            raise ValueError(f"Contract violation: {validation.errors}")
        
        return {'status': 'scaled', 'current_workers': workers}

class MockBuildRegistryAPI:
    """Mock build registry with contract validation"""
    
    def __init__(self):
        self.contracts = IntegrationContracts()
    
    def get_latest_build(self, app_name: str, branch: str = 'main'):
        params = {'app_name': app_name, 'branch': branch}
        validation = self.contracts.validate_build_registry_call('get_latest_build', params)
        
        if not validation.valid:
            raise ValueError(f"Contract violation: {validation.errors}")
        
        return {
            'build_path': f'/builds/{app_name}/latest.tar.gz',
            'build_id': f'build_{app_name}_123',
            'timestamp': '2024-01-01T12:00:00Z'
        }

# Global contract validator
integration_contracts = IntegrationContracts()

def validate_integration_call(service: str, method: str, params: Dict[str, Any]) -> ContractValidationResult:
    """Validate any integration call"""
    if service == 'orchestrator':
        return integration_contracts.validate_orchestrator_call(method, params)
    elif service == 'build_registry':
        return integration_contracts.validate_build_registry_call(method, params)
    elif service == 'qa_logs':
        return integration_contracts.validate_qa_logs_call(method, params)
    else:
        return ContractValidationResult(False, [f"Unknown service: {service}"], [])