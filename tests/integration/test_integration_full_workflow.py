#!/usr/bin/env python3
"""
Integration tests for SuperManUS full workflow
Tests the complete task enforcement workflow from start to finish
"""

import pytest
import json
import tempfile
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from task_enforcer import TaskSystemEnforcer
from llm_guard import LLMGuard


class TestFullWorkflowIntegration:
    """Test complete SuperManUS workflow integration"""
    
    def setup_method(self):
        """Setup full integration test environment"""
        # Create temporary project directory
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_dir)
        
        # Set up project structure
        self.session_state_path = os.path.join(self.project_dir, "SESSION_STATE.json")
        self.work_log_dir = os.path.join(self.project_dir, "work_logs")
        self.src_dir = os.path.join(self.project_dir, "src")
        
        os.makedirs(self.work_log_dir)
        os.makedirs(self.src_dir)
        
        # Create realistic session state
        self.session_state = {
            "current_session_id": "INTEGRATION_001",
            "last_updated": "2025-09-04T10:00:00Z",
            "project_name": "Integration Test Project",
            "current_phase": "development",
            "active_tasks": [
                "T1.1: Implement user authentication system",
                "T1.2: Create user dashboard interface",
                "T2.1: Add task management functionality",
                "BUGFIX.1: Fix authentication token expiry"
            ],
            "completed_tasks": [
                "SETUP.1: Initialize project structure",
                "SETUP.2: Configure development environment"
            ],
            "team_assignments": {
                "integration_tester": ["T1.1: Implement user authentication system"],
                "other_dev": ["T1.2: Create user dashboard interface"]
            },
            "validation_requirements": {
                "all_tasks": {
                    "work_log_required": True,
                    "proof_required": True,
                    "tests_required": True
                },
                "security_tasks": {
                    "security_review": True,
                    "penetration_test": True
                }
            }
        }
        
        with open(self.session_state_path, 'w') as f:
            json.dump(self.session_state, f, indent=2)
        
        # Initialize components
        self.enforcer = TaskSystemEnforcer(
            session_state_path=self.session_state_path,
            work_log_dir=self.work_log_dir
        )
        self.guard = LLMGuard(self.enforcer)
    
    def teardown_method(self):
        """Cleanup integration test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_complete_authentication_task_workflow(self):
        """Test complete workflow for authentication task"""
        
        # Step 1: Task Selection
        task_id = "T1.1: Implement user authentication system"
        self.enforcer.select_task(task_id)
        assert self.enforcer.current_task == task_id
        
        # Step 2: Work Log Creation (Required)
        work_log_content = f"""
# Work Log for T1.1: Implement user authentication system

## Task Information
- **Task ID:** T1.1
- **Task Description:** Implement user authentication system
- **Start Time:** {datetime.now().isoformat()}
- **Developer:** integration_tester

## Pre-Work Validation
- **Environment Check:** Python environment available
- **Dependencies:** pytest, flask available
- **Success Criteria:** Users can register, login, and logout securely

## Work Performed
### Step 1: Create authentication module structure
- **Command/Action:** mkdir src/auth && touch src/auth/__init__.py
- **Expected Result:** Auth module directory created
- **Actual Result:** Directory created successfully
- **Files Created:** src/auth/__init__.py

### Step 2: Implement user model
- **Command/Action:** Create user.py with User class
- **Expected Result:** User model with auth methods
- **Actual Result:** Model created with hash_password, verify_password methods
- **Files Created:** src/auth/user.py
"""
        
        work_log_path = os.path.join(self.work_log_dir, "task_T1_1_auth.md")
        with open(work_log_path, 'w') as f:
            f.write(work_log_content)
        
        # Verify work log requirement satisfied
        assert self.enforcer.requires_work_log() is False
        
        # Step 3: Implement Authentication Components
        # Create auth module structure
        auth_dir = os.path.join(self.src_dir, "auth")
        os.makedirs(auth_dir, exist_ok=True)
        
        # Validate file creation through guard
        init_content = '"""Authentication module for SuperManUS integration test"""'
        result = self.guard.validate_action(
            "write_file",
            {"path": os.path.join(auth_dir, "__init__.py"), "content": init_content},
            "Creating auth module init file as required by T1.1 authentication implementation"
        )
        assert result is True
        
        # Write the actual file
        with open(os.path.join(auth_dir, "__init__.py"), 'w') as f:
            f.write(init_content)
        
        # Create user model
        user_model_content = '''
"""User model for authentication system"""

import hashlib
import secrets
from typing import Optional


class User:
    def __init__(self, username: str, email: str, password_hash: Optional[str] = None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.salt = secrets.token_hex(32)
        self.is_active = True
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        combined = password + self.salt
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return self.password_hash == self.hash_password(password)
    
    def set_password(self, password: str):
        """Set user password"""
        self.password_hash = self.hash_password(password)
'''
        
        result = self.guard.validate_action(
            "write_file",
            {"path": os.path.join(auth_dir, "user.py"), "content": user_model_content},
            "Implementing User model class for T1.1 authentication system with secure password hashing"
        )
        assert result is True
        
        # Write user model file
        with open(os.path.join(auth_dir, "user.py"), 'w') as f:
            f.write(user_model_content)
        
        # Step 4: Create Tests
        tests_dir = os.path.join(self.project_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        
        test_content = '''
"""Tests for authentication system"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.user import User


