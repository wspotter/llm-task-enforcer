# 🔌 SuperManUS API Reference
## Complete Technical Documentation

### 🎯 **Overview**
This document provides comprehensive API reference for SuperManUS TaskEnforcer components, enabling custom integrations and advanced usage patterns.

---

## 🏗️ **Core API Components**

### **TaskSystemEnforcer Class**

#### **Constructor**
```python
from supermanus.task_enforcer import TaskSystemEnforcer

enforcer = TaskSystemEnforcer(
    session_state_path: str = "SESSION_STATE.json",
    work_log_dir: str = "work_logs",
    config_path: str = ".supermanus/config.json",
    strict_mode: bool = True
)
```

**Parameters:**
- `session_state_path`: Path to SESSION_STATE.json file
- `work_log_dir`: Directory for work log files  
- `config_path`: Path to SuperManUS configuration
- `strict_mode`: Enable strict task enforcement

#### **Core Methods**

##### **select_task()**
```python
def select_task(self, task_id: str) -> TaskSelectionResult:
    """Select an official task from SESSION_STATE.json"""
```

**Parameters:**
- `task_id` (str): Task identifier from active_tasks

**Returns:**
- `TaskSelectionResult`: Contains success status and task details

**Example:**
```python
result = enforcer.select_task("T1.2: Implement user authentication")
if result.success:
    print(f"Selected task: {result.task.description}")
else:
    print(f"Error: {result.error_message}")
```

##### **validate_action()**
```python
def validate_action(
    self, 
    action: str, 
    justification: str,
    context: Optional[Dict] = None
) -> ValidationResult:
    """Validate an action against current task"""
```

**Parameters:**
- `action` (str): Description of action to perform
- `justification` (str): How action advances current task
- `context` (Optional[Dict]): Additional context data

**Returns:**
- `ValidationResult`: Validation outcome and details

**Example:**
```python
result = enforcer.validate_action(
    "Create OAuth configuration file",
    "Setting up OAuth as required by authentication task T1.2",
    context={"file_path": "config/oauth.py"}
)

if result.status == ValidationStatus.APPROVED:
    # Proceed with action
    pass
elif result.status == ValidationStatus.BLOCKED:
    print(f"Action blocked: {result.reason}")
```

##### **complete_task()**
```python
def complete_task(
    self, 
    task_id: str,
    proof_package: Dict[str, str]
) -> CompletionResult:
    """Complete a task with proof of completion"""
```

**Parameters:**
- `task_id` (str): Task to complete
- `proof_package` (Dict[str, str]): Evidence of completion

**Returns:**
- `CompletionResult`: Completion validation outcome

**Example:**
```python
proof_package = {
    "file_evidence": "ls -la src/auth/",
    "functional_test": "python -m pytest tests/auth/ -v",
    "integration_test": "curl -f http://localhost:8000/auth/status"
}

result = enforcer.complete_task("T1.2: Implement user authentication", proof_package)
```

#### **Session Management**

##### **get_session_state()**
```python
def get_session_state(self) -> SessionState:
    """Get current session state"""
```

**Returns:**
- `SessionState`: Current project session data

##### **update_session_state()**
```python
def update_session_state(self, updates: Dict[str, Any]) -> bool:
    """Update session state with new data"""
```

**Parameters:**
- `updates` (Dict[str, Any]): Updates to apply

**Returns:**
- `bool`: Success status

#### **Work Log Management**

##### **require_work_log()**
```python
def require_work_log(self, task_id: Optional[str] = None) -> WorkLogRequirement:
    """Check/create work log requirement"""
```

**Parameters:**
- `task_id` (Optional[str]): Task requiring work log

**Returns:**
- `WorkLogRequirement`: Work log status and template

##### **validate_work_log()**
```python
def validate_work_log(self, work_log_path: str) -> WorkLogValidation:
    """Validate work log completeness"""
```

**Parameters:**
- `work_log_path` (str): Path to work log file

**Returns:**
- `WorkLogValidation`: Validation results

---

## 🛡️ **LLMGuard Class**

### **Constructor**
```python
from supermanus.llm_guard import LLMGuard

guard = LLMGuard(
    enforcer: TaskSystemEnforcer,
    validation_config: Optional[Dict] = None
)
```

### **Core Methods**

#### **guard_action()**
```python
def guard_action(
    self, 
    action_type: ActionType,
    action_data: Dict[str, Any],
    justification: str
) -> GuardResult:
    """Guard any LLM action with validation"""
```

