#!/usr/bin/env python3
"""
Test CLI Implementation - Epic E
Tests the command-line interface functionality
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

def test_cli_help():
    """Test CLI help functionality"""
    print("🧪 Testing CLI Help...")
    
    try:
        # Test main help
        result = subprocess.run([
            sys.executable, '-m', 'core.cli', '--help'
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0, "Help command should return 0"
        assert "Cloak & Style - PII Data Scrubber" in result.stdout, "Help should contain tool name"
        assert "run" in result.stdout, "Help should mention run command"
        
        # Test run help
        result = subprocess.run([
            sys.executable, '-m', 'core.cli', 'run', '--help'
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0, "Run help should return 0"
        assert "--in" in result.stdout, "Run help should mention --in"
        assert "--out" in result.stdout, "Run help should mention --out"
        assert "--dry-run" in result.stdout, "Run help should mention --dry-run"
        
        print("✅ CLI help tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ CLI help test failed: {e}")
        return False

def test_cli_file_collection():
    """Test CLI file collection functionality"""
    print("\n🧪 Testing CLI File Collection...")
    
    try:
        from core.cli import CloakAndStyleCLI
        
        cli = CloakAndStyleCLI()
        
        # Create test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = [
                "document1.docx",
                "document2.pdf", 
                "data.csv",
                "report.xlsx",
                "notes.txt"
            ]
            
            for filename in test_files:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w') as f:
                    f.write(f"Test content for {filename}")
            
            # Test single file
            files = cli.collect_files(os.path.join(temp_dir, "document1.docx"))
            assert len(files) == 1, "Should collect single file"
            assert "document1.docx" in files[0], "Should find correct file"
            
            # Test directory (non-recursive)
            files = cli.collect_files(temp_dir)
            assert len(files) == 5, "Should collect all files in directory"
            
            # Test with include patterns
            files = cli.collect_files(temp_dir, include_patterns=["*.docx", "*.pdf"])
            assert len(files) == 2, "Should collect only docx and pdf files"
            
            # Test with exclude patterns
            files = cli.collect_files(temp_dir, exclude_patterns=["*.txt"])
            assert len(files) == 4, "Should exclude txt files"
            
            print("✅ CLI file collection tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ CLI file collection test failed: {e}")
        return False

def test_cli_engine_initialization():
    """Test CLI engine initialization"""
    print("\n🧪 Testing CLI Engine Initialization...")
    
    try:
        from core.cli import CloakAndStyleCLI
        
        cli = CloakAndStyleCLI()
        
        # Test initialization
        success = cli.initialize_engine()
        assert success, "Engine should initialize successfully"
        
        # Check components are initialized
        assert cli.detection_engine is not None, "Detection engine should be initialized"
        assert cli.file_processor is not None, "File processor should be initialized"
        assert cli.document_modifier is not None, "Document modifier should be initialized"
        assert cli.report_generator is not None, "Report generator should be initialized"
        assert cli.performance_processor is not None, "Performance processor should be initialized"
        
        print("✅ CLI engine initialization tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ CLI engine initialization test failed: {e}")
        return False

def test_cli_exit_codes():
    """Test CLI exit code determination"""
    print("\n🧪 Testing CLI Exit Codes...")
    
    try:
        from core.cli import CloakAndStyleCLI
        
        cli = CloakAndStyleCLI()
        
        # Test success exit code
        exit_code = cli.determine_exit_code([])
        assert exit_code == cli.EXIT_SUCCESS, "Should return success for no violations"
        
        # Test policy violation exit code
        cli.policy_violations.append("Caps exceeded: test.pdf")
        exit_code = cli.determine_exit_code(['caps-exceeded'])
        assert exit_code == cli.EXIT_POLICY_VIOLATION, "Should return policy violation for caps exceeded"
        
        # Test fatal error exit code
        cli.fatal_errors.append("Fatal error occurred")
        exit_code = cli.determine_exit_code([])
        assert exit_code == cli.EXIT_FATAL_ERROR, "Should return fatal error when fatal errors exist"
        
        print("✅ CLI exit code tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ CLI exit code test failed: {e}")
        return False

def test_cli_integration():
    """Test CLI integration with actual processing"""
    print("\n🧪 Testing CLI Integration...")
    
    try:
        from core.cli import CloakAndStyleCLI
        
        cli = CloakAndStyleCLI()
        
        # Initialize engine
        assert cli.initialize_engine(), "Engine should initialize"
        
        # Create test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file with PII
            test_file = os.path.join(temp_dir, "test.csv")
            with open(test_file, 'w') as f:
                f.write("Name,Email,Phone\n")
                f.write("John Doe,john.doe@example.com,555-123-4567\n")
            
            # Create output directory
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Test dry run
            results = cli.process_files([test_file], output_dir, dry_run=True)
            assert len(results) == 1, "Should process one file"
            assert results[0]['status'] == 'dry_run', "Should be dry run status"
            
            # Test actual processing
            results = cli.process_files([test_file], output_dir, dry_run=False)
            assert len(results) == 1, "Should process one file"
            assert results[0]['status'] == 'success', "Should be success status"
            
            # Test report generation
            config = {'dry_run': False, 'review_queue': False}
            report_files = cli.generate_reports(results, output_dir, ['html', 'json'], config)
            assert 'html' in report_files, "Should generate HTML report"
            assert 'json' in report_files, "Should generate JSON report"
            
            print("✅ CLI integration tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False

def main():
    """Run all CLI tests"""
    print("🚀 Testing CLI Implementation - Epic E")
    print("=" * 60)
    
    tests = [
        ("CLI Help", test_cli_help),
        ("File Collection", test_cli_file_collection),
        ("Engine Initialization", test_cli_engine_initialization),
        ("Exit Codes", test_cli_exit_codes),
        ("Integration", test_cli_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 CLI implementation working correctly!")
        return True
    else:
        print("⚠️ Some CLI features need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
