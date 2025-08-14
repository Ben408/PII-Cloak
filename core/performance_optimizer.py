#!/usr/bin/env python3
"""
Performance Optimizer for Cloak & Style
Implements caps enforcement and memory management for laptop-grade equipment
"""

import os
import psutil
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceCaps:
    """Performance caps for laptop-grade equipment"""
    # File size limits
    max_csv_rows: int = 100_000
    max_xlsx_rows: int = 100_000
    max_pdf_pages: int = 100
    max_pdf_mb: int = 10
    max_file_mb: int = 50
    
    # Memory limits (8GB laptop profile)
    max_memory_mb: int = 6000  # Leave 2GB for system
    max_memory_percent: float = 75.0
    
    # Processing time limits
    max_processing_time_seconds: int = 300  # 5 minutes
    
    # Batch limits
    max_batch_files: int = 50
    max_concurrent_files: int = 3

@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    start_time: float
    memory_start_mb: float
    cpu_start_percent: float
    file_count: int = 0
    total_entities: int = 0
    processing_time: float = 0.0
    memory_peak_mb: float = 0.0
    cpu_peak_percent: float = 0.0

class PerformanceOptimizer:
    """Performance optimization and monitoring for laptop-grade equipment"""
    
    def __init__(self, caps: Optional[PerformanceCaps] = None):
        self.caps = caps or PerformanceCaps()
        self.metrics = None
        self.monitoring = False
        self.monitor_thread = None
        self.stop_monitoring_event = threading.Event()
        
        # Performance tracking
        self.current_memory_mb = 0
        self.current_cpu_percent = 0
        self.peak_memory_mb = 0
        self.peak_cpu_percent = 0
    
    def start_monitoring(self) -> PerformanceMetrics:
        """Start performance monitoring"""
        if self.monitoring:
            return self.metrics
        
        self.monitoring = True
        self.stop_monitoring_event.clear()
        
        # Initialize metrics
        self.metrics = PerformanceMetrics(
            start_time=time.time(),
            memory_start_mb=self._get_memory_usage_mb(),
            cpu_start_percent=self._get_cpu_usage_percent()
        )
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_performance)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Performance monitoring started")
        return self.metrics
    
    def stop_monitoring(self) -> Optional[PerformanceMetrics]:
        """Stop performance monitoring and return final metrics"""
        if not self.monitoring:
            return None
        
        self.stop_monitoring_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.monitoring = False
        
        if self.metrics:
            self.metrics.processing_time = time.time() - self.metrics.start_time
            self.metrics.memory_peak_mb = self.peak_memory_mb
            self.metrics.cpu_peak_percent = self.peak_cpu_percent
        
        logger.info("Performance monitoring stopped")
        return self.metrics
    
    def _monitor_performance(self):
        """Background thread for performance monitoring"""
        while not self.stop_monitoring_event.is_set():
            try:
                # Update current metrics
                self.current_memory_mb = self._get_memory_usage_mb()
                self.current_cpu_percent = self._get_cpu_usage_percent()
                
                # Track peaks
                self.peak_memory_mb = max(self.peak_memory_mb, self.current_memory_mb)
                self.peak_cpu_percent = max(self.peak_cpu_percent, self.current_cpu_percent)
                
                # Check for violations
                self._check_performance_violations()
                
                time.sleep(1)  # Monitor every second
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                break
    
    def _check_performance_violations(self):
        """Check for performance violations"""
        # Memory violations
        if self.current_memory_mb > self.caps.max_memory_mb:
            logger.warning(f"Memory usage ({self.current_memory_mb:.1f}MB) exceeds cap ({self.caps.max_memory_mb}MB)")
        
        memory_percent = (self.current_memory_mb / self._get_total_memory_mb()) * 100
        if memory_percent > self.caps.max_memory_percent:
            logger.warning(f"Memory usage ({memory_percent:.1f}%) exceeds cap ({self.caps.max_memory_percent}%)")
        
        # CPU violations
        if self.current_cpu_percent > 90:  # High CPU usage
            logger.warning(f"High CPU usage detected: {self.current_cpu_percent:.1f}%")
    
    def validate_file_caps(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate file against performance caps"""
        errors = []
        file_path = Path(file_path)
        
        if not file_path.exists():
            errors.append(f"File not found: {file_path}")
            return False, errors
        
        # File size check
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.caps.max_file_mb:
            errors.append(f"File size ({file_size_mb:.1f}MB) exceeds cap ({self.caps.max_file_mb}MB)")
        
        # File type specific checks
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.csv':
            row_count = self._count_csv_rows(file_path)
            if row_count > self.caps.max_csv_rows:
                errors.append(f"CSV row count ({row_count:,}) exceeds cap ({self.caps.max_csv_rows:,})")
        
        elif file_extension == '.xlsx':
            row_count = self._count_xlsx_rows(file_path)
            if row_count > self.caps.max_xlsx_rows:
                errors.append(f"XLSX row count ({row_count:,}) exceeds cap ({self.caps.max_xlsx_rows:,})")
        
        elif file_extension == '.pdf':
            page_count = self._count_pdf_pages(file_path)
            if page_count > self.caps.max_pdf_pages:
                errors.append(f"PDF page count ({page_count}) exceeds cap ({self.caps.max_pdf_pages})")
            
            if file_size_mb > self.caps.max_pdf_mb:
                errors.append(f"PDF file size ({file_size_mb:.1f}MB) exceeds cap ({self.caps.max_pdf_mb}MB)")
        
        return len(errors) == 0, errors
    
    def validate_batch_caps(self, file_paths: List[str]) -> Tuple[bool, List[str]]:
        """Validate batch processing against caps"""
        errors = []
        
        # Batch size check
        if len(file_paths) > self.caps.max_batch_files:
            errors.append(f"Batch size ({len(file_paths)}) exceeds cap ({self.caps.max_batch_files})")
        
        # Individual file checks
        for file_path in file_paths:
            is_valid, file_errors = self.validate_file_caps(file_path)
            if not is_valid:
                errors.extend(file_errors)
        
        return len(errors) == 0, errors
    
    def optimize_for_laptop(self) -> Dict[str, Any]:
        """Apply laptop-specific optimizations"""
        optimizations = {
            'memory_management': self._optimize_memory(),
            'processing_strategy': self._optimize_processing_strategy(),
            'batch_size': self._calculate_optimal_batch_size(),
            'concurrency': self._calculate_optimal_concurrency()
        }
        
        logger.info(f"Applied laptop optimizations: {optimizations}")
        return optimizations
    
    def _optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage for laptop"""
        total_memory_mb = self._get_total_memory_mb()
        available_memory_mb = self._get_available_memory_mb()
        
        # Calculate safe memory limits
        safe_memory_mb = min(available_memory_mb * 0.8, self.caps.max_memory_mb)
        
        return {
            'total_memory_mb': total_memory_mb,
            'available_memory_mb': available_memory_mb,
            'safe_memory_mb': safe_memory_mb,
            'chunk_size_mb': min(50, safe_memory_mb * 0.1),  # 10% of safe memory or 50MB
            'enable_streaming': available_memory_mb < 4000  # Enable streaming if < 4GB available
        }
    
    def _optimize_processing_strategy(self) -> str:
        """Determine optimal processing strategy"""
        available_memory_mb = self._get_available_memory_mb()
        cpu_count = psutil.cpu_count()
        
        if available_memory_mb < 2000:  # Very low memory
            return "sequential_streaming"
        elif available_memory_mb < 4000:  # Low memory
            return "sequential_buffered"
        elif cpu_count >= 4:  # Multi-core
            return "parallel_limited"
        else:  # Single core or low core count
            return "sequential_optimized"
    
    def _calculate_optimal_batch_size(self) -> int:
        """Calculate optimal batch size based on system resources"""
        available_memory_mb = self._get_available_memory_mb()
        
        if available_memory_mb < 2000:
            return 5
        elif available_memory_mb < 4000:
            return 10
        elif available_memory_mb < 8000:
            return 20
        else:
            return min(50, self.caps.max_batch_files)
    
    def _calculate_optimal_concurrency(self) -> int:
        """Calculate optimal concurrency based on system resources"""
        cpu_count = psutil.cpu_count()
        available_memory_mb = self._get_available_memory_mb()
        
        # Conservative approach for laptop
        if available_memory_mb < 2000:
            return 1
        elif available_memory_mb < 4000:
            return min(2, cpu_count)
        else:
            return min(3, cpu_count, self.caps.max_concurrent_files)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        if not self.metrics:
            return {}
        
        return {
            'processing_time_seconds': self.metrics.processing_time,
            'files_processed': self.metrics.file_count,
            'total_entities': self.metrics.total_entities,
            'memory_peak_mb': self.metrics.memory_peak_mb,
            'cpu_peak_percent': self.metrics.cpu_peak_percent,
            'memory_efficiency': self._calculate_memory_efficiency(),
            'performance_score': self._calculate_performance_score()
        }
    
    def _calculate_memory_efficiency(self) -> float:
        """Calculate memory efficiency (lower is better)"""
        if not self.metrics or self.metrics.processing_time == 0:
            return 0.0
        
        # MB-seconds per entity (lower is better)
        return (self.metrics.memory_peak_mb * self.metrics.processing_time) / max(1, self.metrics.total_entities)
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        if not self.metrics:
            return 0.0
        
        # Factors: processing speed, memory efficiency, CPU usage
        speed_score = min(100, (1000 / max(1, self.metrics.processing_time)))  # Faster = higher score
        memory_score = max(0, 100 - (self.metrics.memory_peak_mb / 100))  # Less memory = higher score
        cpu_score = max(0, 100 - self.metrics.cpu_peak_percent)  # Less CPU = higher score
        
        return (speed_score * 0.4 + memory_score * 0.3 + cpu_score * 0.3)
    
    # System monitoring methods
    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    
    def _get_total_memory_mb(self) -> float:
        """Get total system memory in MB"""
        return psutil.virtual_memory().total / (1024 * 1024)
    
    def _get_available_memory_mb(self) -> float:
        """Get available system memory in MB"""
        return psutil.virtual_memory().available / (1024 * 1024)
    
    def _get_cpu_usage_percent(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    # File analysis methods
    def _count_csv_rows(self, file_path: Path) -> int:
        """Count rows in CSV file"""
        try:
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in csv.reader(f))
        except Exception as e:
            logger.warning(f"Could not count CSV rows: {e}")
            return 0
    
    def _count_xlsx_rows(self, file_path: Path) -> int:
        """Count rows in XLSX file"""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True)
            total_rows = 0
            for sheet in wb.worksheets:
                total_rows += sheet.max_row
            wb.close()
            return total_rows
        except Exception as e:
            logger.warning(f"Could not count XLSX rows: {e}")
            return 0
    
    def _count_pdf_pages(self, file_path: Path) -> int:
        """Count pages in PDF file"""
        try:
            import fitz
            doc = fitz.open(str(file_path))
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception as e:
            logger.warning(f"Could not count PDF pages: {e}")
            return 0

