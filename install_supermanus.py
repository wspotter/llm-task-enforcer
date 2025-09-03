#!/usr/bin/env python3
"""
SuperManUS Task Enforcement System - Easy Installation Script
Sets up task enforcement in any project with minimal configuration
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

class SuperManUSInstaller:
    """
    Installer for SuperManUS task enforcement system
    """
    
    def __init__(self, target_project: str, source_dir: str = None):
        self.target_project = Path(target_project).resolve()
        self.source_dir = Path(source_dir or __file__).parent
        
        # Key directories
        self.target_supermanus_dir = self.target_project / "supermanus"
        self.target_integrations_dir = self.target_supermanus_dir / "integrations"
        
        # Source files to copy
        self.core_files = [
            "src/utils/task_enforcer.py",
            "src/utils/llm_guard.py"
        ]
        
        self.integration_files = [
            "integrations/claude_code_integration.py",
            "integrations/cursor_integration.py", 
            "integrations/github_copilot_integration.py"
        ]
        
        self.template_files = [
            "WORK_LOG_TEMPLATE.md",
            "HUMAN_VALIDATION_GUIDE.md"
        ]
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if target project meets prerequisites"""
        
        checks = {
            "project_exists": self.target_project.exists(),
            "is_directory": self.target_project.is_dir(),
            "has_git": (self.target_project / ".git").exists(),
            "python_project": self._is_python_project(),
            "source_files_exist": self._check_source_files()
        }
        
        return checks
    
    def _is_python_project(self) -> bool:
        """Check if target is a Python project"""
        indicators = [
            "requirements.txt", "setup.py", "pyproject.toml",
            "Pipfile", "poetry.lock", "src", "__init__.py"
        ]
        
        return any((self.target_project / indicator).exists() for indicator in indicators)
    
    def _check_source_files(self) -> bool:
        """Check if all source files exist"""
        all_files = self.core_files + self.integration_files + self.template_files
        return all((self.source_dir / file_path).exists() for file_path in all_files)
    
    def create_session_state_template(self) -> Path:
        """Create SESSION_STATE.json template if it doesn't exist"""
        
        session_file = self.target_project / "SESSION_STATE.json"
        
        if session_file.exists():
            print(f"✅ SESSION_STATE.json already exists")
            return session_file
        
        template = {
            "current_session_id": "SESSION_001",
            "last_updated": "2025-01-01T00:00:00Z",
            "project_name": self.target_project.name,
            "current_phase": "initialization",
            "current_milestone": "setup",
            "active_tasks": [
                "SETUP: Install SuperManUS task enforcement system",
                "SETUP: Configure project for task-driven development"
            ],
            "completed_tasks": [],
            "in_progress": {
                "task": "Project setup with SuperManUS",
                "subtasks": [
                    "Install task enforcement system",
                    "Create initial work log",
                    "Configure AI tool integrations"
                ]
            },
            "blockers": [],
            "next_actions": [
                "Select first real development task",
                "Begin task-driven development workflow"
            ],
            "session_notes": "Initial SuperManUS installation. Ready for task-driven development.",
            "key_decisions": [
                "Using SuperManUS for task enforcement",
                "Preventing LLM deviation through systematic validation"
            ],
            "environment": {
                "platform": os.name,
                "working_directory": str(self.target_project),
                "supermanus_version": "1.0"
            },
            "modules_status": {
                "supermanus_enforcer": "installed",
                "task_validation": "active",
                "ai_integrations": "configured"
            },
            "achievements": [
                "SuperManUS task enforcement system installed",
                "Project configured for systematic development"
            ]
        }
        
        with open(session_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"✅ Created SESSION_STATE.json template")
        return session_file
    
    def copy_core_files(self) -> List[Path]:
        """Copy core SuperManUS files to target project"""
        
        copied_files = []
        
        # Create supermanus directory structure
        self.target_supermanus_dir.mkdir(exist_ok=True)
        (self.target_supermanus_dir / "utils").mkdir(exist_ok=True)
        self.target_integrations_dir.mkdir(exist_ok=True)
        
        # Create __init__.py files
        for init_dir in [self.target_supermanus_dir, self.target_supermanus_dir / "utils", self.target_integrations_dir]:
            init_file = init_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# SuperManUS Task Enforcement System\n")
        
        # Copy core enforcement files
        for file_path in self.core_files:
            source_file = self.source_dir / file_path
            target_file = self.target_supermanus_dir / Path(file_path).name
            
            if source_file.exists():
                shutil.copy2(source_file, target_file)
                copied_files.append(target_file)
                print(f"✅ Copied {file_path}")
            else:
                print(f"⚠️  Source file missing: {file_path}")
        
        # Copy integration files
        for file_path in self.integration_files:
            source_file = self.source_dir / file_path
            target_file = self.target_integrations_dir / Path(file_path).name
            
            if source_file.exists():
                shutil.copy2(source_file, target_file)
                copied_files.append(target_file)
                print(f"✅ Copied {file_path}")
            else:
                print(f"⚠️  Source file missing: {file_path}")
        
        # Copy template files to project root
        for file_path in self.template_files:
            source_file = self.source_dir / file_path
            target_file = self.target_project / Path(file_path).name
            
            if source_file.exists() and not target_file.exists():
                shutil.copy2(source_file, target_file)
                copied_files.append(target_file)
                print(f"✅ Copied {file_path}")
            elif target_file.exists():
                print(f"✅ {file_path} already exists")
        
        return copied_files
    
    def create_quick_start_script(self) -> Path:
        """Create a quick start script for the target project"""
        
        script_content = f'''#!/usr/bin/env python3
"""
SuperManUS Quick Start - {self.target_project.name}
Generated by SuperManUS installer
"""

import sys
from pathlib import Path

# Add SuperManUS to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "supermanus"))

try:
    from task_enforcer import get_enforcer, TaskSystemEnforcer
    from llm_guard import check_task_discipline, LLMActionGuard
    
    # Import integrations
    sys.path.insert(0, str(project_root / "supermanus" / "integrations"))
    from claude_code_integration import get_enforced_claude_code, select_task
    from cursor_integration import setup_cursor_enforcement
    from github_copilot_integration import setup_copilot_enforcement
    
except ImportError as e:
    print(f"❌ SuperManUS not properly installed: {{e}}")
    print("Run the installer again or check file permissions")
    sys.exit(1)

def quick_start():
    """Quick start guide for SuperManUS"""
    
    print("🦸 SuperManUS Task Enforcement System")
    print("=" * 50)
    print(f"Project: {self.target_project.name}")
    print()
    
    # Check current status
    enforcer = get_enforcer()
    
    try:
        active_tasks = enforcer.get_active_tasks()
        print(f"📋 Available tasks: {{len(active_tasks)}}")
        
        if active_tasks:
            for i, task in enumerate(active_tasks, 1):
                print(f"  {{i}}. {{task}}")
        
        if not enforcer.current_task:
            print("\\n⚠️  No task selected. Choose from active_tasks above.")
            print("Usage: select_task('task_id_here')")
        else:
            print(f"\\n✅ Current task: {{enforcer.current_task['id']}}")
            
        # Show discipline status
        disciplined, message = check_task_discipline()
        print(f"\\n🎯 Task discipline: {{'✅ Good' if disciplined else '❌ Needs attention'}}")
        
    except Exception as e:
        print(f"⚠️  Error checking status: {{e}}")
        print("Make sure SESSION_STATE.json exists and is valid")
    
    print("\\n🚀 Quick Actions:")
    print("- select_task('task_id') - Select a task")  
    print("- check_task_discipline() - Check current status")
    print("- setup_cursor_enforcement() - Configure Cursor IDE")
    print("- setup_copilot_enforcement() - Configure GitHub Copilot")
    
    print("\\n📚 Documentation:")
    print("- WORK_LOG_TEMPLATE.md - Required for all tasks")
    print("- HUMAN_VALIDATION_GUIDE.md - For human reviewers")
    
    return True

if __name__ == "__main__":
    quick_start()
'''
        
        script_file = self.target_project / "supermanus_start.py"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(script_file, 0o755)
        
        print(f"✅ Created quick start script: {script_file.name}")
        return script_file
    
    def create_gitignore_entries(self) -> bool:
        """Add SuperManUS-specific entries to .gitignore"""
        
        gitignore_file = self.target_project / ".gitignore"
        
        entries_to_add = [
            "# SuperManUS Task Enforcement",
            "work_logs/",
            "*.supermanus_backup",
            ".cursorrules.json",
            ".copilot-instructions.md",
            "supermanus/__pycache__/",
            "supermanus/**/__pycache__/"
        ]
        
        if gitignore_file.exists():
            with open(gitignore_file, 'r') as f:
                existing_content = f.read()
        else:
            existing_content = ""
        
        # Add entries that don't exist
        new_entries = []
        for entry in entries_to_add:
            if entry not in existing_content:
                new_entries.append(entry)
        
        if new_entries:
            with open(gitignore_file, 'a') as f:
                if existing_content and not existing_content.endswith('\\n'):
                    f.write('\\n')
                f.write('\\n'.join(new_entries) + '\\n')
            
            print(f"✅ Updated .gitignore with {len(new_entries)} SuperManUS entries")
        else:
            print("✅ .gitignore already contains SuperManUS entries")
        
        return True
    
    def install(self, setup_integrations: bool = True) -> Dict[str, Any]:
        """
        Complete SuperManUS installation
        """
        
        print(f"🦸 Installing SuperManUS in: {self.target_project}")
        print("=" * 60)
        
        # Check prerequisites
        print("\\n📋 Checking prerequisites...")
        prereqs = self.check_prerequisites()
        
        for check, passed in prereqs.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}: {passed}")
        
        if not all(prereqs.values()):
            print("\\n❌ Prerequisites not met. Installation aborted.")
            return {"success": False, "error": "Prerequisites failed"}
        
        results = {
            "success": True,
            "files_copied": [],
            "session_state_created": False,
            "quick_start_created": False,
            "integrations_setup": False
        }
        
        try:
            # Copy core files
            print("\\n📁 Copying SuperManUS files...")
            copied_files = self.copy_core_files()
            results["files_copied"] = [str(f) for f in copied_files]
            
            # Create session state template
            print("\\n📄 Setting up project configuration...")
            session_file = self.create_session_state_template()
            results["session_state_created"] = session_file.exists()
            
            # Create quick start script
            print("\\n🚀 Creating quick start script...")
            script_file = self.create_quick_start_script()
            results["quick_start_created"] = script_file.exists()
            
            # Update .gitignore
            print("\\n📝 Updating .gitignore...")
            self.create_gitignore_entries()
            
            # Setup integrations
            if setup_integrations:
                print("\\n🔗 Setting up AI tool integrations...")
                self.setup_ai_integrations()
                results["integrations_setup"] = True
            
            print("\\n" + "=" * 60)
            print("✅ SuperManUS installation complete!")
            print("\\n🚀 Next steps:")
            print(f"1. Run: python supermanus_start.py")
            print(f"2. Select a task from SESSION_STATE.json")
            print(f"3. Create work log using WORK_LOG_TEMPLATE.md")
            print(f"4. Start task-driven development!")
            print("\\n📚 Read HUMAN_VALIDATION_GUIDE.md for review workflow")
            
        except Exception as e:
            print(f"\\n❌ Installation failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def setup_ai_integrations(self) -> Dict[str, bool]:
        """Setup integrations for popular AI coding tools"""
        
        results = {}
        
        # Check which tools might be available
        vscode_dir = self.target_project / ".vscode"
        if vscode_dir.exists():
            print("  📝 VS Code detected - setting up Cursor and Copilot integration")
            
            # Create basic integration setup files
            cursor_rules = {
                "supermanus_integration": True,
                "task_enforcement_active": True,
                "require_justification": True
            }
            
            cursor_file = self.target_project / ".cursorrules.json"
            with open(cursor_file, 'w') as f:
                json.dump(cursor_rules, f, indent=2)
            
            results["cursor"] = True
            print("  ✅ Cursor integration configured")
        
        # Create integration readme
        integration_readme = self.target_integrations_dir / "README.md"
        readme_content = '''# SuperManUS AI Tool Integrations

## Available Integrations

### Claude Code
```python
from claude_code_integration import enforced_read, enforced_write, select_task
# All operations require task justification
```

### Cursor IDE  
```python
from cursor_integration import setup_cursor_enforcement
setup_cursor_enforcement()  # Creates .cursorrules.json
```

### GitHub Copilot
```python  
from github_copilot_integration import setup_copilot_enforcement
setup_copilot_enforcement()  # Configures context injection
```

## Usage Pattern
1. Select active task: `select_task("T1.1: Task description")`
2. Use enforced operations: `enforced_write("file.py", content, justification="Advances current task by...")`  
3. All actions validated against current task
4. Complete with proof validation

See parent directory documentation for full workflow.
'''
        
        with open(integration_readme, 'w') as f:
            f.write(readme_content)
        
        results["readme"] = True
        
        return results

def main():
    """Main installer interface"""
    
    parser = argparse.ArgumentParser(
        description="Install SuperManUS task enforcement system in any project"
    )
    
    parser.add_argument(
        "target_project", 
        help="Path to target project directory"
    )
    
    parser.add_argument(
        "--source", 
        help="Path to SuperManUS source directory (default: auto-detect)"
    )
    
    parser.add_argument(
        "--no-integrations", 
        action="store_true",
        help="Skip AI tool integration setup"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be installed without making changes"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN - No files will be modified")
        print(f"Target: {Path(args.target_project).resolve()}")
        print(f"Source: {Path(args.source or __file__).parent}")
        return
    
    # Run installation
    installer = SuperManUSInstaller(args.target_project, args.source)
    result = installer.install(setup_integrations=not args.no_integrations)
    
    if result["success"]:
        print("\\n🎉 Installation successful!")
    else:
        print(f"\\n💥 Installation failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()