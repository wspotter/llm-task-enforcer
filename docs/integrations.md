# 🔗 SuperManUS AI Tool Integrations
## Complete Integration Guide for Popular AI Coding Tools

### 🎯 **Overview**
This guide provides detailed instructions for integrating SuperManUS task enforcement with popular AI coding tools, ensuring systematic development regardless of your AI assistant choice.

---

## 🤖 **Claude Code Integration**

### **Setup**
```python
# 1. Import enforced operations
from supermanus.integrations.claude_code_integration import (
    select_task, 
    enforced_read, 
    enforced_write, 
    enforced_bash,
    enforced_edit,
    get_enforced_claude_code
)

# 2. Select official task (REQUIRED before any operations)
select_task("T1.2: Implement user authentication")

# 3. Use enforced operations with justifications
content = enforced_read("auth.py", 
    justification="Reading current auth implementation to understand existing patterns for T1.2")

enforced_write("auth_enhanced.py", new_code,
    justification="Implementing OAuth support as required by task T1.2")

enforced_bash("pytest tests/test_auth.py", 
    justification="Validating authentication implementation for task T1.2")
```

### **Advanced Claude Code Integration**
```python
# Context manager for complex operations
from supermanus.integrations.claude_code_integration import EnforcedClaudeContext

with EnforcedClaudeContext("T1.2: Implement user authentication") as cc:
    # All operations automatically validated
    config = cc.read("config.py")
    cc.write("auth.py", generate_auth_code(config))
    cc.edit("main.py", add_auth_middleware)
    cc.bash("npm run test:auth")
    
    # Automatic proof generation
    proof = cc.generate_proof_package()
```

### **Configuration Options**
```python
# .supermanus/claude_code_config.py
CLAUDE_CODE_CONFIG = {
    "require_justification": True,
    "min_justification_length": 20,
    "auto_generate_work_logs": True,
    "validation_timeout": 30,
    "proof_requirements": {
        "file_operations": "syntax_check",
        "bash_operations": "exit_code_check",
        "complex_operations": "full_validation"
    }
}
```

---

## 🖥️ **Cursor IDE Integration**

### **Automatic Setup**
```bash
# Generate Cursor configuration
python -c "
from supermanus.integrations.cursor_integration import setup_cursor_enforcement
setup_cursor_enforcement()
print('✅ Cursor IDE configured for task enforcement')
"
```

### **Generated .cursorrules.json**
```json
{
  "version": "1.0",
  "rules": {
    "taskEnforcement": {
      "enabled": true,
      "requireActiveTask": true,
      "currentTask": "T1.2: Implement user authentication",
      "blockedActions": [
        "Creating files unrelated to current task",
        "Modifying critical files without justification",
        "Implementing features not in current task scope"
      ]
    },
    "codeGeneration": {
      "contextPrefix": "// Current Task: T1.2: Implement user authentication\\n// Justification: ",
      "requireJustification": true,
      "validateAgainstTask": true
    },
    "suggestions": {
      "filterByTask": true,
      "prioritizeTaskRelated": true,
      "addTaskComments": true
    }
  },
  "prompts": {
    "systemPrompt": "You are working on task T1.2: Implement user authentication. All code suggestions and modifications must advance this specific task. Require justification for how each change relates to the current task objectives.",
    "beforeSuggestion": "Ensure this suggestion directly advances task T1.2: Implement user authentication.",
    "beforeEdit": "Justify how this edit advances the current task: T1.2: Implement user authentication"
  }
}
```

### **Dynamic Task Context Update**
```python
# Update Cursor context when task changes
from supermanus.integrations.cursor_integration import update_cursor_task

# When switching tasks
select_task("T1.3: Create user dashboard")
update_cursor_task("T1.3: Create user dashboard")
# .cursorrules.json automatically updated
```

