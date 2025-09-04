# 🚀 SuperManUS Installation Guide
## Complete Setup for Any Project

### 🎯 **Quick Installation Options**

#### **Option 1: Automated Installer (Recommended)**
```bash
# Clone SuperManUS repository
git clone https://github.com/your-org/SuperManUS-TaskEnforcer.git
cd SuperManUS-TaskEnforcer

# Install in your existing project
python install_supermanus.py /path/to/your/project

# With specific source directory
python install_supermanus.py ~/my-project --source .

# Dry run to preview changes
python install_supermanus.py ~/my-project --dry-run
```

#### **Option 2: One-Command Web Install**
```bash
# Direct installation from GitHub
curl -sSL https://raw.githubusercontent.com/your-org/SuperManUS-TaskEnforcer/main/install.sh | bash

# Install to specific directory
curl -sSL https://raw.githubusercontent.com/your-org/SuperManUS-TaskEnforcer/main/install.sh | bash -s -- /path/to/project
```

#### **Option 3: Manual Installation**
```bash
# 1. Clone repository
git clone https://github.com/your-org/SuperManUS-TaskEnforcer.git
cd SuperManUS-TaskEnforcer

# 2. Copy core files to your project
PROJECT_PATH="/path/to/your/project"
mkdir -p $PROJECT_PATH/supermanus
cp task_enforcer.py $PROJECT_PATH/supermanus/
cp llm_guard.py $PROJECT_PATH/supermanus/
cp -r integrations $PROJECT_PATH/supermanus/

# 3. Copy templates
cp SESSION_STATE.json $PROJECT_PATH/
cp WORK_LOG_TEMPLATE.md $PROJECT_PATH/
cp HUMAN_VALIDATION_GUIDE.md $PROJECT_PATH/

# 4. Make executable
chmod +x $PROJECT_PATH/supermanus/task_enforcer.py
```

---

## 🔧 **System Requirements**

### **Python Environment**
- Python 3.8 or higher
- pip (Python package installer)
- git (for repository operations)

### **Dependencies**
```bash
# Core dependencies (automatically installed)
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

### **Platform Support**
- ✅ Linux (all distributions)
- ✅ macOS (10.15+)  
- ✅ Windows 10+ (with WSL recommended)
- ✅ Docker containers
- ✅ GitHub Codespaces
- ✅ GitPod workspaces

---

## 📋 **Installation Verification**

### **Automatic Validation**
```bash
# Run validation script
python validate_installation.py

# Expected output:
# ✅ Core files installed correctly
# ✅ SESSION_STATE.json template created
# ✅ Integration modules available
# ✅ Validation commands working
# ✅ SuperManUS ready for use
```

### **Manual Verification**
```bash
# 1. Check core files
ls -la supermanus/
# Should see: task_enforcer.py, llm_guard.py, integrations/

# 2. Test import
python -c "from supermanus.task_enforcer import TaskSystemEnforcer; print('✅ Core import successful')"

# 3. Test enforcement
python -c "
from supermanus.task_enforcer import get_enforcer
enforcer = get_enforcer()
print(f'✅ Enforcer initialized: {type(enforcer).__name__}')
"

# 4. Check templates
ls -la SESSION_STATE.json WORK_LOG_TEMPLATE.md HUMAN_VALIDATION_GUIDE.md
```

---

## ⚙️ **Configuration Setup**

### **1. Initialize SESSION_STATE.json**
```json
{
  "current_session_id": "PROJECT_001",
  "last_updated": "2025-09-04T00:00:00Z",
  "project_name": "Your Project Name",
  "current_phase": "development",
  "active_tasks": [
    "SETUP.1: Configure SuperManUS task enforcement",
    "SETUP.2: Define initial project tasks",
    "SETUP.3: Test enforcement workflow"
  ],
  "completed_tasks": [],
  "team_assignments": {
    "developer_name": ["SETUP.1", "SETUP.2", "SETUP.3"]
  },
  "validation_requirements": {
    "all_tasks": {
      "work_log_required": true,
      "proof_required": true
    }
  }
}
```

### **2. Configure AI Tool Integrations**

#### **Claude Code Integration**
```python
# In your scripts
from supermanus.integrations.claude_code_integration import select_task, enforced_read, enforced_write

# Select official task
select_task("SETUP.1: Configure SuperManUS task enforcement")

# Use enforced operations
content = enforced_read("config.py", 
    justification="Reading current config to understand project structure for SuperManUS setup")

enforced_write("supermanus_config.py", config_code,
    justification="Creating SuperManUS configuration as required by SETUP.1")
```

#### **Cursor IDE Integration**
```bash
# Auto-generate .cursorrules.json
python -c "
from supermanus.integrations.cursor_integration import setup_cursor_enforcement
setup_cursor_enforcement()
print('✅ Cursor integration configured')
"
```

#### **GitHub Copilot Integration**
```bash
# Configure Copilot context
python -c "
from supermanus.integrations.github_copilot_integration import setup_copilot_enforcement
setup_copilot_enforcement()
print('✅ Copilot integration configured')
"
```

### **3. Create SuperManUS Configuration**
```bash
# Create configuration directory
mkdir -p .supermanus

