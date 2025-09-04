#!/usr/bin/env python3
"""
SuperManUS Test Runner
Comprehensive test suite runner with reporting
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
from datetime import datetime


class SuperManUSTestRunner:
    """Test runner for SuperManUS TaskEnforcer"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        self.results = {
            "start_time": datetime.now().isoformat(),
            "unit_tests": {},
            "integration_tests": {},
            "coverage": {},
            "summary": {}
        }
    
    def run_unit_tests(self, verbose=False):
        """Run all unit tests"""
        print("🧪 Running Unit Tests...")
        print("=" * 50)
        
        unit_test_dir = self.test_dir / "unit"
        test_files = list(unit_test_dir.glob("test_*.py"))
        
        for test_file in test_files:
            print(f"\n📋 Running {test_file.name}...")
            
            cmd = [
                sys.executable, "-m", "pytest", 
                str(test_file), 
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header"
            ]
            
            try:
                result = subprocess.run(
                    cmd, 
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                self.results["unit_tests"][test_file.name] = {
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "status": "PASSED" if result.returncode == 0 else "FAILED"
                }
                
                if result.returncode == 0:
                    print(f"  ✅ {test_file.name} - PASSED")
                else:
                    print(f"  ❌ {test_file.name} - FAILED")
                    if verbose:
                        print(f"  Error: {result.stderr}")
                        
            except subprocess.TimeoutExpired:
                print(f"  ⏰ {test_file.name} - TIMEOUT")
                self.results["unit_tests"][test_file.name] = {
                    "status": "TIMEOUT",
                    "error": "Test execution timed out"
                }
            except Exception as e:
                print(f"  💥 {test_file.name} - ERROR: {e}")
                self.results["unit_tests"][test_file.name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
    
    def run_integration_tests(self, verbose=False):
        """Run all integration tests"""
        print("\n🔗 Running Integration Tests...")
        print("=" * 50)
        
        integration_test_dir = self.test_dir / "integration"
        test_files = list(integration_test_dir.glob("test_*.py"))
        
        for test_file in test_files:
            print(f"\n📋 Running {test_file.name}...")
            
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_file),
                "-v" if verbose else "-q", 
                "--tb=short",
                "--no-header"
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300  # Longer timeout for integration tests
                )
                
                self.results["integration_tests"][test_file.name] = {
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "status": "PASSED" if result.returncode == 0 else "FAILED"
                }
                
                if result.returncode == 0:
                    print(f"  ✅ {test_file.name} - PASSED")
                else:
                    print(f"  ❌ {test_file.name} - FAILED")
                    if verbose:
                        print(f"  Error: {result.stderr}")
                        
            except subprocess.TimeoutExpired:
                print(f"  ⏰ {test_file.name} - TIMEOUT")
                self.results["integration_tests"][test_file.name] = {
                    "status": "TIMEOUT",
                    "error": "Integration test execution timed out"
                }
            except Exception as e:
                print(f"  💥 {test_file.name} - ERROR: {e}")
                self.results["integration_tests"][test_file.name] = {
                    "status": "ERROR", 
                    "error": str(e)
                }
    
    def run_coverage_analysis(self):
        """Run test coverage analysis"""
        print("\n📊 Running Coverage Analysis...")
        print("=" * 50)
        
        # Install coverage if not available
        try:
            import coverage
        except ImportError:
            print("  Installing coverage...")
            subprocess.run([sys.executable, "-m", "pip", "install", "coverage"])
        
        try:
            # Run tests with coverage
            cmd = [
                sys.executable, "-m", "coverage", "run",
                "-m", "pytest", "tests/", "-q"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                # Generate coverage report
                report_cmd = [
                    sys.executable, "-m", "coverage", "report", 
                    "--format=markdown"
                ]
                
                report_result = subprocess.run(
                    report_cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                self.results["coverage"] = {
                    "status": "COMPLETED",
                    "report": report_result.stdout
                }
                
                print("  ✅ Coverage analysis completed")
                print(f"  📄 Coverage report:\n{report_result.stdout}")
            else:
                print(f"  ❌ Coverage analysis failed: {result.stderr}")
                self.results["coverage"] = {
                    "status": "FAILED",
                    "error": result.stderr
                }
                
        except Exception as e:
            print(f"  💥 Coverage analysis error: {e}")
            self.results["coverage"] = {
                "status": "ERROR",
                "error": str(e)
            }
    
    def validate_installation(self):
        """Validate SuperManUS installation"""
        print("\n🔍 Validating Installation...")
        print("=" * 50)
        
        validation_checks = []
        
        # Check core files exist
        core_files = [
            "task_enforcer.py",
            "llm_guard.py", 
            "demo_enforcement.py"
        ]
        
        for file_name in core_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                validation_checks.append(f"✅ {file_name} exists")
            else:
                validation_checks.append(f"❌ {file_name} missing")
        
        # Check integrations directory
        integrations_dir = self.project_root / "integrations"
        if integrations_dir.exists():
            integration_files = list(integrations_dir.glob("*.py"))
            validation_checks.append(f"✅ Integrations directory with {len(integration_files)} files")
        else:
            validation_checks.append("❌ Integrations directory missing")
        
        # Check example project
        example_dir = self.project_root / "example_project"
        if example_dir.exists() and (example_dir / "SESSION_STATE.json").exists():
            validation_checks.append("✅ Example project with SESSION_STATE.json")
        else:
            validation_checks.append("❌ Example project incomplete")
        
        # Check documentation
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            doc_files = list(docs_dir.glob("*.md"))
            validation_checks.append(f"✅ Documentation with {len(doc_files)} files")
        else:
            validation_checks.append("❌ Documentation missing")
        
        # Test basic imports
        try:
            sys.path.insert(0, str(self.project_root))
            from task_enforcer import TaskSystemEnforcer
            validation_checks.append("✅ TaskSystemEnforcer import successful")
        except Exception as e:
            validation_checks.append(f"❌ TaskSystemEnforcer import failed: {e}")
        
        try:
            from llm_guard import LLMGuard
            validation_checks.append("✅ LLMGuard import successful")
        except Exception as e:
            validation_checks.append(f"❌ LLMGuard import failed: {e}")
        
        for check in validation_checks:
            print(f"  {check}")
        
        return validation_checks
    
    def generate_summary(self):
        """Generate test summary"""
        unit_passed = sum(1 for result in self.results["unit_tests"].values() 
                         if result.get("status") == "PASSED")
        unit_total = len(self.results["unit_tests"])
        
        integration_passed = sum(1 for result in self.results["integration_tests"].values()
                               if result.get("status") == "PASSED")
        integration_total = len(self.results["integration_tests"])
        
        self.results["summary"] = {
            "unit_tests": f"{unit_passed}/{unit_total}",
            "integration_tests": f"{integration_passed}/{integration_total}",
            "total_passed": unit_passed + integration_passed,
            "total_tests": unit_total + integration_total,
            "success_rate": round((unit_passed + integration_passed) / max(unit_total + integration_total, 1) * 100, 1)
        }
        
        self.results["end_time"] = datetime.now().isoformat()
    
    def print_summary(self):
        """Print test execution summary"""
        print("\n" + "=" * 60)
        print("🏆 SUPERMANUS TEST SUMMARY")
        print("=" * 60)
        
        summary = self.results["summary"]
        print(f"📊 Unit Tests:        {summary['unit_tests']}")
        print(f"🔗 Integration Tests: {summary['integration_tests']}")
        print(f"✨ Total Success:     {summary['total_passed']}/{summary['total_tests']} ({summary['success_rate']}%)")
        
        if summary["success_rate"] >= 90:
            print("🎉 Excellent! SuperManUS is working great!")
        elif summary["success_rate"] >= 70:
            print("👍 Good! Most tests passing, minor issues to address")
        elif summary["success_rate"] >= 50:
            print("⚠️  Moderate success rate, several issues need attention")
        else:
            print("🚨 Low success rate, significant issues need to be resolved")
        
        print(f"\n⏱️  Test Duration: {self.results['start_time']} - {self.results['end_time']}")
    
    def save_results(self, output_file="test_results.json"):
        """Save test results to file"""
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to {output_path}")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="SuperManUS Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests") 
    parser.add_argument("--coverage", action="store_true", help="Run coverage analysis")
    parser.add_argument("--validate", action="store_true", help="Validate installation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", default="test_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    runner = SuperManUSTestRunner()
    
    print("🛡️  SuperManUS TaskEnforcer Test Suite")
    print("=" * 60)
    
    # Run validation if requested or by default
    if args.validate or not any([args.unit, args.integration, args.coverage]):
        runner.validate_installation()
    
    # Run tests based on arguments
    if args.unit or not any([args.unit, args.integration, args.coverage]):
        runner.run_unit_tests(verbose=args.verbose)
    
    if args.integration or not any([args.unit, args.integration, args.coverage]):
        runner.run_integration_tests(verbose=args.verbose)
    
    if args.coverage:
        runner.run_coverage_analysis()
    
    # Generate and display summary
    runner.generate_summary()
    runner.print_summary()
    
    # Save results
    runner.save_results(args.output)
    
    # Exit with appropriate code
    success_rate = runner.results["summary"]["success_rate"]
    exit_code = 0 if success_rate >= 70 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()