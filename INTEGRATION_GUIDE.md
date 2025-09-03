# 🔗 SuperManUS Integration Guide
## Adding Task Enforcement to Your AI Coding Workflow

### 🎯 **Overview**
This guide shows how to integrate SuperManUS task enforcement into popular AI coding tools and workflows, preventing the 90% LLM deviation problem.

---

## 🚀 **Quick Installation**

### **Option 1: Automated Installer**
```bash
# Install in any existing project
python /path/to/SuperManUS/install_supermanus.py /path/to/your/project

# Install with integrations
python install_supermanus.py ~/my-project --source .

# Dry run to see what will be installed
python install_supermanus.py ~/my-project --dry-run
```

### **Option 2: Manual Integration**
```bash
# 1. Copy core files
cp src/utils/task_enforcer.py your-project/supermanus/
cp src/utils/llm_guard.py your-project/supermanus/

# 2. Copy integrations
cp integrations/* your-project/supermanus/integrations/

# 3. Create SESSION_STATE.json (see template below)

# 4. Start using enforced operations
```

---

## 🛠️ **Integration Patterns**

### **Pattern 1: Drop-in Replacement**
Replace standard operations with enforced versions:

```python
# Before (standard Claude Code)
content = read_file("config.py")
write_file("new_feature.py", code)
run_bash("pytest tests/")

# After (SuperManUS enforced)
from claude_code_integration import enforced_read, enforced_write, enforced_bash

content = enforced_read("config.py", 
    justification="Reading config to understand current task requirements")
    
enforced_write("new_feature.py", code, 
    justification="Implementing feature X as specified in task T1.2.3")
    
enforced_bash("pytest tests/", 
    justification="Validating task completion with test suite")
```

### **Pattern 2: Context Manager**
Use guards for complex operations:

```python
from llm_guard import LLMActionGuard

with LLMActionGuard("Refactor authentication module", 
                   "Task T2.1 requires updating auth to support OAuth"):
    # All operations in this block are validated
    refactor_auth_code()
    update_tests()
    validate_security()
```

### **Pattern 3: Decorator-Based**
Add enforcement to existing functions:

```python
from llm_guard import require_active_task, require_task_justification

@require_active_task
@require_task_justification("Database schema migration")
def migrate_database():
    # Function automatically blocked without active task
    # Must provide justification for how this advances task
    pass
```

---

## 🤖 **AI Tool Integrations**

### **Claude Code Integration**
Complete drop-in replacement for Claude Code tools:

```python
# Setup
from claude_code_integration import get_enforced_claude_code, select_task

# Select official task first  
select_task("T1.3: Implement user authentication")

# All operations now require justification
cc = get_enforced_claude_code()
cc.read_file("auth.py", justification="Analyzing current auth implementation")
cc.write_file("auth_v2.py", new_code, justification="Implementing OAuth support")
cc.run_bash("python -m pytest", justification="Validating implementation")
```

### **Cursor IDE Integration** 
Configures Cursor AI to stay on-task:

```python
from cursor_integration import setup_cursor_enforcement

# Creates .cursorrules.json with task context
setup_cursor_enforcement()

# Cursor AI now gets task constraints automatically:
# - Only suggests code for current task
# - Requires justification for suggestions  
# - Blocks unrelated features
```

### **GitHub Copilot Integration**
Adds task context to Copilot suggestions:

```python
from github_copilot_integration import setup_copilot_enforcement

# Sets up task-aware Copilot configuration
setup_copilot_enforcement()

# Creates:
# - .copilot-instructions.md with current task context
# - Task context comments in Python files  
# - VS Code settings optimized for task focus
```

---

## 📋 **Workflow Integration**

### **Standard Development Workflow**
```python
# 1. Start with task selection
from task_enforcer import get_enforcer, select_task

enforcer = get_enforcer()
tasks = enforcer.get_active_tasks()
select_task(tasks[0])  # Choose from official SESSION_STATE.json

# 2. Create work log (required)
enforcer.require_work_log()  # Shows template and requirements

# 3. Use enforced operations
from claude_code_integration import enforced_read, enforced_write

code = enforced_read("module.py", 
    justification="Understanding current implementation for task requirements")

enforced_write("enhanced_module.py", updated_code,
    justification="Implementing feature required by current task T1.2")

# 4. Complete with proof
proof_package = {
    "file_evidence": "ls -la enhanced_module.py",
    "functional_test": "python test_module.py --verbose", 
    "error_check": "python -m py_compile enhanced_module.py"
}

result = enforcer.validate_completion(proof_package)
```

