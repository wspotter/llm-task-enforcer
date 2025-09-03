#!/usr/bin/env python3
"""
SuperManUS Task System Enforcer
Prevents LLM deviation from assigned tasks through validation gates
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class TaskRiskLevel(Enum):
    LOW = "low"        # File operations, documentation
    MEDIUM = "medium"  # Code changes, configuration
    HIGH = "high"      # Architecture, security, deployment

class ValidationResult(Enum):
    APPROVED = "approved"
    REJECTED = "rejected" 
    PENDING = "pending_human_review"
    BLOCKED = "blocked"

class TaskSystemEnforcer:
    """
    Enforces strict task discipline for LLM operations
    Prevents deviation and ensures completion validation
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.session_file = self.project_root / "SESSION_STATE.json"
        self.work_log_dir = self.project_root / "work_logs"
        self.work_log_dir.mkdir(exist_ok=True)
        
        self.current_task: Optional[Dict[str, Any]] = None
        self.work_log_active: bool = False
        self.validation_history: List[Dict[str, Any]] = []
        
    def load_session_state(self) -> Dict[str, Any]:
        """Load current session state from file"""
        if not self.session_file.exists():
            raise FileNotFoundError("SESSION_STATE.json not found - project not initialized")
        
        with open(self.session_file, 'r') as f:
            return json.load(f)
    
    def get_active_tasks(self) -> List[str]:
        """Get list of officially active tasks from session state"""
        session = self.load_session_state()
        return session.get("active_tasks", [])
    
    def force_task_selection(self) -> str:
        """Force LLM to select from official active tasks"""
        active_tasks = self.get_active_tasks()
        if not active_tasks:
            return "❌ BLOCKED: No active tasks in SESSION_STATE.json. Update session state first."
        
        task_list = "\n".join([f"  {i+1}. {task}" for i, task in enumerate(active_tasks)])
        
        return f"""
🚨 TASK SELECTION REQUIRED

You must select ONE active task before proceeding:

{task_list}

FORBIDDEN ACTIONS until task selected:
- Creating new tasks
- Using any tools  
- Writing any code
- Making any changes

REQUIRED: Call set_current_task(task_id) with exact task string.
        """
    
    def set_current_task(self, task_id: str) -> ValidationResult:
        """Set current active task with validation"""
        active_tasks = self.get_active_tasks()
        
        if task_id not in active_tasks:
            logger.error(f"Invalid task selection: {task_id}")
            return ValidationResult.BLOCKED
        
        self.current_task = {
            "id": task_id,
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "risk_level": self._assess_task_risk(task_id)
        }
        
        logger.info(f"Task selected: {task_id}")
        return ValidationResult.APPROVED
    
    def _assess_task_risk(self, task_id: str) -> TaskRiskLevel:
        """Assess risk level of task for validation requirements"""
        high_risk_keywords = ["deploy", "security", "auth", "database", "kubernetes", "production"]
        medium_risk_keywords = ["implement", "refactor", "api", "service", "docker"]
        
        task_lower = task_id.lower()
        
        if any(keyword in task_lower for keyword in high_risk_keywords):
            return TaskRiskLevel.HIGH
        elif any(keyword in task_lower for keyword in medium_risk_keywords):
            return TaskRiskLevel.MEDIUM
        else:
            return TaskRiskLevel.LOW
    
    def require_work_log(self) -> str:
        """Force creation of work log before proceeding"""
        if not self.current_task:
            return self.force_task_selection()
        
        if self.work_log_active:
            return "✅ Work log active. Proceed with task."
        
        work_log_file = self.work_log_dir / f"task_{self.current_task['id'].replace(':', '_').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        work_log_template = self._generate_work_log_template()
        
        return f"""
🚨 WORK LOG REQUIRED

Create work log file: {work_log_file}

Template content:
{work_log_template}

FORBIDDEN ACTIONS until work log created:
- Using any tools
- Writing any code  
- Making any changes

REQUIRED: Create the work log file, then call start_work_log().
        """
    
    def _generate_work_log_template(self) -> str:
        """Generate work log template for current task"""
        return f"""# Work Log: {self.current_task['id']}

## Task Information
- **Task ID:** {self.current_task['id']}
- **Start Time:** {self.current_task['start_time']}
- **Risk Level:** {self.current_task['risk_level'].value}
- **Status:** {self.current_task['status']}

## Success Criteria
- [ ] Define clear, measurable completion criteria
- [ ] Identify all deliverables
- [ ] List validation commands

## Work Steps
### Step 1: [Description]
- **Action:**
- **Expected Result:**
- **Actual Result:**
- **Validation Command:**
- **Success:** [ ]

## Completion Proof
- **Test Commands:**
- **Output Evidence:**
- **File Evidence:**
- **Functional Proof:**

## Validation
- [ ] All tests pass
- [ ] Files exist as expected
- [ ] Functionality verified
- [ ] Documentation updated
- [ ] Ready for review

---
*Auto-generated by SuperManUS Task Enforcer*
"""
    
    def start_work_log(self) -> ValidationResult:
        """Activate work log for current task"""
        if not self.current_task:
            return ValidationResult.BLOCKED
        
        self.work_log_active = True
        logger.info(f"Work log activated for task: {self.current_task['id']}")
        return ValidationResult.APPROVED
    
    def validate_action(self, action_description: str, justification: str) -> Tuple[ValidationResult, str]:
        """Validate that an action advances the current task"""
        if not self.current_task:
            return ValidationResult.BLOCKED, self.force_task_selection()
        
        if not self.work_log_active:
            return ValidationResult.BLOCKED, self.require_work_log()
        
        # Log the action for audit trail
        action_log = {
            "timestamp": datetime.now().isoformat(),
            "task_id": self.current_task["id"],
            "action": action_description,
            "justification": justification,
            "status": "proposed"
        }
        
        self.validation_history.append(action_log)
        
        # Validate justification quality
        if len(justification.strip()) < 20:
            return ValidationResult.REJECTED, "❌ Insufficient justification. Explain how this action advances the current task."
        
        task_keywords = self._extract_task_keywords(self.current_task["id"])
        justification_lower = justification.lower()
        
        if not any(keyword in justification_lower for keyword in task_keywords):
            return ValidationResult.REJECTED, f"❌ Justification must explain connection to task: {self.current_task['id']}"
        
        return ValidationResult.APPROVED, "✅ Action approved. Proceed."
    
    def _extract_task_keywords(self, task_id: str) -> List[str]:
        """Extract key terms from task for validation"""
        # Simple keyword extraction - can be enhanced
        words = task_id.lower().replace(":", " ").split()
        return [word for word in words if len(word) > 3]
    
    def require_completion_proof(self) -> Dict[str, Any]:
        """Generate completion requirements based on task risk level"""
        if not self.current_task:
            return {"error": "No active task"}
        
        risk_level = TaskRiskLevel(self.current_task["risk_level"])
        
        base_requirements = {
            "file_evidence": "List all files created/modified with ls -la",
            "functional_test": "Provide command that demonstrates functionality",
            "error_check": "Show no errors in logs or output"
        }
        
        if risk_level == TaskRiskLevel.MEDIUM:
            base_requirements.update({
                "integration_test": "Test integration with existing system",
                "syntax_validation": "Validate syntax of all code changes"
            })
        
        if risk_level == TaskRiskLevel.HIGH:
            base_requirements.update({
                "comprehensive_testing": "Full test suite execution",
                "security_check": "Security implications reviewed",
                "human_review_required": "Human approval needed for completion"
            })
        
        return {
            "task_id": self.current_task["id"],
            "risk_level": risk_level.value,
            "requirements": base_requirements,
            "validation_commands": self._generate_validation_commands()
        }
    
    def _generate_validation_commands(self) -> List[str]:
        """Generate validation commands based on current task"""
        commands = [
            "git status --porcelain  # Check file changes",
            "find . -name '*.py' -exec python -m py_compile {} \\;  # Syntax check",
        ]
        
        task_lower = self.current_task["id"].lower()
        
        if "docker" in task_lower:
            commands.append("docker-compose config --quiet  # Validate Docker config")
        
        if "test" in task_lower:
            commands.append("python -m pytest -v  # Run tests")
        
        if "kubernetes" in task_lower or "k8s" in task_lower:
            commands.append("kubectl apply --dry-run=client --validate=true -f k8s/  # Validate K8s")
        
        return commands
    
    def validate_completion(self, proof_data: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate task completion with provided proof"""
        if not self.current_task:
            return ValidationResult.BLOCKED, "No active task to complete"
        
        requirements = self.require_completion_proof()["requirements"]
        
        # Check all requirements are addressed
        missing_proof = []
        for req_key, req_desc in requirements.items():
            if req_key not in proof_data or not proof_data[req_key]:
                missing_proof.append(req_desc)
        
        if missing_proof:
            return ValidationResult.REJECTED, f"❌ Missing proof for: {', '.join(missing_proof)}"
        
        # For HIGH risk tasks, require human approval
        risk_level = TaskRiskLevel(self.current_task["risk_level"])
        if risk_level == TaskRiskLevel.HIGH:
            return ValidationResult.PENDING, "⏳ High-risk task requires human approval"
        
        # Auto-approve LOW and MEDIUM risk with complete proof
        self._mark_task_complete()
        return ValidationResult.APPROVED, "✅ Task completion validated and approved"
    
    def _mark_task_complete(self):
        """Mark current task as complete in session state"""
        session = self.load_session_state()
        
        # Move from active to completed
        if self.current_task["id"] in session.get("active_tasks", []):
            session["active_tasks"].remove(self.current_task["id"])
            session.setdefault("completed_tasks", []).append(self.current_task["id"])
        
        # Update session file
        with open(self.session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        # Reset current task
        self.current_task = None
        self.work_log_active = False
        
        logger.info("Task completed and session state updated")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current enforcer status"""
        return {
            "current_task": self.current_task,
            "work_log_active": self.work_log_active,
            "active_tasks_available": len(self.get_active_tasks()),
            "validation_history_count": len(self.validation_history)
        }

# Global enforcer instance
_enforcer_instance: Optional[TaskSystemEnforcer] = None

def get_enforcer() -> TaskSystemEnforcer:
    """Get global task enforcer instance"""
    global _enforcer_instance
    if _enforcer_instance is None:
        _enforcer_instance = TaskSystemEnforcer()
    return _enforcer_instance

# Convenience functions for LLM integration
def enforce_task_discipline() -> str:
    """Main enforcement check - call before any action"""
    enforcer = get_enforcer()
    
    if not enforcer.current_task:
        return enforcer.force_task_selection()
    
    if not enforcer.work_log_active:
        return enforcer.require_work_log()
    
    return "✅ Task discipline maintained. Proceed with work."

def validate_llm_action(action: str, justification: str) -> Tuple[bool, str]:
    """Validate LLM action against current task"""
    enforcer = get_enforcer()
    result, message = enforcer.validate_action(action, justification)
    return result == ValidationResult.APPROVED, message

def require_completion_proof() -> Dict[str, Any]:
    """Get completion requirements for current task"""
    enforcer = get_enforcer()
    return enforcer.require_completion_proof()