# Basic configuration
cat > .supermanus/config.json << 'EOF'
{
    "enforcement_level": "strict",
    "work_log_required": true,
    "auto_approve_patterns": ["documentation", "test_.*"],
    "human_review_patterns": ["security_.*", "deploy_.*"],
    "integrations": {
        "cursor": {"enabled": true},
        "copilot": {"enabled": true},
        "claude_code": {"enabled": true}
    }
}
EOF
```

---

## 🎯 **First Time Setup Workflow**

### **Step 1: Install and Verify**
```bash
# Install SuperManUS
python install_supermanus.py .

# Verify installation
python validate_installation.py
```

### **Step 2: Define Your First Tasks**
```bash
# Edit SESSION_STATE.json with your actual project tasks
nano SESSION_STATE.json

# Example tasks:
# "T1.1: Set up development environment"
# "T1.2: Implement user authentication"
# "T1.3: Create basic CRUD operations"
```

### **Step 3: Test Enforcement**
```python
# Create test script: test_enforcement.py
from supermanus.integrations.claude_code_integration import select_task, enforced_write

# This will work - task is selected
select_task("T1.1: Set up development environment")
enforced_write("test.py", "print('Hello SuperManUS')", 
    justification="Testing SuperManUS enforcement as part of setup task T1.1")

# This will be blocked - no justification
# enforced_write("random.py", "print('This will fail')")
```

### **Step 4: Create Your First Work Log**
```bash
# Copy template
cp WORK_LOG_TEMPLATE.md work_logs/setup_task_T1_1.md

# Fill out the work log following the template
# This is required before any coding tasks
```

---

## 🔌 **Integration-Specific Setup**

### **For Existing Python Projects**
```python
# Add to your main project files
import sys
from pathlib import Path

# Add SuperManUS to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "supermanus"))

# Import and use
from task_enforcer import get_enforcer
from integrations.claude_code_integration import enforced_read, enforced_write
```

### **For Node.js Projects**
```bash
# Create Python bridge for Node.js projects
cat > supermanus_bridge.js << 'EOF'
const { spawn } = require('child_process');

function enforceTask(taskId, action, justification) {
    return new Promise((resolve, reject) => {
        const python = spawn('python', ['supermanus/task_enforcer.py', taskId, action, justification]);
        // Implementation continues...
    });
}

module.exports = { enforceTask };
EOF
```

### **For Docker Environments**
```dockerfile
# Add to your Dockerfile
COPY supermanus/ /app/supermanus/
COPY SESSION_STATE.json /app/
COPY WORK_LOG_TEMPLATE.md /app/
COPY HUMAN_VALIDATION_GUIDE.md /app/

# Install Python dependencies
RUN pip install -r supermanus/requirements.txt
```

### **For CI/CD Pipelines**
```yaml
# .github/workflows/supermanus-check.yml
name: SuperManUS Task Validation
on: [push, pull_request]

jobs:
  validate-task-discipline:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Validate SuperManUS Setup
      run: python validate_installation.py
    
    - name: Check Active Task
      run: python -c "from supermanus.task_enforcer import get_enforcer; assert get_enforcer().current_task"
```

---

## 🚨 **Troubleshooting**

### **Common Issues and Solutions**

#### **Issue: ModuleNotFoundError: No module named 'supermanus'**
```bash
# Solution: Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"
# Or add to your script:
import sys; sys.path.insert(0, '/path/to/your/project')
```

#### **Issue: FileNotFoundError: SESSION_STATE.json**
```bash
# Solution: Create from template
cp example_project/SESSION_STATE.json ./
# Edit with your project details
```

#### **Issue: Permission denied on install_supermanus.py**
```bash
# Solution: Make executable
chmod +x install_supermanus.py
# Or run with python directly
python install_supermanus.py
```

#### **Issue: AI tool integrations not working**
```bash
# Solution: Regenerate integration configs
python -c "
from supermanus.integrations import cursor_integration, github_copilot_integration
cursor_integration.setup_cursor_enforcement()
github_copilot_integration.setup_copilot_enforcement()
"
```

### **Debug Mode**
```bash
# Enable verbose logging
export SUPERMANUS_DEBUG=1
python your_script.py

# Check enforcement status
python -c "
from supermanus.task_enforcer import get_enforcer
enforcer = get_enforcer()
print(f'Current task: {enforcer.current_task}')
print(f'Enforcement active: {enforcer.is_active()}')
"
```

### **Reset Installation**
```bash
# Complete reset (use with caution)
rm -rf supermanus/
rm SESSION_STATE.json WORK_LOG_TEMPLATE.md HUMAN_VALIDATION_GUIDE.md
rm -rf .supermanus/

# Reinstall
python install_supermanus.py .
```

---

## 📚 **Next Steps**

After successful installation:

1. **📖 Read**: [Integration Guide](integrations.md) for AI tool setup
2. **👥 Review**: [Human Validation Guide](human-review.md) for team workflow
3. **🔬 Explore**: [Example Project](../example_project/) for real implementation
4. **🧪 Test**: Run `python demo_enforcement.py` to see enforcement in action

---

## 🆘 **Support**

### **Getting Help**
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-org/SuperManUS-TaskEnforcer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/SuperManUS-TaskEnforcer/discussions)
- 📖 **Documentation**: [Full Docs](https://supermanus-task-enforcer.readthedocs.io/)

### **Community**
- Share your SuperManUS setup in discussions
- Contribute integration patterns for new AI tools
- Help others troubleshoot installation issues

---

**Installation Guide Version**: 1.0  
**Last Updated**: 2025-09-04  
**Compatibility**: SuperManUS TaskEnforcer v1.0+