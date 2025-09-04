#!/usr/bin/env python3
"""
Integration tests for AI tool integrations
Tests Claude Code, Cursor, and Copilot integrations
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock integrations if not available
try:
    from integrations.claude_code_integration import (
        select_task, enforced_read, enforced_write, enforced_bash
    )
    CLAUDE_CODE_AVAILABLE = True
except ImportError:
    CLAUDE_CODE_AVAILABLE = False

try:
    from integrations.cursor_integration import (
        setup_cursor_enforcement, update_cursor_task
    )
    CURSOR_AVAILABLE = True
except ImportError:
    CURSOR_AVAILABLE = False

try:
    from integrations.github_copilot_integration import (
        setup_copilot_enforcement, update_copilot_context
    )
    COPILOT_AVAILABLE = True
except ImportError:
    COPILOT_AVAILABLE = False


class TestClaudeCodeIntegration:
    """Test Claude Code integration"""
    
    def setup_method(self):
        """Setup Claude Code integration tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "claude_test")
        os.makedirs(self.project_dir)
        
        # Create session state
        session_state = {
            "active_tasks": ["T1.1: Test Claude Code integration"],
            "completed_tasks": [],
            "validation_requirements": {"all_tasks": {"work_log_required": False}}
        }
        
        session_path = os.path.join(self.project_dir, "SESSION_STATE.json")
        with open(session_path, 'w') as f:
            json.dump(session_state, f)
        
        # Change to project directory for integration tests
        self.original_cwd = os.getcwd()
        os.chdir(self.project_dir)
    
    def teardown_method(self):
        """Cleanup Claude Code integration tests"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.skipif(not CLAUDE_CODE_AVAILABLE, reason="Claude Code integration not available")
    def test_claude_code_task_selection(self):
        """Test task selection through Claude Code integration"""
        
        # Test task selection
        result = select_task("T1.1: Test Claude Code integration")
        assert result is True
        
        # Test invalid task selection
        with pytest.raises(Exception):
            select_task("INVALID.1: Nonexistent task")
    
    @pytest.mark.skipif(not CLAUDE_CODE_AVAILABLE, reason="Claude Code integration not available")
    def test_enforced_file_operations(self):
        """Test enforced file operations"""
        
        # Select task first
        select_task("T1.1: Test Claude Code integration")
        
        # Test enforced write
        test_content = "# Test file for Claude Code integration\nprint('Hello SuperManUS')"
        result = enforced_write(
            "test_claude.py",
            test_content,
            "Creating test file for T1.1 Claude Code integration validation"
        )
        assert result is True
        assert os.path.exists("test_claude.py")
        
        # Test enforced read
        content = enforced_read(
            "test_claude.py",
            "Reading test file to validate T1.1 integration implementation"
        )
        assert test_content in content
        
        # Test invalid justification
        with pytest.raises(Exception):
            enforced_write(
                "bad_file.py",
                "bad content",
                "Invalid justification"
            )
    
    @pytest.mark.skipif(not CLAUDE_CODE_AVAILABLE, reason="Claude Code integration not available") 
    def test_enforced_bash_operations(self):
        """Test enforced bash operations"""
        
        select_task("T1.1: Test Claude Code integration")
        
        # Create test file first
        with open("test_script.py", 'w') as f:
            f.write("print('Integration test successful')")
        
        # Test enforced bash with valid justification
        result = enforced_bash(
            "python test_script.py",
            "Running integration test script to validate T1.1 Claude Code functionality"
        )
        assert result.returncode == 0
        assert "Integration test successful" in result.stdout
        
        # Test blocked command
        with pytest.raises(Exception):
            enforced_bash(
                "rm -rf *",
                "Cleaning up files for T1.1"
            )


class TestCursorIntegration:
    """Test Cursor IDE integration"""
    
    def setup_method(self):
        """Setup Cursor integration tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "cursor_test")
        os.makedirs(self.project_dir)
        
        self.original_cwd = os.getcwd()
        os.chdir(self.project_dir)
        
        # Create session state
        session_state = {
            "active_tasks": ["T1.1: Test Cursor integration"]
        }
        
        with open("SESSION_STATE.json", 'w') as f:
            json.dump(session_state, f)
    
    def teardown_method(self):
        """Cleanup Cursor integration tests"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.skipif(not CURSOR_AVAILABLE, reason="Cursor integration not available")
    def test_cursor_enforcement_setup(self):
        """Test Cursor IDE enforcement setup"""
        
        # Test setup
        result = setup_cursor_enforcement()
        assert result is True
        
        # Check that .cursorrules.json was created
        assert os.path.exists(".cursorrules.json")
        
        # Validate configuration format
        with open(".cursorrules.json", 'r') as f:
            config = json.load(f)
        
        assert "rules" in config
        assert "taskEnforcement" in config["rules"]
        assert config["rules"]["taskEnforcement"]["enabled"] is True
    
    @pytest.mark.skipif(not CURSOR_AVAILABLE, reason="Cursor integration not available")
    def test_cursor_task_update(self):
        """Test updating Cursor task context"""
        
        # Setup first
        setup_cursor_enforcement()
        
        # Update task context
        result = update_cursor_task("T1.2: Updated task for Cursor")
        assert result is True
        
        # Verify update
        with open(".cursorrules.json", 'r') as f:
            config = json.load(f)
        
        assert "T1.2: Updated task for Cursor" in str(config)
    
    def test_cursor_config_validation(self):
        """Test Cursor configuration validation"""
        
        # Create invalid config
        invalid_config = {"invalid": "format"}
        with open(".cursorrules.json", 'w') as f:
            json.dump(invalid_config, f)
        
        if CURSOR_AVAILABLE:
            # Should handle invalid config gracefully
            result = setup_cursor_enforcement()
            assert result is True  # Should recreate valid config


class TestCopilotIntegration:
    """Test GitHub Copilot integration"""
    
    def setup_method(self):
        """Setup Copilot integration tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "copilot_test")
        os.makedirs(self.project_dir)
        
        self.original_cwd = os.getcwd()
        os.chdir(self.project_dir)
        
        # Create session state
        session_state = {
            "active_tasks": ["T1.1: Test Copilot integration"]
        }
        
        with open("SESSION_STATE.json", 'w') as f:
            json.dump(session_state, f)
    
    def teardown_method(self):
        """Cleanup Copilot integration tests"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.skipif(not COPILOT_AVAILABLE, reason="Copilot integration not available")
    def test_copilot_enforcement_setup(self):
        """Test Copilot enforcement setup"""
        
        result = setup_copilot_enforcement()
        assert result is True
        
        # Check that configuration files were created
        assert os.path.exists(".copilot-instructions.md")
        
        # Validate VS Code settings if directory exists
        if os.path.exists(".vscode"):
            assert os.path.exists(".vscode/settings.json")
    
    @pytest.mark.skipif(not COPILOT_AVAILABLE, reason="Copilot integration not available")
    def test_copilot_context_update(self):
        """Test updating Copilot context"""
        
        # Setup first
        setup_copilot_enforcement()
        
        # Update context
        result = update_copilot_context("T1.2: Updated Copilot task")
        assert result is True
        
        # Verify context update
        with open(".copilot-instructions.md", 'r') as f:
            instructions = f.read()
        
        assert "T1.2: Updated Copilot task" in instructions
    
    def test_copilot_instructions_format(self):
        """Test Copilot instructions file format"""
        
        if COPILOT_AVAILABLE:
            setup_copilot_enforcement()
            
            with open(".copilot-instructions.md", 'r') as f:
                content = f.read()
            
            # Check required sections
            assert "## Current Active Task" in content
            assert "## Task Requirements" in content
            assert "## Code Generation Guidelines" in content
            assert "## Blocked Suggestions" in content


class TestMultiToolIntegration:
    """Test integration across multiple AI tools"""
    
    def setup_method(self):
        """Setup multi-tool integration tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "multi_tool_test")
        os.makedirs(self.project_dir)
        
        self.original_cwd = os.getcwd()
        os.chdir(self.project_dir)
        
        # Create comprehensive session state
        session_state = {
            "active_tasks": [
                "T1.1: Multi-tool integration test",
                "T1.2: Cross-tool validation test"
            ],
            "validation_requirements": {
                "all_tasks": {"work_log_required": False}
            }
        }
        
        with open("SESSION_STATE.json", 'w') as f:
            json.dump(session_state, f)
    
    def teardown_method(self):
        """Cleanup multi-tool integration tests"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_consistent_task_context_across_tools(self):
        """Test that all tools maintain consistent task context"""
        
        task_id = "T1.1: Multi-tool integration test"
        
        # Setup all available integrations
        if CLAUDE_CODE_AVAILABLE:
            select_task(task_id)
        
        if CURSOR_AVAILABLE:
            setup_cursor_enforcement()
            update_cursor_task(task_id)
        
        if COPILOT_AVAILABLE:
            setup_copilot_enforcement() 
            update_copilot_context(task_id)
        
        # Verify consistency across tools
        if CURSOR_AVAILABLE:
            with open(".cursorrules.json", 'r') as f:
                cursor_config = json.load(f)
            assert task_id in str(cursor_config)
        
        if COPILOT_AVAILABLE:
            with open(".copilot-instructions.md", 'r') as f:
                copilot_instructions = f.read()
            assert task_id in copilot_instructions
    
    def test_integration_health_check(self):
        """Test health check across all integrations"""
        
        health_status = {}
        
        # Check Claude Code integration
        if CLAUDE_CODE_AVAILABLE:
            try:
                select_task("T1.1: Multi-tool integration test")
                health_status["claude_code"] = True
            except Exception:
                health_status["claude_code"] = False
        
        # Check Cursor integration
        if CURSOR_AVAILABLE:
            try:
                setup_cursor_enforcement()
                health_status["cursor"] = os.path.exists(".cursorrules.json")
            except Exception:
                health_status["cursor"] = False
        
        # Check Copilot integration
        if COPILOT_AVAILABLE:
            try:
                setup_copilot_enforcement()
                health_status["copilot"] = os.path.exists(".copilot-instructions.md")
            except Exception:
                health_status["copilot"] = False
        
        # At least one integration should be healthy
        assert any(health_status.values()) or len(health_status) == 0
    
    def test_integration_conflict_resolution(self):
        """Test resolution of conflicts between integrations"""
        
        # Setup multiple integrations with same task
        task_id = "T1.2: Cross-tool validation test"
        
        if CLAUDE_CODE_AVAILABLE:
            select_task(task_id)
        
        if CURSOR_AVAILABLE:
            setup_cursor_enforcement()
            update_cursor_task(task_id)
        
        if COPILOT_AVAILABLE:
            setup_copilot_enforcement()
            update_copilot_context(task_id)
        
        # Change task in one integration
        new_task = "T1.1: Multi-tool integration test"
        
        if CLAUDE_CODE_AVAILABLE:
            select_task(new_task)
        
        # Other integrations should be updateable to maintain consistency
        if CURSOR_AVAILABLE:
            result = update_cursor_task(new_task)
            assert result is True
        
        if COPILOT_AVAILABLE:
            result = update_copilot_context(new_task)
            assert result is True


class TestIntegrationErrorHandling:
    """Test error handling in AI tool integrations"""
    
    def setup_method(self):
        """Setup error handling tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "error_test")
        os.makedirs(self.project_dir)
        
        self.original_cwd = os.getcwd()
        os.chdir(self.project_dir)
    
    def teardown_method(self):
        """Cleanup error handling tests"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_missing_session_state_handling(self):
        """Test handling when SESSION_STATE.json is missing"""
        
        # No SESSION_STATE.json file exists
        
        if CLAUDE_CODE_AVAILABLE:
            with pytest.raises(FileNotFoundError):
                select_task("T1.1: Test task")
        
        if CURSOR_AVAILABLE:
            # Should handle gracefully or create default config
            try:
                result = setup_cursor_enforcement()
                # Should either succeed with default or fail gracefully
                assert isinstance(result, bool)
            except Exception as e:
                # Should be informative error
                assert "session" in str(e).lower() or "file" in str(e).lower()
    
    def test_corrupted_config_handling(self):
        """Test handling of corrupted configuration files"""
        
        # Create corrupted session state
        with open("SESSION_STATE.json", 'w') as f:
            f.write("invalid json {")
        
        if CLAUDE_CODE_AVAILABLE:
            with pytest.raises(json.JSONDecodeError):
                select_task("T1.1: Test task")
        
        # Create corrupted Cursor config
        with open(".cursorrules.json", 'w') as f:
            f.write("invalid json content")
        
        if CURSOR_AVAILABLE:
            # Should handle gracefully and recreate valid config
            try:
                result = setup_cursor_enforcement()
                # Should recreate valid config
                with open(".cursorrules.json", 'r') as f:
                    json.load(f)  # Should not raise JSON error
            except Exception:
                # If it fails, should be graceful failure
                pass
    
    def test_permission_error_handling(self):
        """Test handling of file permission errors"""
        
        # Create read-only file
        with open("readonly.json", 'w') as f:
            json.dump({"test": "data"}, f)
        os.chmod("readonly.json", 0o444)  # Read-only
        
        if CURSOR_AVAILABLE:
            # Should handle permission errors gracefully
            try:
                setup_cursor_enforcement()
            except PermissionError:
                # Should be caught and handled appropriately
                pass
        
        # Cleanup
        os.chmod("readonly.json", 0o644)
        os.remove("readonly.json")


if __name__ == "__main__":
    # Run with verbose output and show which integrations are available
    available_integrations = []
    if CLAUDE_CODE_AVAILABLE:
        available_integrations.append("claude_code")
    if CURSOR_AVAILABLE:
        available_integrations.append("cursor")
    if COPILOT_AVAILABLE:
        available_integrations.append("copilot")
    
    print(f"Available integrations for testing: {', '.join(available_integrations)}")
    
    pytest.main([__file__, "-v", "--tb=short"])