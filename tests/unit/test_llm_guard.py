#!/usr/bin/env python3
"""
Unit tests for LLMGuard
Tests the LLM action guarding and validation logic
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from llm_guard import LLMGuard
from task_enforcer import TaskSystemEnforcer


class TestLLMGuard:
    """Test cases for LLMGuard class"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create mock enforcer
        self.mock_enforcer = Mock(spec=TaskSystemEnforcer)
        self.mock_enforcer.current_task = None
        self.mock_enforcer.session_data = {
            "active_tasks": ["T1.1: Test task"],
            "validation_requirements": {"all_tasks": {"work_log_required": True}}
        }
        
        # Initialize LLMGuard
        self.guard = LLMGuard(self.mock_enforcer)
    
    def test_initialization(self):
        """Test LLMGuard initialization"""
        assert self.guard.enforcer == self.mock_enforcer
        assert hasattr(self.guard, 'action_validators')
        assert hasattr(self.guard, 'blocked_patterns')
    
    def test_validate_action_without_task(self):
        """Test action validation when no task is selected"""
        self.mock_enforcer.current_task = None
        
        with pytest.raises(Exception) as excinfo:
            self.guard.validate_action(
                "write_file",
                {"path": "test.py", "content": "print('hello')"},
                "Creating test file"
            )
        
        assert "no active task" in str(excinfo.value).lower()
    
    def test_validate_action_with_task(self):
        """Test action validation with active task"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        self.mock_enforcer.validate_task_action.return_value = True
        
        result = self.guard.validate_action(
            "write_file",
            {"path": "test.py", "content": "print('hello')"},
            "Creating test file for T1.1 implementation"
        )
        
        assert result is True
        self.mock_enforcer.validate_task_action.assert_called_once()
    
    def test_validate_action_with_invalid_justification(self):
        """Test action validation with invalid justification"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        self.mock_enforcer.validate_task_action.side_effect = Exception("Invalid justification")
        
        with pytest.raises(Exception) as excinfo:
            self.guard.validate_action(
                "write_file",
                {"path": "test.py"},
                "Invalid justification"
            )
        
        assert "Invalid justification" in str(excinfo.value)
    
    def test_blocked_action_patterns(self):
        """Test blocking of dangerous action patterns"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        
        # Test blocked command patterns
        dangerous_commands = [
            "rm -rf /",
            "sudo rm -rf /home",
            "dd if=/dev/zero of=/dev/sda",
            ":(){ :|:& };:",  # Fork bomb
            "chmod 777 / -R"
        ]
        
        for cmd in dangerous_commands:
            with pytest.raises(Exception) as excinfo:
                self.guard.validate_action(
                    "run_command",
                    {"command": cmd},
                    "Running system command for T1.1"
                )
            
            assert "blocked" in str(excinfo.value).lower()
    
    def test_file_operation_validation(self):
        """Test file operation specific validation"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        self.mock_enforcer.validate_task_action.return_value = True
        
        # Valid file operations
        valid_operations = [
            {"action": "read_file", "data": {"path": "src/config.py"}},
            {"action": "write_file", "data": {"path": "src/new_feature.py", "content": "code"}},
            {"action": "edit_file", "data": {"path": "src/existing.py", "changes": "updates"}}
        ]
        
        for op in valid_operations:
            result = self.guard.validate_action(
                op["action"],
                op["data"],
                f"File operation for task T1.1: {op['action']}"
            )
            assert result is True
    
    def test_sensitive_file_protection(self):
        """Test protection of sensitive files"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        
        # Sensitive files that should require extra validation
        sensitive_files = [
            "/etc/passwd",
            "/etc/shadow", 
            "~/.ssh/id_rsa",
            ".env",
            "secrets.json",
            "config/database.yml"
        ]
        
        for file_path in sensitive_files:
            with pytest.raises(Exception):
                self.guard.validate_action(
                    "write_file",
                    {"path": file_path, "content": "malicious content"},
                    "Modifying configuration for T1.1"
                )
    
    def test_work_log_requirement_enforcement(self):
        """Test enforcement of work log requirements"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        self.mock_enforcer.requires_work_log.return_value = True
        self.mock_enforcer.validate_task_action.return_value = True
        
        with pytest.raises(Exception) as excinfo:
            self.guard.validate_action(
                "write_file",
                {"path": "feature.py", "content": "code"},
                "Implementing feature for T1.1"
            )
        
        assert "work log required" in str(excinfo.value).lower()
    
    def test_work_log_requirement_satisfied(self):
        """Test action approval when work log requirement is satisfied"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        self.mock_enforcer.requires_work_log.return_value = False
        self.mock_enforcer.validate_task_action.return_value = True
        
        result = self.guard.validate_action(
            "write_file",
            {"path": "feature.py", "content": "code"},
            "Implementing feature for T1.1 as documented in work log"
        )
        
        assert result is True
    
    def test_action_logging(self):
        """Test that actions are properly logged"""
        self.mock_enforcer.current_task = "T1.1: Test task" 
        self.mock_enforcer.requires_work_log.return_value = False
        self.mock_enforcer.validate_task_action.return_value = True
        
        with patch('builtins.print') as mock_print:
            self.guard.validate_action(
                "write_file",
                {"path": "test.py"},
                "Creating test file for T1.1"
            )
            
            # Check that action was logged
            assert mock_print.called
    
    def test_context_validation(self):
        """Test validation with additional context"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        self.mock_enforcer.requires_work_log.return_value = False
        self.mock_enforcer.validate_task_action.return_value = True
        
        context = {
            "developer": "test_dev",
            "timestamp": datetime.now().isoformat(),
            "session_id": "TEST_001"
        }
        
        result = self.guard.validate_action(
            "write_file",
            {"path": "feature.py", "context": context},
            "Implementing feature for T1.1 with full context"
        )
        
        assert result is True
    
    def test_bulk_action_validation(self):
        """Test validation of multiple actions"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        self.mock_enforcer.requires_work_log.return_value = False
        self.mock_enforcer.validate_task_action.return_value = True
        
        actions = [
            {"action": "read_file", "data": {"path": "config.py"}},
            {"action": "write_file", "data": {"path": "feature.py", "content": "code"}},
            {"action": "run_test", "data": {"test_path": "tests/test_feature.py"}}
        ]
        
        for action_data in actions:
            result = self.guard.validate_action(
                action_data["action"],
                action_data["data"],
                f"Bulk operation for T1.1: {action_data['action']}"
            )
            assert result is True


class TestLLMGuardValidationRules:
    """Test custom validation rules for LLMGuard"""
    
    def setup_method(self):
        """Setup validation rules testing"""
        self.mock_enforcer = Mock(spec=TaskSystemEnforcer)
        self.mock_enforcer.current_task = "T1.1: Security task"
        self.mock_enforcer.requires_work_log.return_value = False
        self.guard = LLMGuard(self.mock_enforcer)
    
    def test_security_task_validation(self):
        """Test special validation for security-related tasks"""
        # Security task should have stricter validation
        self.mock_enforcer.validate_task_action.return_value = True
        
        # Should require security review mention in justification
        with pytest.raises(Exception):
            self.guard.validate_action(
                "write_file",
                {"path": "auth/security.py", "content": "auth code"},
                "Adding authentication code for T1.1"
            )
        
        # Should pass with proper security justification
        result = self.guard.validate_action(
            "write_file", 
            {"path": "auth/security.py", "content": "auth code"},
            "Adding authentication code for T1.1 - security review completed"
        )
        assert result is True
    
    def test_database_operation_validation(self):
        """Test validation for database operations"""
        self.mock_enforcer.current_task = "T1.1: Database task"
        self.mock_enforcer.validate_task_action.return_value = True
        
        # Database operations should require migration mention
        database_operations = [
            {"action": "run_command", "data": {"command": "python manage.py migrate"}},
            {"action": "write_file", "data": {"path": "migrations/001_create_users.py"}},
            {"action": "edit_file", "data": {"path": "models/user.py"}}
        ]
        
        for op in database_operations:
            # Should require backup/migration strategy
            result = self.guard.validate_action(
                op["action"],
                op["data"], 
                "Database change for T1.1 with backup strategy and rollback plan"
            )
            assert result is True
    
    def test_production_deployment_validation(self):
        """Test validation for production deployment actions"""
        self.mock_enforcer.current_task = "T1.1: Deployment task"
        self.mock_enforcer.validate_task_action.return_value = True
        
        prod_actions = [
            {"action": "run_command", "data": {"command": "kubectl apply -f production.yaml"}},
            {"action": "run_command", "data": {"command": "docker push prod/image:latest"}},
            {"action": "write_file", "data": {"path": "deployment/prod-config.yaml"}}
        ]
        
        for action_data in prod_actions:
            # Should require approval and testing confirmation
            with pytest.raises(Exception):
                self.guard.validate_action(
                    action_data["action"],
                    action_data["data"],
                    "Deploying to production for T1.1"
                )
            
            # Should pass with proper approval
            result = self.guard.validate_action(
                action_data["action"],
                action_data["data"],
                "Deploying to production for T1.1 - tested and approved by tech lead"
            )
            assert result is True


class TestLLMGuardErrorHandling:
    """Test error handling in LLMGuard"""
    
    def setup_method(self):
        """Setup error handling tests"""
        self.mock_enforcer = Mock(spec=TaskSystemEnforcer)
        self.guard = LLMGuard(self.mock_enforcer)
    
    def test_enforcer_exception_handling(self):
        """Test handling of enforcer exceptions"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        self.mock_enforcer.validate_task_action.side_effect = Exception("Enforcer error")
        
        with pytest.raises(Exception) as excinfo:
            self.guard.validate_action(
                "write_file",
                {"path": "test.py"},
                "Test justification"
            )
        
        assert "Enforcer error" in str(excinfo.value)
    
    def test_invalid_action_data_handling(self):
        """Test handling of invalid action data"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        
        # Missing required fields
        with pytest.raises(Exception):
            self.guard.validate_action(
                "write_file",
                {},  # Missing path and content
                "Valid justification for T1.1"
            )
        
        # Invalid data types
        with pytest.raises(Exception):
            self.guard.validate_action(
                "write_file",
                "invalid_data_type",
                "Valid justification for T1.1"
            )
    
    def test_empty_justification_handling(self):
        """Test handling of empty or None justification"""
        self.mock_enforcer.current_task = "T1.1: Test task"
        
        with pytest.raises(Exception):
            self.guard.validate_action(
                "write_file",
                {"path": "test.py", "content": "code"},
                ""  # Empty justification
            )
        
        with pytest.raises(Exception):
            self.guard.validate_action(
                "write_file",
                {"path": "test.py", "content": "code"},
                None  # None justification
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])