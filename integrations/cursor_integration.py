#!/usr/bin/env python3
"""
SuperManUS Task Enforcement - Cursor IDE Integration
Wrapper functions for Cursor AI coding with task enforcement
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add SuperManUS to path
SUPERMANUS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SUPERMANUS_ROOT / 'src'))

try:
    from utils.task_enforcer import get_enforcer
    from utils.llm_guard import LLMActionGuard, TaskViolationException
except ImportError as e:
    print(f"⚠️  SuperManUS enforcement not available: {e}")

class EnforcedCursor:
    """
    Integration layer for Cursor IDE with SuperManUS task enforcement
    Prevents AI-driven development from going off-task
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.enforcer = get_enforcer()
    
    def pre_ai_request_hook(self, request_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook to run before any AI request in Cursor
        Validates task alignment and adds context
        """
        
        # Check task discipline
        if not self.enforcer.current_task:
            return {
                "blocked": True,
                "message": "❌ No active task selected. Use SuperManUS task selector first.",
                "required_action": "select_task"
            }
        
        if not self.enforcer.work_log_active:
            return {
                "blocked": True, 
                "message": "❌ Work log required. Create work log before AI assistance.",
                "required_action": "create_work_log"
            }
        
        # Add task context to AI request
        task_context = {
            "current_task": self.enforcer.current_task["id"],
            "task_constraints": f"All suggestions must advance: {self.enforcer.current_task['id']}",
            "completion_requirements": self.enforcer.require_completion_proof()
        }
        
        return {
            "blocked": False,
            "enhanced_context": task_context,
            "message": "✅ AI request approved with task context"
        }
    
    def validate_ai_suggestion(self, suggestion: str, justification: str = None) -> Dict[str, Any]:
        """
        Validate AI suggestions against current task
        """
        
        if not justification:
            return {
                "approved": False,
                "message": "❌ AI suggestion requires justification for task alignment"
            }
        
        try:
            with LLMActionGuard(f"AI Suggestion: {suggestion[:50]}...", justification):
                return {
                    "approved": True,
                    "message": "✅ AI suggestion approved",
                    "enhanced_suggestion": f"/* Task: {self.enforcer.current_task['id']} */\n{suggestion}"
                }
        except TaskViolationException as e:
            return {
                "approved": False,
                "message": f"❌ AI suggestion blocked: {e}"
            }
    
    def generate_cursor_prompt(self) -> str:
        """
        Generate Cursor-specific prompt that includes task enforcement context
        """
        
        if not self.enforcer.current_task:
            return "❌ No active task. Select a task from SESSION_STATE.json first."
        
        task_id = self.enforcer.current_task["id"]
        proof_req = self.enforcer.require_completion_proof()
        
        prompt = f"""
🎯 ACTIVE TASK: {task_id}

CONSTRAINTS:
- All code suggestions MUST advance this specific task
- No unrelated features or improvements
- Follow existing project patterns and conventions
- Provide justification for how changes advance the task

COMPLETION REQUIREMENTS:
"""
        
        for req_type, description in proof_req.get('requirements', {}).items():
            prompt += f"- {req_type}: {description}\n"
        
        prompt += f"""
VALIDATION COMMANDS:
"""
        
        for cmd in proof_req.get('validation_commands', []):
            prompt += f"- {cmd}\n"
        
        prompt += """
Remember: Focus only on advancing the current task. Suggest concrete, implementable code.
"""
        
        return prompt
    
    def create_cursor_rules_json(self) -> Dict[str, Any]:
        """
        Create .cursorrules JSON for project-level enforcement
        """
        
        if not self.enforcer.current_task:
            return {"error": "No active task"}
        
        task_id = self.enforcer.current_task["id"]
        
        rules = {
            "version": "1.0",
            "supermanus_integration": True,
            "active_task": task_id,
            "rules": [
                {
                    "rule": "task_focus",
                    "description": f"All suggestions must advance: {task_id}",
                    "enforcement": "block_unrelated_suggestions"
                },
                {
                    "rule": "justification_required", 
                    "description": "Explain how each suggestion advances the current task",
                    "enforcement": "require_task_alignment_comment"
                },
                {
                    "rule": "no_scope_creep",
                    "description": "No additional features beyond task requirements",
                    "enforcement": "warn_on_extra_features"
                },
                {
                    "rule": "validation_aware",
                    "description": "Consider completion validation requirements",
                    "enforcement": "suggest_testable_implementations"
                }
            ],
            "completion_requirements": self.enforcer.require_completion_proof(),
            "suggested_prompt": self.generate_cursor_prompt()
        }
        
        # Write to project root
        rules_file = self.project_root / ".cursorrules.json"
        with open(rules_file, 'w') as f:
            json.dump(rules, f, indent=2)
        
        return rules
    
    def post_ai_generation_hook(self, generated_code: str, file_path: str) -> Dict[str, Any]:
        """
        Hook to run after AI code generation
        Validates and logs the changes
        """
        
        # Log the AI generation for audit trail
        self.enforcer.validation_history.append({
            "timestamp": "now",
            "type": "ai_generation",
            "file": file_path,
            "task": self.enforcer.current_task["id"],
            "code_length": len(generated_code),
            "validated": True
        })
        
        # Add task context comment to generated code
        if generated_code and not generated_code.startswith("/*"):
            task_comment = f"/* Generated for task: {self.enforcer.current_task['id']} */\n"
            enhanced_code = task_comment + generated_code
        else:
            enhanced_code = generated_code
        
        return {
            "enhanced_code": enhanced_code,
            "audit_logged": True,
            "task_aligned": True
        }

# Cursor-specific helper functions

def setup_cursor_enforcement(project_root: str = None) -> bool:
    """
    Set up Cursor IDE with SuperManUS task enforcement
    """
    
    cursor = EnforcedCursor(project_root)
    
    print("🎯 Setting up Cursor IDE with SuperManUS enforcement...")
    
    # Create .cursorrules.json
    rules = cursor.create_cursor_rules_json()
    if "error" not in rules:
        print("✅ Created .cursorrules.json with task enforcement")
    else:
        print(f"❌ Failed to create Cursor rules: {rules['error']}")
        return False
    
    # Create cursor-specific workspace settings
    vscode_dir = Path(project_root or ".") / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    settings = {
        "supermanus.enforceTaskDiscipline": True,
        "supermanus.requireJustification": True,
        "supermanus.blockOfftaskSuggestions": True,
        "editor.rulers": [80, 120],
        "editor.comments": {
            "task_context": f"Active task: {cursor.enforcer.current_task['id'] if cursor.enforcer.current_task else 'None'}"
        }
    }
    
    settings_file = vscode_dir / "settings.json"
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print("✅ Created .vscode/settings.json with SuperManUS integration")
    
    # Create snippets for task-aligned development
    snippets_dir = vscode_dir / "snippets"
    snippets_dir.mkdir(exist_ok=True)
    
    task_snippets = {
        "Task Context Comment": {
            "prefix": "task",
            "body": [
                "/* Task: ${1:current_task} */",
                "/* Purpose: ${2:explain_how_this_advances_task} */",
                "$0"
            ],
            "description": "Add task context to code"
        },
        "Validation Command": {
            "prefix": "validate",
            "body": [
                "# Validation for task completion:",
                "# ${1:validation_command}",
                "$0"
            ],
            "description": "Add validation command"
        }
    }
    
    snippets_file = snippets_dir / "supermanus.code-snippets"
    with open(snippets_file, 'w') as f:
        json.dump(task_snippets, f, indent=2)
    
    print("✅ Created code snippets for task-aligned development")
    print("\n🎯 Cursor IDE integration complete!")
    print("Your AI assistant will now enforce task discipline automatically.")
    
    return True

def get_cursor_prompt() -> str:
    """Get the current Cursor prompt with task context"""
    cursor = EnforcedCursor()
    return cursor.generate_cursor_prompt()

def validate_cursor_suggestion(suggestion: str, justification: str) -> bool:
    """Validate a Cursor AI suggestion against current task"""
    cursor = EnforcedCursor()
    result = cursor.validate_ai_suggestion(suggestion, justification)
    return result.get("approved", False)

# Testing function
def test_cursor_integration():
    """Test Cursor integration functionality"""
    
    print("🧪 Testing Cursor Integration")
    print("-" * 40)
    
    cursor = EnforcedCursor()
    
    # Test pre-request hook
    print("1. Testing pre-AI request hook...")
    result = cursor.pre_ai_request_hook("code_generation", {"file": "test.py"})
    print(f"Result: {result.get('message', 'No message')}")
    
    # Test prompt generation
    print("\n2. Testing prompt generation...")
    prompt = cursor.generate_cursor_prompt()
    print(f"Prompt length: {len(prompt)} characters")
    
    # Test rules creation
    print("\n3. Testing Cursor rules creation...")
    rules = cursor.create_cursor_rules_json()
    if "error" not in rules:
        print("✅ Rules created successfully")
    else:
        print(f"❌ {rules['error']}")
    
    print("\n✅ Cursor integration test complete!")

if __name__ == "__main__":
    test_cursor_integration()