#!/usr/bin/env python3
"""
SuperManUS Installation Validator
Comprehensive validation of SuperManUS TaskEnforcer installation
"""

import os
import sys
import json
import importlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any


class SuperManUSValidator:
    """Validates SuperManUS TaskEnforcer installation"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "checks": {},
            "summary": {}
        }
        self.errors = []
        self.warnings = []
    
    def print_header(self):
        """Print validation header"""
        print("🔍 SuperManUS Installation Validator")
        print("=" * 50)
        print(f"📁 Project Root: {self.project_root}")
        print(f"⏰ Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def validate_core_files(self) -> bool:
        """Validate core SuperManUS files exist"""
        print("📋 Validating Core Files...")
        
        required_files = {
            "task_enforcer.py": "Core task enforcement engine",
            "llm_guard.py": "LLM action guard and validator",
            "demo_enforcement.py": "Demonstration script"
        }
        
        supermanus_dir = self.project_root / "supermanus"
        if not supermanus_dir.exists():
            # Check if files are in project root (alternative structure)
            supermanus_dir = self.project_root
        
        missing_files = []
        for file_name, description in required_files.items():
            file_path = supermanus_dir / file_name
            if file_path.exists():
                print(f"  ✅ {file_name} - {description}")
                self.validation_results["checks"][f"core_file_{file_name}"] = True
            else:
                print(f"  ❌ {file_name} - Missing ({description})")
                missing_files.append(file_name)
                self.validation_results["checks"][f"core_file_{file_name}"] = False
        
        if missing_files:
            self.errors.append(f"Missing core files: {', '.join(missing_files)}")
            return False
        
        print("  ✅ All core files present")
        return True
    
    def validate_integrations(self) -> bool:
        """Validate integration modules"""
        print("\n🔌 Validating Integration Modules...")
        
        integrations_dir = self.project_root / "supermanus" / "integrations"
        if not integrations_dir.exists():
            integrations_dir = self.project_root / "integrations"
        
        if not integrations_dir.exists():
            print("  ⚠️  Integrations directory not found")
            self.warnings.append("Integrations directory missing")
            return False
        
        expected_integrations = {
            "claude_code_integration.py": "Claude Code enforcement integration",
            "cursor_integration.py": "Cursor IDE integration", 
            "github_copilot_integration.py": "GitHub Copilot integration",
            "__init__.py": "Python package initialization"
        }
        
        all_present = True
        for file_name, description in expected_integrations.items():
            file_path = integrations_dir / file_name
            if file_path.exists():
                print(f"  ✅ {file_name} - {description}")
                self.validation_results["checks"][f"integration_{file_name}"] = True
            else:
                print(f"  ❌ {file_name} - Missing ({description})")
                self.validation_results["checks"][f"integration_{file_name}"] = False
                all_present = False
        
        if all_present:
            print("  ✅ All integration modules present")
        else:
            self.warnings.append("Some integration modules missing")
        
        return all_present
    
    def validate_session_state(self) -> bool:
        """Validate SESSION_STATE.json file"""
        print("\n📄 Validating SESSION_STATE.json...")
        
        session_file = self.project_root / "SESSION_STATE.json"
        if not session_file.exists():
            print("  ❌ SESSION_STATE.json not found")
            self.errors.append("SESSION_STATE.json missing")
            return False
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check required fields
            required_fields = [
                "current_session_id",
                "project_name", 
                "active_tasks",
                "completed_tasks"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in session_data:
                    missing_fields.append(field)
                else:
                    print(f"  ✅ Field '{field}' present")
                    self.validation_results["checks"][f"session_field_{field}"] = True
            
            if missing_fields:
                print(f"  ❌ Missing required fields: {', '.join(missing_fields)}")
                self.errors.append(f"SESSION_STATE.json missing fields: {', '.join(missing_fields)}")
                return False
            
            # Validate active tasks format
            if isinstance(session_data.get("active_tasks"), list):
                task_count = len(session_data["active_tasks"])
                print(f"  ✅ Active tasks: {task_count} tasks defined")
                self.validation_results["checks"]["active_tasks_count"] = task_count
            else:
                print("  ❌ Active tasks should be a list")
                self.errors.append("Invalid active_tasks format")
                return False
            
            print("  ✅ SESSION_STATE.json validation passed")
            return True
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON format: {e}")
            self.errors.append(f"SESSION_STATE.json JSON error: {e}")
            return False
        except Exception as e:
            print(f"  ❌ Error reading SESSION_STATE.json: {e}")
            self.errors.append(f"SESSION_STATE.json read error: {e}")
            return False
    
    def validate_templates(self) -> bool:
        """Validate template files"""
        print("\n📝 Validating Template Files...")
        
        template_files = {
            "WORK_LOG_TEMPLATE.md": "Work log template for task documentation",
            "HUMAN_VALIDATION_GUIDE.md": "Human validation process guide"
        }
        
        all_present = True
        for file_name, description in template_files.items():
            file_path = self.project_root / file_name
            if file_path.exists():
                # Check if file has content
                if file_path.stat().st_size > 0:
                    print(f"  ✅ {file_name} - {description}")
                    self.validation_results["checks"][f"template_{file_name}"] = True
                else:
                    print(f"  ⚠️  {file_name} - Present but empty")
                    self.warnings.append(f"{file_name} is empty")
                    self.validation_results["checks"][f"template_{file_name}"] = "empty"
            else:
                print(f"  ❌ {file_name} - Missing ({description})")
                self.validation_results["checks"][f"template_{file_name}"] = False
                all_present = False
        
        return all_present
    
    def validate_configuration(self) -> bool:
        """Validate SuperManUS configuration"""
        print("\n⚙️  Validating Configuration...")
        
        config_file = self.project_root / ".supermanus" / "config.json"
        if not config_file.exists():
            print("  ⚠️  Configuration file not found (.supermanus/config.json)")
            print("  ℹ️  SuperManUS will use default configuration")
            self.warnings.append("No custom configuration file")
            return True
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Check configuration structure
            expected_sections = [
                "enforcement_level",
                "integrations"
            ]
            
            for section in expected_sections:
                if section in config_data:
                    print(f"  ✅ Configuration section '{section}' present")
                else:
                    print(f"  ⚠️  Configuration section '{section}' missing")
                    self.warnings.append(f"Config section '{section}' missing")
            
            print("  ✅ Configuration file validation passed")
            return True
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid configuration JSON: {e}")
            self.errors.append(f"Configuration JSON error: {e}")
            return False
    
    def validate_python_imports(self) -> bool:
        """Validate Python module imports"""
        print("\n🐍 Validating Python Imports...")
        
        # Add project directories to path
        sys.path.insert(0, str(self.project_root / "supermanus"))
        sys.path.insert(0, str(self.project_root))
        
        core_modules = [
            ("task_enforcer", "TaskSystemEnforcer"),
            ("llm_guard", "LLMGuard")
        ]
        
        import_success = True
        for module_name, class_name in core_modules:
            try:
                module = importlib.import_module(module_name)
                class_obj = getattr(module, class_name)
                print(f"  ✅ {module_name}.{class_name} - Import successful")
                self.validation_results["checks"][f"import_{module_name}"] = True
            except ImportError as e:
                print(f"  ❌ {module_name}.{class_name} - Import failed: {e}")
                self.errors.append(f"Import error: {module_name} - {e}")
                self.validation_results["checks"][f"import_{module_name}"] = False
                import_success = False
            except AttributeError as e:
                print(f"  ❌ {module_name}.{class_name} - Class not found: {e}")
                self.errors.append(f"Class error: {class_name} - {e}")
                self.validation_results["checks"][f"import_{module_name}"] = False
                import_success = False
            except Exception as e:
                print(f"  ❌ {module_name}.{class_name} - Unexpected error: {e}")
                self.errors.append(f"Unexpected import error: {module_name} - {e}")
                self.validation_results["checks"][f"import_{module_name}"] = False
                import_success = False
        
        return import_success
    
    def validate_directory_structure(self) -> bool:
        """Validate project directory structure"""
        print("\n📁 Validating Directory Structure...")
        
        expected_directories = {
            "work_logs": "Directory for work log files",
            ".supermanus": "Configuration directory"
        }
        
        optional_directories = {
            "docs": "Documentation directory",
            "tests": "Test files directory",
            "example_project": "Example project structure"
        }
        
        structure_valid = True
        
        # Check required directories
        for dir_name, description in expected_directories.items():
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"  ✅ {dir_name}/ - {description}")
                self.validation_results["checks"][f"directory_{dir_name}"] = True
            else:
                print(f"  ❌ {dir_name}/ - Missing ({description})")
                self.errors.append(f"Missing directory: {dir_name}")
                self.validation_results["checks"][f"directory_{dir_name}"] = False
                structure_valid = False
        
        # Check optional directories
        for dir_name, description in optional_directories.items():
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"  ✅ {dir_name}/ - {description}")
                self.validation_results["checks"][f"optional_directory_{dir_name}"] = True
            else:
                print(f"  ⚠️  {dir_name}/ - Optional ({description})")
                self.validation_results["checks"][f"optional_directory_{dir_name}"] = False
        
        return structure_valid
    
    def test_basic_functionality(self) -> bool:
        """Test basic SuperManUS functionality"""
        print("\n🧪 Testing Basic Functionality...")
        
        try:
            # Add to path
            sys.path.insert(0, str(self.project_root / "supermanus"))
            sys.path.insert(0, str(self.project_root))
            
            # Test TaskSystemEnforcer initialization
            from task_enforcer import TaskSystemEnforcer
            
            # Create test session state if needed
            test_session_state = {
                "active_tasks": ["TEST.1: Validation test"],
                "completed_tasks": [],
                "project_name": "Validation Test"
            }
            
            # Test with existing or temporary session state
            session_file = self.project_root / "SESSION_STATE.json"
            if session_file.exists():
                enforcer = TaskSystemEnforcer(str(session_file))
                print("  ✅ TaskSystemEnforcer initialized with existing session")
            else:
                # Create temporary session for testing
                temp_session = self.project_root / "temp_session.json"
                with open(temp_session, 'w') as f:
                    json.dump(test_session_state, f)
                
                enforcer = TaskSystemEnforcer(str(temp_session))
                print("  ✅ TaskSystemEnforcer initialized with temporary session")
                
                # Cleanup
                temp_session.unlink()
            
            # Test LLMGuard
            from llm_guard import LLMGuard
            guard = LLMGuard(enforcer)
            print("  ✅ LLMGuard initialized successfully")
            
            self.validation_results["checks"]["functionality_test"] = True
            return True
            
        except Exception as e:
            print(f"  ❌ Basic functionality test failed: {e}")
            self.errors.append(f"Functionality test error: {e}")
            self.validation_results["checks"]["functionality_test"] = False
            return False
    
    def validate_documentation(self) -> bool:
        """Validate documentation files"""
        print("\n📚 Validating Documentation...")
        
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            print("  ⚠️  Documentation directory not found")
            self.warnings.append("Documentation directory missing")
            return False
        
        expected_docs = {
            "installation.md": "Installation guide",
            "integrations.md": "AI tool integrations guide",
            "human-review.md": "Human review process guide",
            "api.md": "API reference documentation"
        }
        
        docs_present = 0
        for doc_name, description in expected_docs.items():
            doc_path = docs_dir / doc_name
            if doc_path.exists():
                print(f"  ✅ {doc_name} - {description}")
                docs_present += 1
            else:
                print(f"  ⚠️  {doc_name} - Missing ({description})")
        
        print(f"  📊 Documentation coverage: {docs_present}/{len(expected_docs)} files")
        
        self.validation_results["checks"]["documentation_coverage"] = docs_present / len(expected_docs)
        return docs_present > 0
    
    def run_integration_checks(self) -> bool:
        """Run integration-specific validation checks"""
        print("\n🔗 Running Integration Checks...")
        
        integration_results = []
        
        # Check for integration config files
        integration_configs = {
            ".cursorrules.json": "Cursor IDE configuration",
            ".copilot-instructions.md": "GitHub Copilot instructions", 
            ".vscode/settings.json": "VS Code configuration"
        }
        
        for config_file, description in integration_configs.items():
            config_path = self.project_root / config_file
            if config_path.exists():
                print(f"  ✅ {config_file} - {description}")
                integration_results.append(True)
            else:
                print(f"  ⚠️  {config_file} - Not configured ({description})")
                integration_results.append(False)
        
        # Test integration imports if available
        try:
            sys.path.insert(0, str(self.project_root / "supermanus"))
            from integrations import claude_code_integration
            print("  ✅ Claude Code integration available")
            integration_results.append(True)
        except ImportError:
            print("  ⚠️  Claude Code integration not available")
            integration_results.append(False)
        
        success_rate = sum(integration_results) / len(integration_results) if integration_results else 0
        print(f"  📊 Integration readiness: {success_rate:.1%}")
        
        self.validation_results["checks"]["integration_readiness"] = success_rate
        return success_rate > 0.5
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        total_checks = len(self.validation_results["checks"])
        passed_checks = sum(1 for result in self.validation_results["checks"].values() 
                          if result is True)
        
        summary = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": len(self.errors),
            "warnings": len(self.warnings),
            "success_rate": (passed_checks / total_checks * 100) if total_checks > 0 else 0,
            "status": "PASS" if len(self.errors) == 0 else "FAIL",
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        self.validation_results["summary"] = summary
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("🏆 VALIDATION SUMMARY")
        print("=" * 60)
        
        status_color = "🟢" if summary["status"] == "PASS" else "🔴"
        print(f"{status_color} Overall Status: {summary['status']}")
        print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
        print(f"✅ Passed Checks: {summary['passed_checks']}/{summary['total_checks']}")
        
        if summary["failed_checks"] > 0:
            print(f"❌ Failed Checks: {summary['failed_checks']}")
        
        if summary["warnings"] > 0:
            print(f"⚠️  Warnings: {summary['warnings']}")
        
        # Print errors
        if self.errors:
            print(f"\n🚨 Critical Issues:")
            for error in self.errors:
                print(f"  • {error}")
        
        # Print warnings
        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Print recommendations
        print(f"\n💡 Recommendations:")
        if summary["status"] == "PASS":
            print("  • SuperManUS is properly installed and ready to use!")
            print("  • Start by customizing SESSION_STATE.json for your project")
            print("  • Run the demo: python3 supermanus/demo_enforcement.py")
        else:
            print("  • Fix critical issues before using SuperManUS")
            if not Path(self.project_root / "SESSION_STATE.json").exists():
                print("  • Create SESSION_STATE.json from template")
            if summary["failed_checks"] > 2:
                print("  • Consider reinstalling SuperManUS")
    
    def save_report(self, filename: str = "validation_report.json"):
        """Save validation report to file"""
        report_path = self.project_root / filename
        with open(report_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        print(f"\n💾 Validation report saved to: {report_path}")
    
    def run_full_validation(self, save_report: bool = True) -> bool:
        """Run complete validation suite"""
        self.print_header()
        
        # Run all validation checks
        validation_steps = [
            self.validate_core_files,
            self.validate_integrations, 
            self.validate_session_state,
            self.validate_templates,
            self.validate_configuration,
            self.validate_directory_structure,
            self.validate_python_imports,
            self.test_basic_functionality,
            self.validate_documentation,
            self.run_integration_checks
        ]
        
        for step in validation_steps:
            try:
                step()
            except Exception as e:
                print(f"  💥 Validation step failed: {e}")
                self.errors.append(f"Validation step error: {e}")
        
        # Generate and print summary
        summary = self.generate_summary()
        self.print_summary(summary)
        
        # Save report if requested
        if save_report:
            self.save_report()
        
        return summary["status"] == "PASS"


def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SuperManUS Installation Validator")
    parser.add_argument(
        "project_dir", 
        nargs="?", 
        default=".", 
        help="Project directory to validate (default: current directory)"
    )
    parser.add_argument(
        "--no-report", 
        action="store_true", 
        help="Don't save validation report file"
    )
    parser.add_argument(
        "--report-file",
        default="validation_report.json",
        help="Report filename (default: validation_report.json)"
    )
    
    args = parser.parse_args()
    
    # Run validation
    validator = SuperManUSValidator(args.project_dir)
    success = validator.run_full_validation(save_report=not args.no_report)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()