**Parameters:**
- `action_type` (ActionType): Type of action being performed
- `action_data` (Dict): Action-specific data
- `justification` (str): Task advancement justification

**Returns:**
- `GuardResult`: Guard decision and details

#### **Context Manager Usage**
```python
from supermanus.llm_guard import LLMActionGuard

with LLMActionGuard("Refactor authentication", "Required for task T1.2") as guard:
    # All operations automatically validated
    result = guard.protected_operation(lambda: perform_refactoring())
```

---

## 🔌 **Integration APIs**

### **Claude Code Integration**

#### **Enforced Operations**
```python
from supermanus.integrations.claude_code_integration import (
    enforced_read,
    enforced_write, 
    enforced_edit,
    enforced_bash,
    enforced_glob,
    enforced_grep
)

# File operations
content = enforced_read(
    file_path: str,
    justification: str,
    context: Optional[Dict] = None
) -> str

success = enforced_write(
    file_path: str,
    content: str, 
    justification: str,
    context: Optional[Dict] = None
) -> bool

# Command operations  
result = enforced_bash(
    command: str,
    justification: str,
    timeout: Optional[int] = None
) -> BashResult

# Search operations
matches = enforced_grep(
    pattern: str,
    justification: str,
    path: Optional[str] = None,
    options: Optional[Dict] = None
) -> List[Match]
```

#### **Batch Operations**
```python
from supermanus.integrations.claude_code_integration import EnforcedBatch

batch = EnforcedBatch("T1.2: Implement authentication")
batch.add_read("config.py", "Reading current config")
batch.add_write("auth.py", auth_code, "Creating auth module") 
batch.add_bash("pytest tests/", "Validating implementation")

results = batch.execute()
```

### **Cursor Integration**

#### **Configuration Management**
```python
from supermanus.integrations.cursor_integration import (
    setup_cursor_enforcement,
    update_cursor_task,
    get_cursor_config,
    validate_cursor_config
)

# Setup
config = setup_cursor_enforcement(
    task_id: str,
    custom_rules: Optional[Dict] = None
) -> CursorConfig

# Updates
success = update_cursor_task(
    new_task_id: str,
    preserve_custom_rules: bool = True
) -> bool

# Validation
validation = validate_cursor_config() -> CursorValidation
```

### **GitHub Copilot Integration**

#### **Context Management**
```python
from supermanus.integrations.github_copilot_integration import (
    setup_copilot_enforcement,
    update_copilot_context,
    generate_copilot_instructions,
    validate_copilot_setup
)

# Setup
setup_result = setup_copilot_enforcement(
    task_id: str,
    context_files: Optional[List[str]] = None,
    custom_instructions: Optional[str] = None
) -> CopilotSetup

# Context updates
success = update_copilot_context(
    task_id: str,
    additional_context: Optional[str] = None
) -> bool
```

---

## 📊 **Analytics and Metrics APIs**

### **TaskEnforcementMetrics Class**
```python
from supermanus.analytics import TaskEnforcementMetrics

metrics = TaskEnforcementMetrics(
    session_state_path: str = "SESSION_STATE.json",
    work_logs_dir: str = "work_logs",
    history_days: int = 30
)
```

#### **Core Metrics**
```python
# Task completion metrics
completion_rate = metrics.task_completion_rate() -> float
average_duration = metrics.average_task_duration() -> timedelta
deviation_rate = metrics.deviation_prevention_rate() -> float

# Quality metrics  
quality_score = metrics.completion_quality_score() -> float
rework_rate = metrics.task_rework_rate() -> float
human_review_efficiency = metrics.human_review_efficiency() -> float

# Team metrics
team_productivity = metrics.team_productivity_metrics() -> Dict[str, float]
collaboration_score = metrics.collaboration_effectiveness() -> float
```

#### **Time Series Data**
```python
# Historical trends
completion_trend = metrics.get_completion_trend(
    start_date: datetime,
    end_date: datetime,
    granularity: str = "day"  # "hour", "day", "week"
) -> List[MetricPoint]

productivity_trend = metrics.get_productivity_trend(
    developer: Optional[str] = None,
    task_type: Optional[str] = None
) -> List[ProductivityPoint]
```

#### **Advanced Analytics**
```python
# Predictive metrics
estimated_completion = metrics.predict_task_completion(
    task_id: str,
    current_progress: Optional[float] = None
) -> CompletionPrediction

bottleneck_analysis = metrics.analyze_bottlenecks() -> BottleneckReport

risk_assessment = metrics.assess_project_risks() -> RiskAssessment
```