### **Cursor Workspace Settings**
```json
// .vscode/settings.json (automatically generated)
{
  "cursor.cpp.taskContext": "T1.2: Implement user authentication",
  "cursor.general.contextLength": 8000,
  "cursor.general.systemPrompt": "Focus on current task: T1.2: Implement user authentication. Require justification for suggestions.",
  "cursor.chat.systemPrompt": "You are helping with task T1.2: Implement user authentication. All suggestions must advance this specific task.",
  "cursor.autocomplete.disableInFiles": [
    "**/*test*",
    "**/node_modules/**"
  ]
}
```

---

## 🐙 **GitHub Copilot Integration**

### **Setup Process**
```bash
# Configure Copilot for task enforcement
python -c "
from supermanus.integrations.github_copilot_integration import setup_copilot_enforcement
setup_copilot_enforcement()
print('✅ GitHub Copilot configured for task enforcement')
"
```

### **Generated Configuration Files**

#### **.copilot-instructions.md**
```markdown
# GitHub Copilot Task Context

## Current Active Task
**T1.2: Implement user authentication**

## Task Requirements
- Implement OAuth2 authentication flow
- Support email/password login
- Create secure session management
- Add password reset functionality

## Code Generation Guidelines
1. All suggestions must advance the current task T1.2
2. Focus on authentication-related code only  
3. Follow security best practices for auth systems
4. Include error handling for auth failures
5. Add appropriate logging for auth events

## Blocked Suggestions
- UI/UX changes not related to authentication
- Database operations unrelated to user management
- Feature additions outside current task scope
- Performance optimizations not critical to auth functionality

## Context Files
- `src/auth/` - Main authentication modules
- `src/middleware/auth.js` - Authentication middleware
- `tests/auth/` - Authentication test files
- `config/auth.js` - Authentication configuration

## Success Criteria
- User can register with email/password
- User can login with valid credentials  
- Sessions are managed securely
- Password reset flow works end-to-end
- All authentication tests pass
```

#### **VS Code Settings for Copilot**
```json
// .vscode/settings.json additions
{
  "github.copilot.enable": {
    "*": true,
    "yaml": false,
    "plaintext": false
  },
  "github.copilot.advanced": {
    "secret_key": "current_task",
    "secret_value": "T1.2: Implement user authentication"
  },
  "github.copilot.editor.enableAutoCompletions": true,
  "files.associations": {
    "*.copilot-context": "markdown"
  }
}
```

### **Task Context Comments**
```python
# Automatically added to Python files
"""
SUPERMANUS TASK CONTEXT
Current Task: T1.2: Implement user authentication
Task Started: 2025-09-04T10:30:00Z
Developer: current_user

This file contributes to the authentication system implementation.
All code in this file should advance the authentication task objectives.

Required Deliverables:
- OAuth2 integration
- Session management  
- Password reset flow
- Security audit compliance
"""

# Your code here...
```

### **Copilot Chat Integration**
```javascript
// Custom Copilot chat commands
// In VS Code Command Palette: "Copilot: Ask Copilot"

// Task-specific prompts:
// /task-help - Get help with current task T1.2
// /task-validate - Validate code against task requirements  
// /task-suggest - Get task-focused suggestions
// /task-review - Review code for task compliance
```

---

## 🔧 **VS Code Integration**

### **Extension Configuration**
```bash
# Install SuperManUS VS Code extension (if available)
code --install-extension supermanus.task-enforcer

# Or configure manually
python -c "
from supermanus.integrations.vscode_integration import setup_vscode_enforcement
setup_vscode_enforcement()
"
```

### **Workspace Settings**
```json
// .vscode/settings.json
{
  "supermanus.taskEnforcement.enabled": true,
  "supermanus.taskEnforcement.currentTask": "T1.2: Implement user authentication",
  "supermanus.taskEnforcement.workLogRequired": true,
  "supermanus.taskEnforcement.autoValidation": true,
  
  "files.watcherExclude": {
    "**/work_logs/**": false
  },
  
  "editor.rulers": [80, 120],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "supermanus.validateTask": true
  },
  
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.testing.pytestEnabled": true
}
```