class TestUserAuthentication:
    def test_user_creation(self):
        """Test user can be created"""
        user = User("testuser", "test@example.com")
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
    
    def test_password_hashing(self):
        """Test password hashing works"""
        user = User("testuser", "test@example.com")
        user.set_password("secure_password")
        assert user.password_hash is not None
        assert user.password_hash != "secure_password"  # Should be hashed
    
    def test_password_verification(self):
        """Test password verification works"""
        user = User("testuser", "test@example.com")
        user.set_password("secure_password")
        
        assert user.verify_password("secure_password") is True
        assert user.verify_password("wrong_password") is False
    
    def test_salt_uniqueness(self):
        """Test that each user gets unique salt"""
        user1 = User("user1", "user1@example.com")
        user2 = User("user2", "user2@example.com")
        assert user1.salt != user2.salt
'''
        
        result = self.guard.validate_action(
            "write_file",
            {"path": os.path.join(tests_dir, "test_auth.py"), "content": test_content},
            "Creating comprehensive test suite for T1.1 authentication system validation"
        )
        assert result is True
        
        with open(os.path.join(tests_dir, "test_auth.py"), 'w') as f:
            f.write(test_content)
        
        # Step 5: Run Tests (Validation)
        test_command = f"cd {self.project_dir} && python -m pytest tests/test_auth.py -v"
        result = self.guard.validate_action(
            "run_command",
            {"command": test_command},
            "Running authentication tests to validate T1.1 implementation quality"
        )
        assert result is True
        
        # Actually run the tests to verify they pass
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/test_auth.py", "-v"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, f"Tests failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.skip("Test execution timed out")
        
        # Step 6: Task Completion with Proof Package
        proof_package = {
            "file_evidence": f"ls -la {auth_dir}/ && wc -l {auth_dir}/*.py",
            "functional_test": f"cd {self.project_dir} && python -m pytest tests/test_auth.py -v",
            "code_quality": f"python -m py_compile {auth_dir}/user.py",
            "security_validation": "Password hashing implemented with secure salt generation"
        }
        
        # Complete the task
        completion_result = self.enforcer.complete_task(task_id, proof_package)
        assert completion_result is True
        
        # Verify task moved to completed
        updated_state = self.enforcer._load_session_state()
        assert task_id in updated_state["completed_tasks"]
        assert task_id not in updated_state["active_tasks"]
    
    def test_multi_developer_workflow(self):
        """Test workflow with multiple developers working on different tasks"""
        
        # Developer 1 works on authentication
        dev1_task = "T1.1: Implement user authentication system"
        self.enforcer.select_task(dev1_task)
        
        # Create work log for dev1
        dev1_work_log = os.path.join(self.work_log_dir, "dev1_auth_task.md")
        with open(dev1_work_log, 'w') as f:
            f.write(f"# Work Log for {dev1_task}\n\nDeveloper 1 authentication work\n")
        
        # Dev1 creates auth file
        result = self.guard.validate_action(
            "write_file",
            {"path": os.path.join(self.src_dir, "auth_dev1.py"), "content": "# Auth by dev1"},
            "Creating authentication module as assigned developer for T1.1"
        )
        assert result is True
        
        # Switch to Developer 2 task
        dev2_task = "T1.2: Create user dashboard interface"
        self.enforcer.select_task(dev2_task)
        
        # Create work log for dev2
        dev2_work_log = os.path.join(self.work_log_dir, "dev2_dashboard_task.md")
        with open(dev2_work_log, 'w') as f:
            f.write(f"# Work Log for {dev2_task}\n\nDeveloper 2 dashboard work\n")
        
        # Dev2 creates dashboard file
        result = self.guard.validate_action(
            "write_file",
            {"path": os.path.join(self.src_dir, "dashboard.py"), "content": "# Dashboard UI"},
            "Creating dashboard interface components for T1.2 user interface requirements"
        )
        assert result is True
        
        # Both files should exist
        assert os.path.exists(os.path.join(self.src_dir, "auth_dev1.py"))
        assert os.path.exists(os.path.join(self.src_dir, "dashboard.py"))
        
        # Both work logs should exist
        assert os.path.exists(dev1_work_log)
        assert os.path.exists(dev2_work_log)
    
    def test_task_violation_prevention(self):
        """Test prevention of task violations and off-scope work"""
        
        # Select authentication task
        auth_task = "T1.1: Implement user authentication system"
        self.enforcer.select_task(auth_task)
        
        # Create minimal work log
        work_log_path = os.path.join(self.work_log_dir, "auth_work.md")
        with open(work_log_path, 'w') as f:
            f.write(f"# Work Log for {auth_task}\n\nStarted authentication work\n")
        
        # Try to do work unrelated to authentication - should be blocked
        unrelated_actions = [
            {
                "action": "write_file",
                "data": {"path": os.path.join(self.src_dir, "ui_animations.py"), "content": "# Fancy animations"},
                "justification": "Adding cool animations to make UI prettier"
            },
            {
                "action": "write_file", 
                "data": {"path": os.path.join(self.src_dir, "analytics.py"), "content": "# User analytics"},
                "justification": "Tracking user behavior for business insights"
            },
            {
                "action": "run_command",
                "data": {"command": "npm install fancy-ui-lib"},
                "justification": "Installing new UI library for better design"
            }
        ]
        
        for action_data in unrelated_actions:
            with pytest.raises(Exception) as excinfo:
                self.guard.validate_action(
                    action_data["action"],
                    action_data["data"],
                    action_data["justification"]
                )
            
            assert "task" in str(excinfo.value).lower() or "justification" in str(excinfo.value).lower()
        
        # Valid authentication-related work should pass
        valid_actions = [
            {
                "action": "write_file",
                "data": {"path": os.path.join(self.src_dir, "auth", "login.py"), "content": "# Login logic"},
                "justification": "Implementing login functionality for T1.1 authentication system"
            },
            {
                "action": "write_file",
                "data": {"path": os.path.join(self.src_dir, "auth", "session.py"), "content": "# Session management"},
                "justification": "Creating session management for T1.1 user authentication requirements"
            }
        ]
        
        for action_data in valid_actions:
            result = self.guard.validate_action(
                action_data["action"],
                action_data["data"], 
                action_data["justification"]
            )
            assert result is True
    
    def test_proof_validation_workflow(self):
        """Test proof validation for task completion"""
        
        # Select and setup task
        task_id = "T2.1: Add task management functionality"
        self.enforcer.select_task(task_id)
        
        # Create work log
        work_log_path = os.path.join(self.work_log_dir, "task_mgmt.md")
        with open(work_log_path, 'w') as f:
            f.write(f"# Work Log for {task_id}\n\nImplementing task management\n")
        
        # Create task management file
        task_mgmt_content = '''
