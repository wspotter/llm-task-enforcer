#!/usr/bin/env python3
"""
SuperManUS Task Enforcement - Claude Code Integration
Wrapper functions that add task enforcement to Claude Code workflows
"""

import os
import sys
import functools
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

# Add SuperManUS to path
SUPERMANUS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SUPERMANUS_ROOT / 'src'))

try:
    from utils.task_enforcer import get_enforcer, ValidationResult
    from utils.llm_guard import LLMActionGuard, TaskViolationException, validate_file_creation
except ImportError as e:
    print(f"⚠️  SuperManUS enforcement not available: {e}")
    print("Install SuperManUS task enforcer first")

class EnforcedClaudeCode:
    """
    Wrapper for Claude Code operations with task enforcement
    Use this instead of direct tool calls to maintain task discipline
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.enforcer = get_enforcer()
    
    def require_task_justification(func):
        """Decorator requiring task justification for Claude Code operations"""
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Extract justification from kwargs
            justification = kwargs.pop('justification', None)
            if not justification:
                raise TaskViolationException(
                    f"❌ {func.__name__} requires justification parameter: "
                    f"Explain how this operation advances the current task"
                )
            
            # Use LLMActionGuard for validation
            action_desc = f"Claude Code: {func.__name__}"
            with LLMActionGuard(action_desc, justification):
                return func(self, *args, **kwargs)
        
        return wrapper
    
    @require_task_justification
    def read_file(self, file_path: str, **kwargs) -> str:
        """Read file with task enforcement"""
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        print(f"📖 Read file: {file_path} ({len(content)} chars)")
        return content
    
    @require_task_justification  
    def write_file(self, file_path: str, content: str, **kwargs) -> bool:
        """Write file with task enforcement"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✍️  Wrote file: {file_path} ({len(content)} chars)")
        return True
    
    @require_task_justification
    def edit_file(self, file_path: str, old_text: str, new_text: str, **kwargs) -> bool:
        """Edit file with task enforcement"""
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        if old_text not in content:
            raise ValueError(f"Text not found in file: {old_text[:50]}...")
        
        new_content = content.replace(old_text, new_text)
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print(f"✏️  Edited file: {file_path}")
        return True
    
    @require_task_justification
    def run_bash(self, command: str, timeout: int = 30, **kwargs) -> Dict[str, Any]:
        """Run bash command with task enforcement"""
        print(f"🔧 Running: {command}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=self.project_root
            )
            
            output = {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            print(f"✅ Command {'succeeded' if output['success'] else 'failed'}")
            return output
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Command timed out after {timeout}s")
            return {'returncode': -1, 'stdout': '', 'stderr': 'Timeout', 'success': False}
    
    @require_task_justification
    def search_files(self, pattern: str, file_glob: str = "**/*", **kwargs) -> List[Dict[str, Any]]:
        """Search files with task enforcement"""
        import re
        
        matches = []
        for file_path in self.project_root.glob(file_glob):
            if file_path.is_file():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    for line_num, line in enumerate(content.split('\n'), 1):
                        if re.search(pattern, line):
                            matches.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': line_num,
                                'content': line.strip()
                            })
                except:
                    continue  # Skip binary files
        
        print(f"🔍 Found {len(matches)} matches for '{pattern}'")
        return matches
    
    @require_task_justification
    def git_operations(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Git operations with task enforcement"""
        git_commands = {
            'status': 'git status --porcelain',
            'diff': 'git diff',
            'add': 'git add .',
            'commit': 'git commit -m "Task progress commit"',
            'log': 'git log --oneline -10'
        }
        
        if operation not in git_commands:
            raise ValueError(f"Unsupported git operation: {operation}")
        
        return self.run_bash(git_commands[operation], **kwargs)
    
    def get_task_context(self) -> Dict[str, Any]:
        """Get current task context for LLM reference"""
        if not self.enforcer.current_task:
            return {"error": "No active task - select one first"}
        
        return {
            "current_task": self.enforcer.current_task,
            "completion_requirements": self.enforcer.require_completion_proof(),
            "work_log_active": self.enforcer.work_log_active,
            "status": "ready" if self.enforcer.work_log_active else "need_work_log"
        }
    
    def validate_completion(self, proof_package: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task completion with comprehensive proof"""
        return {
            "validation_result": self.enforcer.validate_completion(proof_package),
            "requirements_met": self._check_proof_completeness(proof_package)
        }
    
    def _check_proof_completeness(self, proof: Dict[str, Any]) -> Dict[str, bool]:
        """Check if proof package meets requirements"""
        requirements = self.enforcer.require_completion_proof().get('requirements', {})
        
        completeness = {}
        for req_key in requirements:
            completeness[req_key] = bool(proof.get(req_key))
        
        return completeness

# Global instance for easy access
_claude_code = None

def get_enforced_claude_code(project_root: str = None) -> EnforcedClaudeCode:
    """Get global enforced Claude Code instance"""
    global _claude_code
    if _claude_code is None:
        _claude_code = EnforcedClaudeCode(project_root)
    return _claude_code

# Convenience functions that mimic Claude Code tools but with enforcement

def enforced_read(file_path: str, justification: str) -> str:
    """Read file with task enforcement - direct replacement for Read tool"""
    cc = get_enforced_claude_code()
    return cc.read_file(file_path, justification=justification)

def enforced_write(file_path: str, content: str, justification: str) -> bool:
    """Write file with task enforcement - direct replacement for Write tool"""
    cc = get_enforced_claude_code()
    return cc.write_file(file_path, content, justification=justification)

def enforced_edit(file_path: str, old_text: str, new_text: str, justification: str) -> bool:
    """Edit file with task enforcement - direct replacement for Edit tool"""
    cc = get_enforced_claude_code()
    return cc.edit_file(file_path, old_text, new_text, justification=justification)

def enforced_bash(command: str, justification: str, timeout: int = 30) -> Dict[str, Any]:
    """Run bash with task enforcement - direct replacement for Bash tool"""
    cc = get_enforced_claude_code()
    return cc.run_bash(command, timeout=timeout, justification=justification)

def enforced_search(pattern: str, justification: str, file_glob: str = "**/*") -> List[Dict[str, Any]]:
    """Search files with task enforcement - direct replacement for Grep tool"""
    cc = get_enforced_claude_code()
    return cc.search_files(pattern, file_glob, justification=justification)

def enforced_git(operation: str, justification: str) -> Dict[str, Any]:
    """Git operations with task enforcement"""
    cc = get_enforced_claude_code()
    return cc.git_operations(operation, justification=justification)

# Task management functions

def select_task(task_id: str) -> bool:
    """Select official task from SESSION_STATE.json"""
    enforcer = get_enforcer()
    result = enforcer.set_current_task(task_id)
    return result == ValidationResult.APPROVED

def start_work_log() -> bool:
    """Start work log for current task"""
    enforcer = get_enforcer()
    result = enforcer.start_work_log()
    return result == ValidationResult.APPROVED

def get_task_status() -> Dict[str, Any]:
    """Get current task and enforcement status"""
    cc = get_enforced_claude_code()
    return cc.get_task_context()

def complete_task(proof_package: Dict[str, Any]) -> Dict[str, Any]:
    """Complete current task with proof validation"""
    cc = get_enforced_claude_code()
    return cc.validate_completion(proof_package)

# Integration testing
def test_integration():
    """Test the integration with sample operations"""
    print("🧪 Testing SuperManUS-Claude Code Integration")
    print("-" * 50)
    
    try:
        # Test without task selection
        print("1. Testing action without task...")
        cc = get_enforced_claude_code()
        cc.read_file("README.md", justification="Just checking")
        print("❌ Should have been blocked!")
    except TaskViolationException as e:
        print("✅ Correctly blocked:", str(e)[:60])
    
    try:
        # Test task selection
        print("\n2. Testing task selection...")
        enforcer = get_enforcer()
        tasks = enforcer.get_active_tasks()
        if tasks:
            result = select_task(tasks[0])
            print(f"✅ Task selection: {result}")
        
        # Test work log requirement
        print("\n3. Testing work log requirement...")
        cc.read_file("SESSION_STATE.json", justification="Check task status")
        print("❌ Should require work log!")
    except TaskViolationException as e:
        print("✅ Correctly requires work log:", str(e)[:60])
    
    print("\n🎯 Integration test complete!")

if __name__ == "__main__":
    test_integration()