### **Custom Snippets**
```json
// .vscode/supermanus-snippets.code-snippets
{
  "SuperManUS Work Log Entry": {
    "prefix": "smwl",
    "body": [
      "### Task Information",
      "- **Task ID:** ${1:T1.2}",
      "- **Task Description:** ${2:Implement user authentication}",
      "- **Start Time:** $CURRENT_DATETIME",
      "",
      "### Work Performed", 
      "#### Step 1: ${3:Action Description}",
      "- **Command/Action:** ${4:exact command}",
      "- **Expected Result:** ${5:what should happen}",
      "- **Actual Result:** ${6:what actually happened}",
      "- **Validation:** ${7:how was success confirmed}",
      "- **Files Created/Modified:** ${8:list with paths}"
    ],
    "description": "SuperManUS work log entry template"
  },
  
  "Task Justification Comment": {
    "prefix": "smjust",
    "body": [
      "# TASK: ${1:T1.2} - ${2:Brief description}",
      "# JUSTIFICATION: ${3:How this code advances the current task}",
      "# CONTEXT: ${4:Additional context or dependencies}"
    ],
    "description": "Add task justification comment"
  }
}
```

---

## 🔀 **Multi-Tool Integration**

### **Unified Enforcement Wrapper**
```python
# supermanus/unified_integration.py
class UnifiedAIEnforcement:
    def __init__(self):
        self.active_integrations = {}
        self.current_task = None
    
    def setup_all_integrations(self):
        """Configure all available AI tools"""
        from integrations import (
            claude_code_integration,
            cursor_integration, 
            github_copilot_integration,
            vscode_integration
        )
        
        # Setup each integration
        claude_code_integration.setup()
        cursor_integration.setup_cursor_enforcement()
        github_copilot_integration.setup_copilot_enforcement()
        vscode_integration.setup_vscode_enforcement()
        
        self.active_integrations = {
            'claude_code': True,
            'cursor': True,
            'copilot': True,
            'vscode': True
        }
    
    def update_all_tasks(self, task_id: str):
        """Update task context across all tools"""
        self.current_task = task_id
        
        if self.active_integrations.get('cursor'):
            cursor_integration.update_cursor_task(task_id)
        
        if self.active_integrations.get('copilot'):
            github_copilot_integration.update_copilot_context(task_id)
        
        if self.active_integrations.get('vscode'):
            vscode_integration.update_workspace_task(task_id)

# Usage
unified = UnifiedAIEnforcement()
unified.setup_all_integrations()
unified.update_all_tasks("T1.3: Create user dashboard")
```

### **Cross-Tool Validation**
```python
# Validate consistency across all AI tools
def validate_all_integrations():
    """Ensure all AI tools have consistent task context"""
    from integrations.validation import IntegrationValidator
    
    validator = IntegrationValidator()
    results = {
        'cursor': validator.validate_cursor_config(),
        'copilot': validator.validate_copilot_config(),
        'claude_code': validator.validate_claude_code_config(),
        'vscode': validator.validate_vscode_config()
    }
    
    inconsistencies = [
        tool for tool, valid in results.items() 
        if not valid
    ]
    
    if inconsistencies:
        print(f"⚠️  Inconsistent integrations: {inconsistencies}")
        return False
    
    print("✅ All integrations consistent")
    return True
```

---

## 🏗️ **Custom Integration Framework**

### **Creating New Integrations**
```python
# Template for new AI tool integrations
from supermanus.integrations.base import BaseIntegration

class CustomAIToolIntegration(BaseIntegration):
    def __init__(self):
        super().__init__()
        self.tool_name = "CustomAITool"
        self.config_files = [".customaitool-config.json"]
    
    def setup_enforcement(self):
        """Configure the AI tool for task enforcement"""
        config = {
            "task_context": self.get_current_task(),
            "enforcement_level": "strict",
            "require_justification": True
        }
        self.write_config_file(self.config_files[0], config)
    
    def update_task_context(self, task_id: str):
        """Update task context in the AI tool"""
        config = self.load_config_file(self.config_files[0])
        config["task_context"] = task_id
        config["last_updated"] = self.get_timestamp()
        self.write_config_file(self.config_files[0], config)
    
    def validate_integration(self) -> bool:
        """Validate integration is working correctly"""
        try:
            config = self.load_config_file(self.config_files[0])
            return config.get("task_context") == self.get_current_task()
        except Exception:
            return False

# Register new integration
from supermanus.integrations import register_integration
register_integration(CustomAIToolIntegration())
```