### **Real-time Monitoring**
```python
from supermanus.monitoring import TaskMonitor

monitor = TaskMonitor()

# Event monitoring
@monitor.on_task_start
def handle_task_start(task_id: str, developer: str):
    print(f"Task {task_id} started by {developer}")

@monitor.on_deviation_attempt  
def handle_deviation(action: str, reason: str):
    alert_team(f"Deviation blocked: {action} - {reason}")

# Start monitoring
monitor.start_monitoring()
```

---

## 🔧 **Configuration APIs**

### **Configuration Management**
```python
from supermanus.config import SuperManUSConfig

config = SuperManUSConfig.load_config(".supermanus/config.json")

# Access configuration
enforcement_level = config.enforcement_level  # "strict", "moderate", "permissive"
auto_approval_patterns = config.auto_approval_patterns  # List[str]
human_review_patterns = config.human_review_patterns  # List[str]

# Update configuration
config.enforcement_level = "strict"
config.add_auto_approval_pattern("test_.*")
config.save()
```

### **Dynamic Configuration**
```python
# Runtime configuration updates
from supermanus.config import update_runtime_config

update_runtime_config({
    "enforcement_level": "moderate",
    "timeout_seconds": 60,
    "require_work_log": False
})

# Environment-specific configs
config.load_environment_config("development")  # Loads dev-specific settings
```

---

## 🚨 **Error Handling and Exceptions**

### **Exception Hierarchy**
```python
# Base exceptions
class SuperManUSException(Exception):
    """Base exception for all SuperManUS errors"""

class TaskViolationException(SuperManUSException):
    """Raised when task enforcement rules are violated"""

class ValidationException(SuperManUSException):
    """Raised when validation fails"""

class ConfigurationException(SuperManUSException):
    """Raised for configuration-related errors"""

# Specific exceptions
class NoActiveTaskException(TaskViolationException):
    """No task selected before attempting operation"""

class InvalidTaskException(TaskViolationException):
    """Selected task not in active_tasks"""

class InsufficientJustificationException(TaskViolationException):
    """Action justification doesn't meet requirements"""

class WorkLogRequiredException(ValidationException):
    """Work log required but not found"""

class ProofValidationException(ValidationException):
    """Task completion proof validation failed"""
```

### **Error Response Format**
```python
# Standardized error responses
class ErrorResponse:
    def __init__(self, error: Exception, context: Dict = None):
        self.error_type = type(error).__name__
        self.error_message = str(error)
        self.error_code = getattr(error, 'error_code', None)
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()
        self.suggested_actions = self._get_suggested_actions(error)

    def to_dict(self) -> Dict:
        return {
            "error_type": self.error_type,
            "error_message": self.error_message, 
            "error_code": self.error_code,
            "context": self.context,
            "timestamp": self.timestamp,
            "suggested_actions": self.suggested_actions
        }
```

---

## 🔍 **Validation APIs**

### **Validation Engine**
```python
from supermanus.validation import ValidationEngine

engine = ValidationEngine()

# File validation
file_result = engine.validate_file_operation(
    operation: str,  # "read", "write", "edit"
    file_path: str,
    content: Optional[str] = None,
    justification: str
) -> FileValidationResult

# Command validation  
command_result = engine.validate_command(
    command: str,
    justification: str,
    safe_commands: Optional[List[str]] = None
) -> CommandValidationResult

# Task validation
task_result = engine.validate_task_alignment(
    action: str,
    task_id: str,
    justification: str
) -> TaskAlignmentResult
```

### **Custom Validation Rules**
```python
from supermanus.validation import ValidationRule

class SecurityReviewRule(ValidationRule):
    def applies_to(self, action: str, context: Dict) -> bool:
        return "security" in action.lower() or "auth" in action.lower()
    
    def validate(self, action: str, justification: str, context: Dict) -> ValidationResult:
        if "security review completed" not in justification:
            return ValidationResult.rejected("Security tasks require security review")
        return ValidationResult.approved()

# Register custom rule
engine.register_rule(SecurityReviewRule())
```

---

## 🧪 **Testing APIs**