class LaptopOptimizedProcessor:
    """Laptop-optimized file processor with performance monitoring"""
    
    def __init__(self, caps: Optional[PerformanceCaps] = None):
        self.optimizer = PerformanceOptimizer(caps)
        self.optimizations = self.optimizer.optimize_for_laptop()
    
    def process_files(self, file_paths: List[str], processor_func) -> List[Any]:
        """Process files with laptop optimizations"""
        # Validate batch
        is_valid, errors = self.optimizer.validate_batch_caps(file_paths)
        if not is_valid:
            raise ValueError(f"Batch validation failed: {'; '.join(errors)}")
        
        # Start monitoring
        self.optimizer.start_monitoring()
        
        try:
            results = []
            strategy = self.optimizations['processing_strategy']
            
            if strategy == "sequential_streaming":
                results = self._process_sequential_streaming(file_paths, processor_func)
            elif strategy == "sequential_buffered":
                results = self._process_sequential_buffered(file_paths, processor_func)
            elif strategy == "parallel_limited":
                results = self._process_parallel_limited(file_paths, processor_func)
            else:  # sequential_optimized
                results = self._process_sequential_optimized(file_paths, processor_func)
            
            return results
            
        finally:
            # Stop monitoring and get metrics
            metrics = self.optimizer.stop_monitoring()
            if metrics:
                logger.info(f"Processing completed: {metrics.file_count} files, "
                          f"{metrics.total_entities} entities, "
                          f"{metrics.processing_time:.2f}s")
    
    def _process_sequential_streaming(self, file_paths: List[str], processor_func) -> List[Any]:
        """Process files sequentially with streaming for low memory"""
        results = []
        for file_path in file_paths:
            try:
                result = processor_func(file_path)
                results.append(result)
                self.optimizer.metrics.file_count += 1
                
                # Force garbage collection after each file
                import gc
                gc.collect()
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results.append({'error': str(e), 'file': file_path})
        
        return results
    
    def _process_sequential_buffered(self, file_paths: List[str], processor_func) -> List[Any]:
        """Process files sequentially with buffering"""
        results = []
        batch_size = self.optimizations['batch_size']
        
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            
            for file_path in batch:
                try:
                    result = processor_func(file_path)
                    results.append(result)
                    self.optimizer.metrics.file_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results.append({'error': str(e), 'file': file_path})
            
            # Garbage collection between batches
            import gc
            gc.collect()
        
        return results
    
    def _process_parallel_limited(self, file_paths: List[str], processor_func) -> List[Any]:
        """Process files with limited parallelism"""
        import concurrent.futures
        
        max_workers = self.optimizations['concurrency']
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(processor_func, file_path): file_path 
                            for file_path in file_paths}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.optimizer.metrics.file_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results.append({'error': str(e), 'file': file_path})
        
        return results
    
    def _process_sequential_optimized(self, file_paths: List[str], processor_func) -> List[Any]:
        """Process files with optimized sequential processing"""
        results = []
        
        for file_path in file_paths:
            try:
                result = processor_func(file_path)
                results.append(result)
                self.optimizer.metrics.file_count += 1
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results.append({'error': str(e), 'file': file_path})
        
        return results
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return self.optimizer.get_performance_summary()

# Test the performance optimizer
if __name__ == "__main__":
    # Test performance monitoring
    optimizer = PerformanceOptimizer()
    
    print("Starting performance monitoring...")
    optimizer.start_monitoring()
    
    # Simulate some work
    import time
    time.sleep(2)
    
    # Get performance summary
    summary = optimizer.get_performance_summary()
    print(f"Performance summary: {summary}")
    
    # Stop monitoring
    metrics = optimizer.stop_monitoring()
    print(f"Final metrics: {metrics}")
    
    # Test laptop optimizations
    processor = LaptopOptimizedProcessor()
    optimizations = processor.optimizations
    print(f"Laptop optimizations: {optimizations}")
