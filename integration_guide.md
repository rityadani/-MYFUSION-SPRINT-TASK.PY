# Integration Guide - Team Connections

## Shivam (Orchestrator) Integration

**File to update:** `rl/orchestrator_wrapper.py`

```python
# Replace line 9 with:
from shivam_orchestrator import deploy, stop, scale, get_status

# Update methods to call real functions:
def deploy_app(self, app_name, env):
    return deploy(app_name, env)

def stop_app(self, app_name, env):
    return stop(app_name, env)

def scale(self, app_name, env, direction="up", workers=None):
    return scale(app_name, env, workers)
```

---

## Nilesh (Build Registry) Integration

**File to update:** `rl/app_state_mapper.py`

```python
# Add at top:
from nilesh_build_registry import get_build_logs, get_app_metrics

# Update extract_state function:
def extract_state(app_name, env):
    # Get real logs from Nilesh
    logs = get_build_logs(app_name, env)
    metrics = get_app_metrics(app_name, env)
    
    state = {
        'app_name': app_name,
        'env': env,
        'status': metrics.get('status', 'unknown'),
        'error_rate': metrics.get('error_rate', 0.0),
        'response_time': metrics.get('response_time', 0),
    }
    return f"{app_name}_{env}_{state['status']}_err{int(state['error_rate']*100)}"
```

---

## Vinayak (QA) Integration

**File to update:** `rl/app_state_mapper.py`

```python
# Add at top:
from vinayak_qa_logs import get_failure_logs, get_test_results

# Add new function:
def get_failure_metrics(app_name, env):
    failures = get_failure_logs(app_name, env)
    test_results = get_test_results(app_name, env)
    
    return {
        'failure_count': len(failures),
        'test_pass_rate': test_results.get('pass_rate', 1.0),
        'critical_errors': test_results.get('critical_errors', 0)
    }
```

---

## Quick Integration Steps

1. **Get modules from team:**
   - `shivam_orchestrator.py` from Shivam
   - `nilesh_build_registry.py` from Nilesh  
   - `vinayak_qa_logs.py` from Vinayak

2. **Place in project root**

3. **Update imports in:**
   - `rl/orchestrator_wrapper.py`
   - `rl/app_state_mapper.py`

4. **Test integration:**
   ```bash
   python run_universal_rl_cycle.py --app sample_backend --env stage
   ```