"""Task Management System"""

class Task:
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.completed = False
    
    def mark_complete(self):
        self.completed = True

class TaskManager:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, task):
        self.tasks.append(task)
    
    def get_tasks(self):
        return self.tasks
    
    def complete_task(self, task_title):
        for task in self.tasks:
            if task.title == task_title:
                task.mark_complete()
                return True
        return False
'''
        
        self.guard.validate_action(
            "write_file",
            {"path": os.path.join(self.src_dir, "task_manager.py"), "content": task_mgmt_content},
            "Implementing task management classes for T2.1 task functionality requirements"
        )
        
        with open(os.path.join(self.src_dir, "task_manager.py"), 'w') as f:
            f.write(task_mgmt_content)
        
        # Test insufficient proof package - should fail
        weak_proof = {
            "claim": "Task management implemented"
        }
        
        with pytest.raises(Exception) as excinfo:
            self.enforcer.complete_task(task_id, weak_proof)
        assert "proof" in str(excinfo.value).lower()
        
        # Comprehensive proof package - should pass
        comprehensive_proof = {
            "file_evidence": f"ls -la {self.src_dir}/task_manager.py && wc -l {self.src_dir}/task_manager.py",
            "functional_test": "Task and TaskManager classes implemented with required methods",
            "integration_test": "Classes can be imported and instantiated successfully", 
            "code_quality": f"python -m py_compile {self.src_dir}/task_manager.py",
            "feature_completeness": "Add, list, and complete task functionality implemented"
        }
        
        completion_result = self.enforcer.complete_task(task_id, comprehensive_proof)
        assert completion_result is True


class TestIntegrationRealWorldScenarios:
    """Test integration with real-world development scenarios"""
    
    def setup_method(self):
        """Setup real-world scenario testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "real_project")
        os.makedirs(self.project_dir)
        
        # Create realistic project structure
        for directory in ["src", "tests", "config", "docs", "work_logs"]:
            os.makedirs(os.path.join(self.project_dir, directory))
        
        # Create session state
        session_state = {
            "current_session_id": "REAL_001",
            "project_name": "Real World Project",
            "active_tasks": [
                "FEATURE.1: Implement OAuth2 integration",
                "BUGFIX.1: Fix database connection pool leak",
                "REFACTOR.1: Optimize API response times",
                "DOCS.1: Update API documentation"
            ],
            "validation_requirements": {
                "all_tasks": {"work_log_required": True, "proof_required": True},
                "security_tasks": {"security_review": True},
                "performance_tasks": {"benchmark_required": True}
            }
        }
        
        session_path = os.path.join(self.project_dir, "SESSION_STATE.json")
        with open(session_path, 'w') as f:
            json.dump(session_state, f)
        
        self.enforcer = TaskSystemEnforcer(
            session_state_path=session_path,
            work_log_dir=os.path.join(self.project_dir, "work_logs")
        )
        self.guard = LLMGuard(self.enforcer)
    
    def teardown_method(self):
        """Cleanup real-world scenario testing"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_security_feature_workflow(self):
        """Test workflow for security-sensitive feature"""
        
        # Select OAuth implementation task
        task_id = "FEATURE.1: Implement OAuth2 integration"
        self.enforcer.select_task(task_id)
        
        # Create detailed work log for security feature
        work_log_content = f"""
# Work Log for FEATURE.1: Implement OAuth2 integration

## Security Considerations
- OAuth2 implementation requires secure token handling
- HTTPS enforcement needed for token exchange
- Token expiration and refresh logic required
- Security review mandatory before deployment

## Implementation Plan
1. Create OAuth2 client configuration
2. Implement authorization code flow
3. Add token storage and management
4. Create security tests
5. Conduct security review
"""
        
        work_log_path = os.path.join(self.project_dir, "work_logs", "oauth_implementation.md")
        with open(work_log_path, 'w') as f:
            f.write(work_log_content)
        
        # Implement OAuth configuration - should require security review mention
        oauth_config_content = '''
