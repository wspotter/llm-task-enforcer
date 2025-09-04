#!/usr/bin/env python3
"""
Unit tests for TaskSystemEnforcer
Tests core enforcement logic and task management
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from task_enforcer import TaskSystemEnforcer
from llm_guard import LLMGuard


class TestTaskSystemEnforcer:
    """Test cases for TaskSystemEnforcer class"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.session_state_path = os.path.join(self.temp_dir, "SESSION_STATE.json")
        self.work_log_dir = os.path.join(self.temp_dir, "work_logs")
        
        # Create work logs directory
        os.makedirs(self.work_log_dir, exist_ok=True)
        
        # Create test session state
        self.test_session_state = {
            "current_session_id": "TEST_001",
            "last_updated": "2025-09-04T10:00:00Z",
            "project_name": "Test Project",
            "current_phase": "testing",
            "active_tasks": [
                "T1.1: Implement user authentication",
                "T1.2: Create user dashboard", 
                "T2.1: Add task management features",
                "BUGFIX.1: Fix memory leak in rendering"
            ],
            "completed_tasks": [
                "SETUP.1: Initialize project structure"
            ],
            "team_assignments": {
                "test_developer": ["T1.1", "T1.2"],
                "other_developer": ["T2.1", "BUGFIX.1"]
            },
            "validation_requirements": {
                "all_tasks": {
                    "work_log_required": True,
                    "proof_required": True
                }
            }
        }
        
        # Write test session state
        with open(self.session_state_path, 'w') as f:
            json.dump(self.test_session_state, f, indent=2)
        
        # Initialize enforcer
        self.enforcer = TaskSystemEnforcer(
            session_state_path=self.session_state_path,
            work_log_dir=self.work_log_dir
        )
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test TaskSystemEnforcer initialization"""
        assert self.enforcer.session_state_path == self.session_state_path
        assert self.enforcer.work_log_dir == self.work_log_dir
        assert self.enforcer.current_task is None
        assert self.enforcer.session_data is not None
    
    def test_load_session_state(self):
        """Test loading session state from file"""
        session_data = self.enforcer._load_session_state()
        
        assert session_data["current_session_id"] == "TEST_001"
        assert session_data["project_name"] == "Test Project"
        assert len(session_data["active_tasks"]) == 4
        assert "T1.1: Implement user authentication" in session_data["active_tasks"]
    
    def test_get_active_tasks(self):
        """Test getting active tasks"""
        active_tasks = self.enforcer.get_active_tasks()
        
        assert len(active_tasks) == 4
        assert "T1.1: Implement user authentication" in active_tasks
        assert "T1.2: Create user dashboard" in active_tasks
    
    def test_select_valid_task(self):
        """Test selecting a valid task from active tasks"""
        task_id = "T1.1: Implement user authentication"
        result = self.enforcer.select_task(task_id)
        
        assert result is True
        assert self.enforcer.current_task == task_id
    
    def test_select_invalid_task(self):
        """Test selecting a task not in active tasks"""
        with pytest.raises(Exception) as excinfo:
            self.enforcer.select_task("INVALID.1: Nonexistent task")
        
        assert "not in active_tasks" in str(excinfo.value)
        assert self.enforcer.current_task is None
    
    def test_select_empty_task(self):
        """Test selecting empty or None task"""
        with pytest.raises(Exception):
            self.enforcer.select_task("")
        
        with pytest.raises(Exception):
            self.enforcer.select_task(None)
    
    def test_task_validation_with_active_task(self):
        """Test task validation when task is active"""
        # Select a task first
        self.enforcer.select_task("T1.1: Implement user authentication")
        
        # Valid justification
        result = self.enforcer.validate_task_action(
            "Create OAuth configuration",
            "Setting up OAuth authentication as required by T1.1"
        )
        assert result is True
        
        # Valid justification with task ID
        result = self.enforcer.validate_task_action(
            "Add login endpoint", 
            "Implementing login functionality for task T1.1"
        )
        assert result is True
    
    def test_task_validation_without_active_task(self):
        """Test task validation when no task is active"""
        with pytest.raises(Exception) as excinfo:
            self.enforcer.validate_task_action(
                "Random action",
                "Some justification"
            )
        
        assert "No active task selected" in str(excinfo.value)
    
    def test_task_validation_with_poor_justification(self):
        """Test task validation with insufficient justification"""
        self.enforcer.select_task("T1.1: Implement user authentication")
        
        # Too short
        with pytest.raises(Exception):
            self.enforcer.validate_task_action("Action", "Short")
        
        # Unrelated to task
        with pytest.raises(Exception):
            self.enforcer.validate_task_action(
                "Add fancy animations",
                "Making the UI look cooler with animations"
            )
    
    def test_work_log_requirement(self):
        """Test work log requirement enforcement"""
        self.enforcer.select_task("T1.1: Implement user authentication")
        
        # Should require work log when none exists
        requires_log = self.enforcer.requires_work_log()
        assert requires_log is True
        
        # Create work log file
        work_log_path = os.path.join(
            self.work_log_dir, 
            "task_T1_1_authentication.md"
        )
        with open(work_log_path, 'w') as f:
            f.write("# Work Log for T1.1\nTask started\n")
        
        # Should not require work log when it exists
        requires_log = self.enforcer.requires_work_log()
        assert requires_log is False
    
    def test_update_session_state(self):
        """Test updating session state"""
        # Add completed task
        self.enforcer.update_session_state({
            "completed_tasks": ["SETUP.1: Initialize project structure", "T1.1: Implement user authentication"]
        })
        
        # Verify update
        updated_state = self.enforcer._load_session_state()
        assert len(updated_state["completed_tasks"]) == 2
        assert "T1.1: Implement user authentication" in updated_state["completed_tasks"]
    
    def test_task_completion_validation(self):
        """Test task completion with proof validation"""
        self.enforcer.select_task("T1.1: Implement user authentication")
        
        # Valid proof package
        proof_package = {
            "file_evidence": "auth.py created with 150 lines",
            "functional_test": "pytest tests/test_auth.py - 5 tests passed", 
            "integration_test": "curl localhost:8000/auth/login - 200 OK"
        }
        
        # Mock validation methods
        with patch.object(self.enforcer, '_validate_proof_package', return_value=True):
            result = self.enforcer.complete_task("T1.1: Implement user authentication", proof_package)
            assert result is True
    
    def test_task_completion_without_proof(self):
        """Test task completion without sufficient proof"""
        self.enforcer.select_task("T1.1: Implement user authentication")
        
        # Insufficient proof
        weak_proof = {
            "claim": "It works"
        }
        
        with pytest.raises(Exception) as excinfo:
            self.enforcer.complete_task("T1.1: Implement user authentication", weak_proof)
        
        assert "insufficient proof" in str(excinfo.value).lower()
    
    def test_multiple_task_selection(self):
        """Test selecting multiple tasks in sequence"""
        # Select first task
        self.enforcer.select_task("T1.1: Implement user authentication")
        assert self.enforcer.current_task == "T1.1: Implement user authentication"
        
        # Select second task
        self.enforcer.select_task("T1.2: Create user dashboard")  
        assert self.enforcer.current_task == "T1.2: Create user dashboard"
        
        # First task should no longer be current
        assert self.enforcer.current_task != "T1.1: Implement user authentication"
    
    def test_team_assignment_validation(self):
        """Test validation against team assignments"""
        # Test with assigned developer
        with patch('os.getlogin', return_value='test_developer'):
            self.enforcer.select_task("T1.1: Implement user authentication")
            # Should work - task is assigned to test_developer
        
        # Test with unassigned developer  
        with patch('os.getlogin', return_value='unassigned_developer'):
            # Should still work in current implementation
            # (Team assignment is informational, not restrictive)
            self.enforcer.select_task("T1.1: Implement user authentication")
    
    def test_error_handling_missing_session_file(self):
        """Test error handling when session state file is missing"""
        # Remove session state file
        os.remove(self.session_state_path)
        
        with pytest.raises(FileNotFoundError):
            TaskSystemEnforcer(session_state_path=self.session_state_path)
    
    def test_error_handling_corrupted_session_file(self):
        """Test error handling when session state file is corrupted"""
        # Write invalid JSON
        with open(self.session_state_path, 'w') as f:
            f.write("invalid json content {")
        
        with pytest.raises(json.JSONDecodeError):
            TaskSystemEnforcer(session_state_path=self.session_state_path)
    
    def test_justification_keyword_matching(self):
        """Test justification validation with keyword matching"""
        self.enforcer.select_task("T1.1: Implement user authentication")
        
        # Should pass - contains task-related keywords
        valid_justifications = [
            "Implementing OAuth authentication for user login as required by T1.1",
            "Adding authentication middleware to secure endpoints for current task",
            "Creating user authentication flow using JWT tokens for task T1.1"
        ]
        
        for justification in valid_justifications:
            result = self.enforcer.validate_task_action("Auth work", justification)
            assert result is True
        
        # Should fail - unrelated to authentication task
        invalid_justifications = [
            "Adding fancy CSS animations to make UI prettier",
            "Optimizing database queries for better performance", 
            "Refactoring file structure for better organization"
        ]
        
        for justification in invalid_justifications:
            with pytest.raises(Exception):
                self.enforcer.validate_task_action("Unrelated work", justification)


class TestTaskEnforcerIntegration:
    """Integration tests for TaskSystemEnforcer with other components"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_state_path = os.path.join(self.temp_dir, "SESSION_STATE.json")
        self.work_log_dir = os.path.join(self.temp_dir, "work_logs")
        
        os.makedirs(self.work_log_dir, exist_ok=True)
        
        # Minimal session state for integration tests
        session_state = {
            "active_tasks": ["INT.1: Integration test task"],
            "completed_tasks": [],
            "team_assignments": {"test_dev": ["INT.1: Integration test task"]}
        }
        
        with open(self.session_state_path, 'w') as f:
            json.dump(session_state, f)
        
        self.enforcer = TaskSystemEnforcer(
            session_state_path=self.session_state_path,
            work_log_dir=self.work_log_dir
        )
    
    def teardown_method(self):
        """Cleanup integration test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_llm_guard_integration(self):
        """Test TaskSystemEnforcer integration with LLMGuard"""
        guard = LLMGuard(self.enforcer)
        
        # Should require task selection
        with pytest.raises(Exception):
            guard.validate_action("write_file", {"path": "test.py"}, "Test justification")
        
        # Select task and try again
        self.enforcer.select_task("INT.1: Integration test task")
        
        # Should work with valid justification
        result = guard.validate_action(
            "write_file", 
            {"path": "integration_test.py"}, 
            "Creating integration test file as required by INT.1"
        )
        assert result is True
    
    def test_work_log_integration(self):
        """Test work log creation and validation integration"""
        self.enforcer.select_task("INT.1: Integration test task")
        
        # Should require work log initially
        assert self.enforcer.requires_work_log() is True
        
        # Create work log
        work_log_content = """
# Work Log for INT.1: Integration test task

## Task Information
- Task ID: INT.1
- Description: Integration test task
- Start Time: 2025-09-04T10:00:00Z

## Work Performed
### Step 1: Setup test environment
- Command: mkdir test_env
- Expected: Directory created
- Actual: Directory created successfully
- Validation: ls -la test_env
"""
        
        work_log_path = os.path.join(self.work_log_dir, "integration_test.md")
        with open(work_log_path, 'w') as f:
            f.write(work_log_content)
        
        # Should no longer require work log
        assert self.enforcer.requires_work_log() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])