### **Team Development Workflow**
```python
# Team lead selects tasks in SESSION_STATE.json
{
    "active_tasks": [
        "T1.1: Developer A - Implement authentication", 
        "T1.2: Developer B - Create user dashboard",
        "T1.3: Developer C - Add data validation"
    ]
}

# Each developer uses their assigned task
select_task("T1.1: Developer A - Implement authentication")

# All work automatically tracked and validated
# Human reviewer uses HUMAN_VALIDATION_GUIDE.md for approval
```

### **CI/CD Integration**
```yaml
# .github/workflows/supermanus-validation.yml
name: SuperManUS Task Validation

on: [push, pull_request]

jobs:
  validate-task-discipline:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Check Task Discipline
      run: |
        python -c "
        import sys; sys.path.insert(0, 'supermanus')
        from task_enforcer import get_enforcer
        enforcer = get_enforcer()
        assert enforcer.current_task, 'No active task selected'
        print('✅ Task discipline maintained')
        "
    
    - name: Validate Work Log
      run: |
        ls work_logs/*.md || (echo '❌ No work log found' && exit 1)
        echo '✅ Work log exists'
    
    - name: Run Validation Commands
      run: |
        # Run the validation commands from task requirements
        python -m pytest -v
        python -m flake8 --max-line-length=120
        find . -name "*.py" -exec python -m py_compile {} \;
```

---

## 🏗️ **Architecture Patterns**

### **Microservice Integration**
For distributed development:

```python
# Each microservice gets its own SuperManUS instance
# with shared SESSION_STATE.json

# service-a/supermanus_config.py
SERVICE_TASKS = [
    "T1.1: API Gateway - Implement rate limiting",
    "T1.2: API Gateway - Add authentication middleware"
]

# service-b/supermanus_config.py  
SERVICE_TASKS = [
    "T2.1: User Service - Implement user CRUD",
    "T2.2: User Service - Add password hashing"
]

# Shared task validation across services
def validate_cross_service_task(task_id: str, service: str):
    # Ensure task belongs to this service
    if not task_id.startswith(f"T{service_id}"):
        raise TaskViolationException("Task not assigned to this service")
```

### **Monorepo Integration**
For large codebases:

```python
# Different SuperManUS instances per module
# with hierarchical task organization

# Root SESSION_STATE.json
{
    "active_tasks": [
        "M1: Frontend Module - User interface overhaul",
        "M2: Backend Module - Database optimization", 
        "M3: DevOps Module - Deployment automation"
    ]
}

# frontend/SESSION_STATE.json (inherits from root)
{
    "parent_task": "M1: Frontend Module - User interface overhaul",
    "active_tasks": [
        "M1.T1: Redesign login page",
        "M1.T2: Implement responsive design",
        "M1.T3: Add accessibility features"
    ]
}
```

### **Plugin Architecture**
For extensible enforcement:

```python
# Custom enforcement plugins
class CustomValidationPlugin:
    def validate_task_completion(self, task_id: str, proof: Dict) -> bool:
        # Custom business logic validation
        if "security" in task_id.lower():
            return self.validate_security_requirements(proof)
        return True

# Register plugin
from task_enforcer import get_enforcer
enforcer = get_enforcer()
enforcer.register_plugin(CustomValidationPlugin())
```

---

## 🔧 **Configuration Examples**

### **PROJECT_ROOT/.supermanus/config.json**
```json
{
    "enforcement_level": "strict",
    "auto_approve_patterns": [
        "documentation",
        "test_.*", 
        "fix_typo"
    ],
    "human_review_patterns": [
        "security_.*",
        "architecture_.*",
        "deploy_.*"
    ],
    "validation_timeout": 300,
    "work_log_required": true,
    "integrations": {
        "cursor": {
            "enabled": true,
            "inject_context": true
        },
        "copilot": {
            "enabled": true,
            "context_length": 500
        },
        "claude_code": {
            "enabled": true,
            "require_justification": true
        }
    }
}
```

### **Custom Validation Rules**
```python
# .supermanus/custom_rules.py
from task_enforcer import ValidationResult

def validate_database_changes(task_id: str, changes: List[str]) -> ValidationResult:
    """Custom validation for database-related tasks"""
    
    if "database" in task_id.lower():
        # Require migration scripts
        if not any("migration" in change for change in changes):
            return ValidationResult.REJECTED
        
        # Require backup strategy
        if not any("backup" in change for change in changes):
            return ValidationResult.PENDING  # Human review
    
    return ValidationResult.APPROVED
```

---

