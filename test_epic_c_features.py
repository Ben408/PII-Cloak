#!/usr/bin/env python3
"""
Test Epic C Features - Report Generation and Performance Optimization
Tests the new reporting system and laptop-optimized processing
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

def test_report_generation():
    """Test the report generation system"""
    print("🧪 Testing Report Generation System...")
    
    try:
        from report_generator import ReportGenerator
        
        # Create sample data
        from dataclasses import dataclass
        
        @dataclass
        class FileInfo:
            filename: str
            file_type: str
            file_size: int
        
        @dataclass
        class PIIEntity:
            entity_type: str
            value: str
            confidence: float
            detection_method: str
            status: str
            start_pos: int
            end_pos: int
        
        @dataclass
        class ProcessingResult:
            file_info: FileInfo
            entities_found: list
            questionable_entities: list
            residual_entities: list
            processing_time: float
            errors: list
        
        # Sample processing results
        sample_results = [
            ProcessingResult(
                file_info=FileInfo("sample1.csv", "csv", 2048),
                entities_found=[
                    PIIEntity("EMAIL", "john.doe@example.com", 0.95, "rule-based", "auto_masked", 0, 20),
                    PIIEntity("PHONE", "555-123-4567", 0.92, "rule-based", "auto_masked", 25, 37),
                    PIIEntity("SSN", "123-45-6789", 0.98, "rule-based", "auto_masked", 42, 52)
                ],
                questionable_entities=[
                    PIIEntity("PERSON", "John Smith", 0.45, "ml", "questionable", 60, 70)
                ],
                residual_entities=[],
                processing_time=0.15,
                errors=[]
            ),
            ProcessingResult(
                file_info=FileInfo("sample2.docx", "docx", 4096),
                entities_found=[
                    PIIEntity("EMAIL", "jane.smith@company.com", 0.96, "rule-based", "auto_masked", 0, 25),
                    PIIEntity("CREDIT_CARD", "4111-1111-1111-1111", 0.99, "rule-based", "auto_masked", 30, 49)
                ],
                questionable_entities=[],
                residual_entities=[],
                processing_time=0.25,
                errors=[]
            )
        ]
        
        config = {
            "mask_format": "TOKEN",
            "enabled_entities": ["EMAIL", "PHONE", "SSN", "CREDIT_CARD", "PERSON"],
            "review_queue": True,
            "dry_run": False,
            "min_confidence": 0.35,
            "questionable_band": [0.35, 0.65]
        }
        
        # Create temporary directory for reports
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()
            
            # Generate reports
            html_path = generator.generate_html_report(sample_results, config, 
                                                     os.path.join(temp_dir, "test_report.html"))
            json_path = generator.generate_json_report(sample_results, config,
                                                     os.path.join(temp_dir, "test_report.json"))
            csv_path = generator.generate_csv_findings(sample_results,
                                                     os.path.join(temp_dir, "test_findings.csv"))
            
            # Verify files were created
            assert os.path.exists(html_path), "HTML report not created"
            assert os.path.exists(json_path), "JSON report not created"
            assert os.path.exists(csv_path), "CSV report not created"
            
            # Check file sizes
            assert os.path.getsize(html_path) > 1000, "HTML report too small"
            assert os.path.getsize(json_path) > 500, "JSON report too small"
            assert os.path.getsize(csv_path) > 100, "CSV report too small"
            
            print("✅ Report generation tests passed!")
            print(f"  • HTML Report: {os.path.getsize(html_path)} bytes")
            print(f"  • JSON Report: {os.path.getsize(json_path)} bytes")
            print(f"  • CSV Report: {os.path.getsize(csv_path)} bytes")
            
            return True
            
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return False

def test_performance_optimization():
    """Test the performance optimization system"""
    print("\n🧪 Testing Performance Optimization System...")
    
    try:
        from performance_optimizer import PerformanceOptimizer, LaptopOptimizedProcessor, PerformanceCaps
        
        # Test performance monitoring
        optimizer = PerformanceOptimizer()
        
        print("  Testing performance monitoring...")
        optimizer.start_monitoring()
        
        # Simulate some work
        time.sleep(1)
        
        # Get performance summary
        summary = optimizer.get_performance_summary()
        assert 'processing_time_seconds' in summary, "Performance summary missing processing time"
        
        # Stop monitoring
        metrics = optimizer.stop_monitoring()
        assert metrics is not None, "Performance metrics not returned"
        assert metrics.processing_time > 0, "Processing time should be positive"
        
        print("✅ Performance monitoring tests passed!")
        print(f"  • Processing time: {metrics.processing_time:.2f}s")
        print(f"  • Memory peak: {metrics.memory_peak_mb:.1f}MB")
        print(f"  • CPU peak: {metrics.cpu_peak_percent:.1f}%")
        
        # Test laptop optimizations
        print("  Testing laptop optimizations...")
        processor = LaptopOptimizedProcessor()
        
        optimizations = processor.optimizations
        assert 'processing_strategy' in optimizations, "Processing strategy not found"
        assert 'batch_size' in optimizations, "Batch size not found"
        assert 'concurrency' in optimizations, "Concurrency not found"
        
        print("✅ Laptop optimization tests passed!")
        print(f"  • Strategy: {optimizations['processing_strategy']}")
        print(f"  • Batch size: {optimizations['batch_size']}")
        print(f"  • Concurrency: {optimizations['concurrency']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance optimization test failed: {e}")
        return False

def test_caps_enforcement():
    """Test caps enforcement"""
    print("\n🧪 Testing Caps Enforcement...")
    
    try:
        from performance_optimizer import PerformanceOptimizer, PerformanceCaps
        
        # Create custom caps for testing
        test_caps = PerformanceCaps(
            max_csv_rows=100,
            max_xlsx_rows=100,
            max_pdf_pages=5,
            max_pdf_mb=1,
            max_file_mb=1
        )
        
        optimizer = PerformanceOptimizer(test_caps)
        
        # Create test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test CSV caps
            csv_path = os.path.join(temp_dir, "test.csv")
            with open(csv_path, 'w') as f:
                for i in range(150):  # Exceeds 100 row cap
                    f.write(f"row{i},data{i}\n")
            
            is_valid, errors = optimizer.validate_file_caps(csv_path)
            assert not is_valid, "CSV should fail validation (too many rows)"
            assert any("row count" in error for error in errors), "Row count error not found"
            
            # Test file size caps
            large_file_path = os.path.join(temp_dir, "large.txt")
            with open(large_file_path, 'w') as f:
                f.write('x' * (2 * 1024 * 1024))  # 2MB file
            
            is_valid, errors = optimizer.validate_file_caps(large_file_path)
            assert not is_valid, "Large file should fail validation"
            assert any("file size" in error.lower() for error in errors), "File size error not found"
            
            print("✅ Caps enforcement tests passed!")
            print(f"  • CSV validation: {len(errors)} errors detected")
            print(f"  • File size validation: {len(errors)} errors detected")
            
            return True
            
    except Exception as e:
        print(f"❌ Caps enforcement test failed: {e}")
        return False

def test_integration():
    """Test integration of all Epic C features"""
    print("\n🧪 Testing Epic C Integration...")
    
    try:
        from core import ReportGenerator, LaptopOptimizedProcessor, PerformanceCaps
        
        # Create a simple processing function that returns ProcessingResult-like objects
        def mock_processor(file_path):
            from dataclasses import dataclass
            
            @dataclass
            class MockFileInfo:
                filename: str
                file_type: str
                file_size: int
            
            @dataclass
            class MockProcessingResult:
                file_info: MockFileInfo
                entities_found: list
                questionable_entities: list
                residual_entities: list
                processing_time: float
                errors: list
            
            return MockProcessingResult(
                file_info=MockFileInfo(os.path.basename(file_path), "txt", 100),
                entities_found=[],
                questionable_entities=[],
                residual_entities=[],
                processing_time=0.1,
                errors=[]
            )
        
        # Test with performance optimization
        processor = LaptopOptimizedProcessor()
        
        # Create test files
        with tempfile.TemporaryDirectory() as temp_dir:
            test_files = []
            for i in range(3):
                file_path = os.path.join(temp_dir, f"test{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Test content {i}")
                test_files.append(file_path)
            
            # Process files
            results = processor.process_files(test_files, mock_processor)
            
            assert len(results) == 3, "Should process all 3 files"
            # Check that all results are valid (not error dictionaries)
            assert all(hasattr(result, 'file_info') for result in results), "All results should have file_info attribute"
            
            # Test report generation with results
            generator = ReportGenerator()
            config = {"test": True}
            
            html_path = generator.generate_html_report(results, config, 
                                                     os.path.join(temp_dir, "integration_report.html"))
            
            assert os.path.exists(html_path), "Integration report not created"
            
            print("✅ Epic C integration tests passed!")
            print(f"  • Files processed: {len(results)}")
            print(f"  • Report generated: {os.path.basename(html_path)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Epic C integration test failed: {e}")
        return False

def main():
    """Run all Epic C feature tests"""
    print("🚀 Testing Epic C Features - Report Generation & Performance Optimization")
    print("=" * 70)
    
    tests = [
        ("Report Generation", test_report_generation),
        ("Performance Optimization", test_performance_optimization),
        ("Caps Enforcement", test_caps_enforcement),
        ("Integration", test_integration)
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
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Epic C features working correctly!")
        return True
    else:
        print("⚠️ Some Epic C features need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
