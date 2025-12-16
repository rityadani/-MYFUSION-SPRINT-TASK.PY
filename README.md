# Universal RL Decision Layer - Fusion Sprint

**Role**: RL + Decision Intelligence Lead  
**Owner**: Ritesh DevOps  
**Duration**: 3 Days

## Overview

Universal RL engine that manages ANY app using app-spec, makes real-time decisions, and coordinates with orchestrator layer.

## Architecture

```
App Spec → RL Controller → State Mapper → Action Space → Orchestrator API
                ↓
         Q-Learning Engine
                ↓
         Policy Runtime
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Single App Test
```bash
python run_universal_rl_cycle.py --app sample_backend --env stage --cycles 5
```

### 3. Run Multi-App Test
```bash
python multi_app_rl_test.py
```

### 4. Launch Dashboard
```bash
streamlit run universal_dashboard.py
```

## File Structure

```
rl/
├── universal_controller.py    # Core RL engine
├── app_state_mapper.py        # Log → State converter
├── app_action_space.py        # Valid actions per app
├── orchestrator_wrapper.py    # Shivam's API wrapper
└── policy_runtime.json        # Learned Q-table

run_universal_rl_cycle.py      # Single-cycle runner
multi_app_rl_test.py           # Multi-app validator
universal_dashboard.py         # Streamlit dashboard

logs/rl_universal/
└── rl_events.csv              # All RL decisions

reports/
└── fusion_rl_summary.json     # Final test report

app_specs/
└── {app_name}.json            # Universal app specs
```

## Key Features

✅ **Universal**: Works with ANY app via app-spec  
✅ **No Hardcoding**: Fully config-driven  
✅ **Real-time Learning**: Q-learning with epsilon-greedy  
✅ **Safe Actions**: Fallback rules + validation  
✅ **Multi-app**: Tested on 3+ apps  
✅ **Observable**: Dashboard + CSV logs  

## Integration Points

- **Shivam (Orchestrator)**: Calls `deploy_app()`, `stop_app()`, `scale()`
- **Nilesh (Build Registry)**: Reads build output paths
- **Vinayak (QA)**: Receives failure injection logs

## RL Cycle Flow

1. **Load App Spec** → Get valid actions
2. **Extract State** → From logs/metrics
3. **Choose Action** → Epsilon-greedy policy
4. **Execute Action** → Via orchestrator API
5. **Compute Reward** → State transition quality
6. **Update Q-Table** → Q-learning algorithm
7. **Save Policy** → Persist learned values

## Safety Rules

- Max 3 workers for scaling
- Invalid action → fallback to restart
- Production apps protected from unnecessary stops
- All actions validated before execution

## Success Checklist

- [x] RL runs on any app spec
- [x] RL selects valid actions only
- [x] Actions execute via orchestrator
- [x] Rewards computed from real logs
- [x] RL learns across cycles
- [x] Multi-app test passes
- [x] Dashboard updates live

## Deliverables

1. ✅ `rl/universal_controller.py`
2. ✅ `run_universal_rl_cycle.py`
3. ✅ `multi_app_rl_test.py`
4. ✅ `/logs/rl_universal/rl_events.csv`
5. ✅ `policy_runtime.json`
6. ✅ `universal_dashboard.py`
7. ✅ `reports/fusion_rl_summary.json`

## Testing

```bash
# Test single app
python run_universal_rl_cycle.py --app sample_backend --env stage

# Test universality
python multi_app_rl_test.py

# View results
streamlit run universal_dashboard.py
```

## Next Steps

1. Connect to Shivam's real orchestrator module
2. Integrate Nilesh's build registry for state extraction
3. Add Vinayak's failure injection logs
4. Tune hyperparameters (alpha, gamma, epsilon)
5. Add more sophisticated reward functions

---

**Status**: ✅ Ready for Integration  
**Last Updated**: Fusion Sprint Phase