---

## 🔍 **Monitoring and Validation**

### **Integration Health Checks**
```bash
# Check all integration statuses
python -c "
from supermanus.integrations.health import check_all_integrations
results = check_all_integrations()
for tool, status in results.items():
    print(f'{tool}: {\"✅\" if status else \"❌\"} ')
"
```

### **Automated Integration Testing**
```python
# tests/test_integrations.py
import pytest
from supermanus.integrations import (
    claude_code_integration,
    cursor_integration,
    github_copilot_integration
)

def test_claude_code_integration():
    # Test enforced operations
    select_task("TEST.1: Integration testing")
    result = enforced_write("test.py", "print('test')", 
        justification="Testing integration for TEST.1")
    assert result.success

def test_cursor_integration():
    # Test cursor configuration
    cursor_integration.setup_cursor_enforcement()
    assert os.path.exists(".cursorrules.json")
    
    with open(".cursorrules.json") as f:
        config = json.load(f)
        assert "taskEnforcement" in config["rules"]

def test_copilot_integration():
    # Test copilot configuration
    github_copilot_integration.setup_copilot_enforcement()
    assert os.path.exists(".copilot-instructions.md")
```

### **Performance Monitoring**
```python
# Monitor integration performance impact
from supermanus.integrations.metrics import IntegrationMetrics

metrics = IntegrationMetrics()
performance_data = {
    "claude_code_overhead": metrics.measure_claude_code_latency(),
    "cursor_config_update_time": metrics.measure_cursor_update_time(),
    "copilot_context_injection_time": metrics.measure_copilot_injection_time()
}

# Log to monitoring system
send_metrics_to_monitoring(performance_data)
```

---

## 🚨 **Troubleshooting Integrations**

### **Common Issues**

#### **Claude Code: Import Errors**
```bash
# Problem: Cannot import enforced operations
# Solution: Check Python path and installation
python -c "import sys; print(sys.path)"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### **Cursor: Configuration Not Loading**
```bash
# Problem: .cursorrules.json ignored
# Solution: Restart Cursor and check file format
cat .cursorrules.json | python -m json.tool  # Validate JSON
```

#### **Copilot: Context Not Applied**
```bash
# Problem: Copilot ignoring task context
# Solution: Check VS Code settings and reload window
code --list-extensions | grep copilot
# Reload VS Code window: Cmd+Shift+P -> "Developer: Reload Window"
```

### **Debug Mode**
```bash
# Enable debug logging for integrations
export SUPERMANUS_INTEGRATION_DEBUG=1
python your_script_with_integrations.py
```

---

## 📊 **Integration Analytics**

### **Usage Metrics**
```python
# Track integration effectiveness
from supermanus.integrations.analytics import IntegrationAnalytics

analytics = IntegrationAnalytics()
metrics = {
    "task_adherence_rate": analytics.calculate_task_adherence(),
    "integration_usage": analytics.get_integration_usage_stats(), 
    "deviation_prevention": analytics.count_prevented_deviations(),
    "human_review_reduction": analytics.calculate_review_efficiency()
}

# Generate integration effectiveness report
analytics.generate_integration_report(metrics)
```

---

## 🎯 **Best Practices**

### **Integration Maintenance**
1. **Regular Updates**: Update integration configs when tasks change
2. **Validation Checks**: Run integration health checks before major work
3. **Backup Configs**: Keep backup copies of working configurations
4. **Team Sync**: Ensure all team members use same integration setup

### **Performance Optimization**
1. **Selective Integration**: Only enable integrations you actively use
2. **Configuration Caching**: Cache integration configs to reduce setup time
3. **Lazy Loading**: Load integrations only when needed
4. **Resource Monitoring**: Monitor integration performance impact

---

**Integration Guide Version**: 1.0  
**Last Updated**: 2025-09-04  
**Compatibility**: All SuperManUS TaskEnforcer versions