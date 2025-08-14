#!/usr/bin/env python3
"""
Core module for Cloak & Style PII Data Scrubber
"""

from .detection_engine import PIIDetectionEngine, PIIEntity, DetectionResult
from .file_processor import FileProcessor, FileInfo, ProcessingResult
from .document_modifier import DocumentModifier, ModificationResult
from .report_generator import ReportGenerator
from .performance_optimizer import PerformanceOptimizer, PerformanceCaps, PerformanceMetrics, LaptopOptimizedProcessor
from .cli import CloakAndStyleCLI

__all__ = [
    # Detection
    'PIIDetectionEngine',
    'PIIEntity', 
    'DetectionResult',
    
    # File Processing
    'FileProcessor',
    'FileInfo',
    'ProcessingResult',
    
    # Document Modification
    'DocumentModifier',
    'ModificationResult',
    
    # Reporting
    'ReportGenerator',
    
    # Performance
    'PerformanceOptimizer',
    'PerformanceCaps',
    'PerformanceMetrics',
    'LaptopOptimizedProcessor',
    
    # CLI
    'CloakAndStyleCLI'
]