### **Test Utilities**
```python
from supermanus.testing import SuperManUSTestCase, MockEnforcer

class TestMyFeature(SuperManUSTestCase):
    def setUp(self):
        self.enforcer = MockEnforcer()
        self.enforcer.set_active_task("TEST.1: Test feature implementation")
    
    def test_enforced_operation(self):
        # Test with enforcement
        with self.assertRaises(TaskViolationException):
            enforced_write("test.py", "content", "invalid justification")
        
        # Test valid operation
        result = enforced_write("test.py", "content", 
            "Testing implementation for task TEST.1")
        self.assertTrue(result)
    
    def test_task_completion(self):
        proof = {"test": "pytest passed"}
        result = self.enforcer.complete_task("TEST.1", proof)
        self.assertEqual(result.status, CompletionStatus.APPROVED)
```

### **Integration Testing**
```python
from supermanus.testing import IntegrationTestSuite

# Test all integrations
suite = IntegrationTestSuite()
suite.add_integration_test("claude_code")
suite.add_integration_test("cursor") 
suite.add_integration_test("copilot")

results = suite.run_all_tests()
print(f"Integration tests: {results.summary()}")
```

---

## 🔄 **Event System APIs**

### **Event Handling**
```python
from supermanus.events import EventSystem, Event

events = EventSystem()

# Subscribe to events
@events.on("task.selected")
def handle_task_selection(event: Event):
    print(f"Task selected: {event.data['task_id']}")

@events.on("validation.failed")
def handle_validation_failure(event: Event):
    log_warning(f"Validation failed: {event.data['reason']}")

# Emit custom events
events.emit("custom.event", {
    "message": "Custom event data",
    "timestamp": datetime.now()
})
```

### **Event Types**
```python
# Built-in event types
EVENT_TYPES = [
    "task.selected",           # Task selection
    "task.completed",          # Task completion  
    "task.failed",            # Task completion failed
    "validation.approved",     # Action approved
    "validation.rejected",     # Action rejected
    "validation.pending",      # Requires human review
    "work_log.created",       # Work log created
    "work_log.updated",       # Work log updated
    "session.started",        # Session started
    "session.ended",          # Session ended
    "integration.configured", # Integration setup
    "integration.updated",    # Integration updated
    "error.occurred",         # Error occurred
    "warning.issued"          # Warning issued
]
```

---

## 📚 **Data Models**

### **Core Models**
```python
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

@dataclass
class Task:
    task_id: str
    description: str
    assigned_developer: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    dependencies: List[str]
    priority: int
    estimated_duration: Optional[int]

@dataclass  
class SessionState:
    current_session_id: str
    last_updated: datetime
    project_name: str
    current_phase: str
    active_tasks: List[str]
    completed_tasks: List[str]
    team_assignments: Dict[str, List[str]]
    validation_requirements: Dict[str, Any]

@dataclass
class WorkLogEntry:
    task_id: str
    entry_id: str
    timestamp: datetime
    action: str
    expected_result: str
    actual_result: str
    validation_status: str
    files_modified: List[str]

class ValidationStatus(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"  
    PENDING = "pending"
    BLOCKED = "blocked"

@dataclass
class ValidationResult:
    status: ValidationStatus
    reason: str
    evidence: Optional[Dict] = None
    reviewer: Optional[str] = None
    timestamp: datetime = None
```

---

## 🛠️ **Utility Functions**

### **Helper Functions**
```python
from supermanus.utils import (
    normalize_task_id,
    validate_justification,
    extract_file_paths,
    estimate_task_risk,
    generate_work_log_template,
    parse_proof_package
)

# Task ID normalization  
normalized_id = normalize_task_id("t1.2 implement auth")  # "T1.2: Implement auth"

# Justification validation
is_valid = validate_justification("Short", min_length=20)  # False

# File path extraction
paths = extract_file_paths("Modified src/auth.py and tests/test_auth.py")
# Returns: ["src/auth.py", "tests/test_auth.py"]

# Risk assessment
risk_level = estimate_task_risk("T1.2: Implement security authentication")
# Returns: RiskLevel.HIGH
```

### **Decorators**
```python
from supermanus.decorators import (
    require_active_task,
    require_justification,
    log_action,
    validate_task_alignment
)

@require_active_task
@require_justification(min_length=10)
@log_action
def my_function(action_data: Dict, justification: str):
    """Function automatically protected by SuperManUS"""
    pass

@validate_task_alignment("database")
def database_operation():
    """Only allowed if current task involves database work"""
    pass
```

---

**API Reference Version**: 1.0  
**Last Updated**: 2025-09-04  
**Compatibility**: SuperManUS TaskEnforcer v1.0+