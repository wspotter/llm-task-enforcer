#!/usr/bin/env python3
"""
SuperManUS LLM Guard System
Real-time enforcement of task discipline and prevention of LLM deviation
"""

import functools
import logging
from typing import Any, Callable, Dict, Tuple, Optional
from .task_enforcer import get_enforcer, ValidationResult

logger = logging.getLogger(__name__)

class LLMGuardException(Exception):
    """Exception raised when LLM attempts unauthorized actions"""
    pass

class TaskViolationException(LLMGuardException):
    """Exception raised when LLM deviates from assigned task"""
    pass

class ProofRequiredException(LLMGuardException):
    """Exception raised when LLM claims completion without proof"""
    pass

def require_active_task(func: Callable) -> Callable:
    """Decorator that blocks function execution without an active task"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        enforcer = get_enforcer()
        
        if not enforcer.current_task:
            raise TaskViolationException(
                "❌ BLOCKED: No active task selected. "
                "Call set_current_task() first with official task from SESSION_STATE.json"
            )
        
        if not enforcer.work_log_active:
            raise TaskViolationException(
                "❌ BLOCKED: Work log required. "
                "Create work log using template and call start_work_log()"
            )
        
        return func(*args, **kwargs)
    
    return wrapper

def require_task_justification(action_description: str):
    """Decorator that requires justification for how action advances current task"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Look for justification in kwargs
            justification = kwargs.get('justification', '')
            
            if not justification:
                raise TaskViolationException(
                    f"❌ BLOCKED: Action '{action_description}' requires justification. "
                    f"Add justification='...' parameter explaining how this advances current task."
                )
            
            enforcer = get_enforcer()
            result, message = enforcer.validate_action(action_description, justification)
            
            if result != ValidationResult.APPROVED:
                raise TaskViolationException(f"❌ Action blocked: {message}")
            
            # Remove justification from kwargs before calling function
            kwargs.pop('justification', None)
            
            logger.info(f"Action approved: {action_description}")
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_completion_proof(func: Callable) -> Callable:
    """Decorator that blocks completion claims without comprehensive proof"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        proof_data = kwargs.get('proof_data', {})
        
        if not proof_data:
            raise ProofRequiredException(
                "❌ BLOCKED: Task completion requires proof_data parameter with comprehensive evidence"
            )
        
        enforcer = get_enforcer()
        result, message = enforcer.validate_completion(proof_data)
        
        if result == ValidationResult.REJECTED:
            raise ProofRequiredException(f"❌ Completion proof insufficient: {message}")
        
        if result == ValidationResult.PENDING:
            logger.warning(f"Completion pending human review: {message}")
            return {"status": "pending_human_review", "message": message}
        
        logger.info("Task completion validated")
        return func(*args, **kwargs)
    
    return wrapper

class LLMActionGuard:
    """Context manager that enforces task discipline during LLM operations"""
    
    def __init__(self, action_description: str, justification: str):
        self.action_description = action_description
        self.justification = justification
        self.enforcer = get_enforcer()
        
    def __enter__(self):
        """Validate action before allowing execution"""
        if not self.enforcer.current_task:
            raise TaskViolationException(self.enforcer.force_task_selection())
        
        if not self.enforcer.work_log_active:
            raise TaskViolationException(self.enforcer.require_work_log())
        
        result, message = self.enforcer.validate_action(
            self.action_description, 
            self.justification
        )
        
        if result != ValidationResult.APPROVED:
            raise TaskViolationException(f"❌ {message}")
        
        logger.info(f"Guarded action started: {self.action_description}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log completion of guarded action"""
        if exc_type is None:
            logger.info(f"Guarded action completed: {self.action_description}")
        else:
            logger.error(f"Guarded action failed: {self.action_description} - {exc_val}")
        
        return False  # Don't suppress exceptions

# Convenience functions for common LLM operations

def guard_file_operation(operation: str, filepath: str, justification: str):
    """Guard file operations with task validation"""
    return LLMActionGuard(
        f"File operation: {operation} on {filepath}",
        justification
    )