## 📊 **Monitoring and Analytics**

### **Task Completion Metrics**
```python
# Generate task discipline reports
from task_enforcer import get_enforcer

enforcer = get_enforcer()

metrics = {
    "tasks_completed": len(enforcer.validation_history),
    "average_task_duration": calculate_average_duration(),
    "deviation_attempts": count_blocked_actions(),
    "human_review_rate": calculate_human_review_percentage(),
    "top_violation_types": get_violation_patterns()
}

# Export to monitoring systems
send_to_datadog(metrics)
log_to_prometheus(metrics)
```

### **Integration Health Monitoring**
```python
# Monitor integration effectiveness
def check_integration_health():
    health = {
        "cursor": cursor_integration.is_healthy(),
        "copilot": copilot_integration.is_healthy(), 
        "claude_code": claude_code_integration.is_healthy(),
        "task_discipline": check_task_discipline()[0]
    }
    
    return health
```

---

## 🚨 **Common Integration Issues**

### **Issue 1: Import Path Problems**
```python
# Problem: SuperManUS modules not found
# Solution: Add to Python path
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "supermanus"))
```

### **Issue 2: SESSION_STATE.json Missing**
```python  
# Problem: FileNotFoundError for SESSION_STATE.json
# Solution: Create with installer or manually
from install_supermanus import SuperManUSInstaller

installer = SuperManUSInstaller(".")
installer.create_session_state_template()
```

### **Issue 3: Work Log Not Created**
```python
# Problem: Task blocked because no work log
# Solution: Use the template
from task_enforcer import get_enforcer

enforcer = get_enforcer()
work_log_msg = enforcer.require_work_log()
print(work_log_msg)  # Shows template to create
```

---

## 🎯 **Best Practices**

### **Task Definition Best Practices**
```python
# ✅ Good task definitions
"T1.2.1: Implement OAuth2 authentication with Google provider"
"T2.3.4: Add input validation to user registration form"
"T3.1.2: Optimize database queries for user dashboard"

# ❌ Poor task definitions  
"Fix stuff"
"Make it better"
"Update code"
```

### **Justification Best Practices**
```python
# ✅ Good justifications
justification = "This refactors the authentication module to support OAuth2 as required by task T1.2.1, specifically implementing the Google provider integration"

# ❌ Poor justifications
justification = "Updating code"
justification = "It's necessary"
justification = "Because"
```

### **Proof Package Best Practices**
```python
# ✅ Comprehensive proof
proof_package = {
    "file_evidence": "ls -la auth/ && wc -l auth/*.py",
    "functional_test": "python -m pytest tests/test_oauth.py -v",
    "integration_test": "python test_google_auth_flow.py",
    "error_check": "python -m flake8 auth/ && python -m mypy auth/",
    "security_check": "python security_scan.py auth/",
    "documentation": "Updated docs/authentication.md with OAuth flow"
}

# ❌ Insufficient proof
proof_package = {
    "functional_test": "It works"
}
```

---

## 🔮 **Advanced Integration Patterns**

### **Multi-LLM Coordination**
```python
# Prevent multiple LLMs from conflicting
class LLMCoordinator:
    def __init__(self):
        self.active_llm_sessions = {}
    
    def request_task_lock(self, task_id: str, llm_id: str):
        if task_id in self.active_llm_sessions:
            raise TaskViolationException(f"Task {task_id} already assigned to {self.active_llm_sessions[task_id]}")
        
        self.active_llm_sessions[task_id] = llm_id
        return True
```

### **Dynamic Task Generation**
```python
# Generate tasks based on codebase analysis
def generate_refactoring_tasks(codebase_path: str) -> List[str]:
    analysis = analyze_code_quality(codebase_path)
    
    tasks = []
    for issue in analysis.issues:
        task_id = f"REFACTOR_{issue.severity}_{issue.component}"
        tasks.append(f"{task_id}: {issue.description}")
    
    return tasks
```

### **Cross-Project Task Dependencies**
```python
# Handle tasks that span multiple repositories
class CrossProjectEnforcer(TaskSystemEnforcer):
    def validate_cross_project_task(self, task_id: str, dependent_projects: List[str]):
        # Ensure all dependent projects are ready
        for project in dependent_projects:
            project_state = load_project_session_state(project)
            if not project_state.has_completed_prerequisites(task_id):
                return ValidationResult.BLOCKED
        
        return ValidationResult.APPROVED
```

---

**Integration Guide Version:** 1.0  
**Created:** 2025-09-03  
**Usage:** Reference for integrating SuperManUS into any AI coding workflow