"""OAuth2 Configuration"""

import os
from typing import Dict

class OAuth2Config:
    def __init__(self):
        self.client_id = os.getenv("OAUTH_CLIENT_ID")
        self.client_secret = os.getenv("OAUTH_CLIENT_SECRET") 
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        
        # Security: Validate configuration
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Missing required OAuth2 configuration")
    
    def get_auth_params(self) -> Dict[str, str]:
        """Get OAuth2 authorization parameters"""
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid profile email",
            "state": self._generate_state_token()
        }
    
    def _generate_state_token(self) -> str:
        """Generate secure state token for CSRF protection"""
        import secrets
        return secrets.token_urlsafe(32)
'''
        
        result = self.guard.validate_action(
            "write_file",
            {"path": os.path.join(self.project_dir, "src", "oauth_config.py"), "content": oauth_config_content},
            "Implementing OAuth2 configuration for FEATURE.1 with security best practices - security review completed"
        )
        assert result is True
        
        # Security test should be required
        security_test_content = '''
"""Security tests for OAuth2 implementation"""

import pytest
from src.oauth_config import OAuth2Config


class TestOAuth2Security:
    def test_config_validation(self):
        """Test configuration validation"""
        # Should raise error with missing config
        with pytest.raises(ValueError):
            config = OAuth2Config()
    
    def test_state_token_generation(self):
        """Test CSRF protection state token"""
        import os
        os.environ.update({
            "OAUTH_CLIENT_ID": "test_id",
            "OAUTH_CLIENT_SECRET": "test_secret", 
            "OAUTH_REDIRECT_URI": "https://example.com/callback"
        })
        
        config = OAuth2Config()
        params = config.get_auth_params()
        
        assert "state" in params
        assert len(params["state"]) > 20  # Sufficient entropy
        
        # State tokens should be unique
        params2 = config.get_auth_params()
        assert params["state"] != params2["state"]
'''
        
        result = self.guard.validate_action(
            "write_file",
            {"path": os.path.join(self.project_dir, "tests", "test_oauth_security.py"), "content": security_test_content},
            "Creating security tests for FEATURE.1 OAuth implementation to validate security requirements"
        )
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])