def guard_code_change(module: str, change_description: str, justification: str):
    """Guard code modifications with task validation"""
    return LLMActionGuard(
        f"Code change: {change_description} in {module}",
        justification
    )

def guard_tool_usage(tool_name: str, purpose: str, justification: str):
    """Guard tool usage with task validation"""
    return LLMActionGuard(
        f"Tool usage: {tool_name} for {purpose}",
        justification
    )

# Pre-built validation functions for common scenarios

def validate_file_creation(filepath: str, purpose: str, justification: str) -> bool:
    """Validate file creation against current task"""
    try:
        with guard_file_operation("create", filepath, justification):
            return True
    except TaskViolationException:
        return False

def validate_code_modification(module: str, changes: str, justification: str) -> bool:
    """Validate code modifications against current task"""  
    try:
        with guard_code_change(module, changes, justification):
            return True
    except TaskViolationException:
        return False

# Task enforcement utilities

def check_task_discipline() -> Tuple[bool, str]:
    """Check if LLM is maintaining proper task discipline"""
    try:
        enforcer = get_enforcer()
        
        if not enforcer.current_task:
            return False, enforcer.force_task_selection()
        
        if not enforcer.work_log_active:
            return False, enforcer.require_work_log()
        
        return True, "✅ Task discipline maintained"
    
    except Exception as e:
        return False, f"❌ Task discipline check failed: {e}"

def get_current_task_context() -> Dict[str, Any]:
    """Get current task context for LLM reference"""
    enforcer = get_enforcer()
    
    if not enforcer.current_task:
        return {"error": "No active task"}
    
    return {
        "current_task": enforcer.current_task,
        "completion_requirements": enforcer.require_completion_proof(),
        "validation_history_count": len(enforcer.validation_history),
        "work_log_active": enforcer.work_log_active
    }

def enforce_completion_standards(proof_package: Dict[str, Any]) -> Dict[str, Any]:
    """Enforce completion standards with proof validation"""
    enforcer = get_enforcer()
    
    if not enforcer.current_task:
        return {"error": "No active task to complete"}
    
    result, message = enforcer.validate_completion(proof_package)
    
    return {
        "validation_result": result.value,
        "message": message,
        "requires_human_review": result == ValidationResult.PENDING,
        "approved": result == ValidationResult.APPROVED
    }

# Integration hooks for external systems

def hook_git_operations(justification: str = None):
    """Hook for git operations requiring task validation"""
    if not justification:
        raise TaskViolationException(
            "❌ Git operations require justification parameter: "
            "Explain how this git operation advances the current task"
        )
    
    return guard_tool_usage("git", "version control", justification)

def hook_docker_operations(justification: str = None):
    """Hook for Docker operations requiring task validation"""
    if not justification:
        raise TaskViolationException(
            "❌ Docker operations require justification parameter: "
            "Explain how this Docker operation advances the current task"
        )
    
    return guard_tool_usage("docker", "containerization", justification)

def hook_test_execution(justification: str = None):
    """Hook for test execution requiring task validation"""
    if not justification:
        raise TaskViolationException(
            "❌ Test execution requires justification parameter: "
            "Explain how running tests advances the current task"
        )
    
    return guard_tool_usage("pytest", "testing", justification)

# Emergency controls

def emergency_unlock() -> str:
    """Emergency unlock for human intervention"""
    logger.warning("EMERGENCY UNLOCK ACTIVATED - Human intervention required")
    return """
🚨 EMERGENCY UNLOCK ACTIVATED

This bypasses normal task enforcement.
Use only for:
- Critical system recovery
- Emergency bug fixes  
- Human-supervised operations

Normal task discipline will resume after human confirmation.
"""

def reset_task_state() -> str:
    """Reset task enforcer state - use with caution"""
    global _enforcer_instance
    _enforcer_instance = None
    logger.warning("Task enforcer state reset")
    return "⚠️ Task state reset. Must select new task before proceeding."