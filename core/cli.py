#!/usr/bin/env python3
"""
CLI Implementation for Cloak & Style
Implements Epic E requirements for batch processing and command-line interface
"""

import argparse
import sys
import os
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

try:
    from .detection_engine import PIIDetectionEngine
    from .file_processor import FileProcessor
    from .document_modifier import DocumentModifier
    from .report_generator import ReportGenerator
    from .performance_optimizer import LaptopOptimizedProcessor, PerformanceCaps
except ImportError:
    from detection_engine import PIIDetectionEngine
    from file_processor import FileProcessor
    from document_modifier import DocumentModifier
    from report_generator import ReportGenerator
    from performance_optimizer import LaptopOptimizedProcessor, PerformanceCaps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloakAndStyleCLI:
    """Command-line interface for Cloak & Style PII Data Scrubber"""
    
    def __init__(self):
        self.detection_engine = None
        self.file_processor = None
        self.document_modifier = None
        self.report_generator = None
        self.performance_processor = None
        
        # Exit codes as per requirements
        self.EXIT_SUCCESS = 0
        self.EXIT_POLICY_VIOLATION = 2
        self.EXIT_FATAL_ERROR = 3
        
        # Processing results
        self.results = []
        self.policy_violations = []
        self.fatal_errors = []
    
    def initialize_engine(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the processing engine"""
        try:
            logger.info("Initializing Cloak & Style engine...")
            
            # Initialize components
            self.detection_engine = PIIDetectionEngine(config)
            self.file_processor = FileProcessor(self.detection_engine)
            self.document_modifier = DocumentModifier(self.detection_engine)
            self.report_generator = ReportGenerator()
            self.performance_processor = LaptopOptimizedProcessor()
            
            logger.info("Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize engine: {e}")
            self.fatal_errors.append(f"Engine initialization failed: {e}")
            return False
    
    def collect_files(self, input_path: str, recursive: bool = False, 
                     include_patterns: Optional[List[str]] = None,
                     exclude_patterns: Optional[List[str]] = None) -> List[str]:
        """Collect files to process based on input path and patterns"""
        files = []
        input_path = Path(input_path)
        
        if input_path.is_file():
            # Single file
            if self._should_process_file(input_path, include_patterns, exclude_patterns):
                files.append(str(input_path))
        elif input_path.is_dir():
            # Directory
            if recursive:
                # Recursive search
                for pattern in include_patterns or ["*"]:
                    pattern_path = input_path / "**" / pattern
                    files.extend([
                        str(f) for f in input_path.rglob(pattern)
                        if f.is_file() and self._should_process_file(f, include_patterns, exclude_patterns)
                    ])
            else:
                # Non-recursive search
                for pattern in include_patterns or ["*"]:
                    pattern_path = input_path / pattern
                    files.extend([
                        str(f) for f in input_path.glob(pattern)
                        if f.is_file() and self._should_process_file(f, include_patterns, exclude_patterns)
                    ])
        else:
            raise FileNotFoundError(f"Input path not found: {input_path}")
        
        # Remove duplicates and sort
        files = sorted(list(set(files)))
        logger.info(f"Collected {len(files)} files to process")
        return files
    
    def _should_process_file(self, file_path: Path, include_patterns: Optional[List[str]] = None,
                           exclude_patterns: Optional[List[str]] = None) -> bool:
        """Check if file should be processed based on patterns"""
        filename = file_path.name.lower()
        
        # Check include patterns
        if include_patterns:
            if not any(self._matches_pattern(filename, pattern) for pattern in include_patterns):
                return False
        
        # Check exclude patterns
        if exclude_patterns:
            if any(self._matches_pattern(filename, pattern) for pattern in exclude_patterns):
                return False
        
        return True
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches glob pattern"""
        return glob.fnmatch.fnmatch(filename, pattern.lower())
    
    def process_single_file(self, file_path: str, output_dir: str, dry_run: bool = False) -> Dict[str, Any]:
        """Process a single file"""
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Process file
            result = self.file_processor.process_file(file_path)
            
            if result.errors:
                logger.warning(f"Errors processing {file_path}: {result.errors}")
                return {
                    'file_path': file_path,
                    'status': 'error',
                    'errors': result.errors,
                    'processing_time': result.processing_time
                }
            
            # Modify document if not dry run
            if not dry_run:
                modification_result = self.document_modifier.modify_file(
                    file_path, output_dir
                )
                
                if modification_result.errors:
                    logger.warning(f"Errors modifying {file_path}: {modification_result.errors}")
                    return {
                        'file_path': file_path,
                        'status': 'modification_error',
                        'errors': modification_result.errors,
                        'processing_time': result.processing_time
                    }
                
                return {
                    'file_path': file_path,
                    'status': 'success',
                    'entities_found': len(result.entities_found),
                    'questionable_entities': len(result.questionable_entities),
                    'residual_entities': len(result.residual_entities),
                    'output_file': modification_result.modified_file,
                    'processing_time': result.processing_time
                }
            else:
                # Dry run - just return detection results
                return {
                    'file_path': file_path,
                    'status': 'dry_run',
                    'entities_found': len(result.entities_found),
                    'questionable_entities': len(result.questionable_entities),
                    'residual_entities': len(result.residual_entities),
                    'processing_time': result.processing_time
                }
                
        except Exception as e:
            logger.error(f"Fatal error processing {file_path}: {e}")
            self.fatal_errors.append(f"Fatal error processing {file_path}: {e}")
            return {
                'file_path': file_path,
                'status': 'fatal_error',
                'errors': [str(e)],
                'processing_time': 0.0
            }
    
    def process_files(self, files: List[str], output_dir: str, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Process multiple files using performance optimization"""
        logger.info(f"Processing {len(files)} files (dry_run={dry_run})")
        
        # Use performance processor for optimized batch processing
        results = self.performance_processor.process_files(
            files, 
            lambda file_path: self.process_single_file(file_path, output_dir, dry_run)
        )
        
        # Analyze results for policy violations
        for result in results:
            if result.get('status') == 'fatal_error':
                self.fatal_errors.append(result.get('errors', ['Unknown fatal error']))
            elif result.get('status') == 'error':
                # Check for policy violations
                errors = result.get('errors', [])
                if any('caps exceeded' in error.lower() for error in errors):
                    self.policy_violations.append(f"Caps exceeded: {result['file_path']}")
                elif any('image-only' in error.lower() for error in errors):
                    self.policy_violations.append(f"Image-only PDF: {result['file_path']}")
        
        return results
    
    def generate_reports(self, results: List[Dict[str, Any]], output_dir: str, 
                        report_formats: List[str], config: Dict[str, Any]) -> Dict[str, str]:
        """Generate reports in specified formats"""
        report_files = {}
        
        # Convert CLI results to ProcessingResult format for report generator
        processing_results = self._convert_to_processing_results(results)
        
        if 'html' in report_formats:
            html_path = os.path.join(output_dir, "cloak_and_style_report.html")
            self.report_generator.generate_html_report(processing_results, config, html_path)
            report_files['html'] = html_path
        
        if 'json' in report_formats:
            json_path = os.path.join(output_dir, "cloak_and_style_report.json")
            self.report_generator.generate_json_report(processing_results, config, json_path)
            report_files['json'] = json_path
        
        if 'csv' in report_formats:
            csv_path = os.path.join(output_dir, "cloak_and_style_findings.csv")
            self.report_generator.generate_csv_findings(processing_results, csv_path)
            report_files['csv'] = csv_path
        
        return report_files
    
    def _convert_to_processing_results(self, results: List[Dict[str, Any]]) -> List[Any]:
        """Convert CLI results to ProcessingResult format for report generator"""
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
            entities_found: List[PIIEntity]
            questionable_entities: List[PIIEntity]
            residual_entities: List[PIIEntity]
            processing_time: float
            errors: List[str]
        
        processing_results = []
        
        for result in results:
            file_path = result['file_path']
            file_info = FileInfo(
                filename=os.path.basename(file_path),
                file_type=os.path.splitext(file_path)[1][1:].lower(),
                file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0
            )
            
            # Create dummy entities for reporting (actual entities would come from detection)
            entities_found = []
            questionable_entities = []
            residual_entities = []
            
            processing_result = ProcessingResult(
                file_info=file_info,
                entities_found=entities_found,
                questionable_entities=questionable_entities,
                residual_entities=residual_entities,
                processing_time=result.get('processing_time', 0.0),
                errors=result.get('errors', [])
            )
            
            processing_results.append(processing_result)
        
        return processing_results
    
    def determine_exit_code(self, exit_on_violations: List[str]) -> int:
        """Determine exit code based on violations and configuration"""
        if self.fatal_errors:
            return self.EXIT_FATAL_ERROR
        
        # Check for policy violations that should cause exit
        for violation_type in exit_on_violations:
            if violation_type == 'image-only-pdf':
                if any('Image-only PDF' in violation for violation in self.policy_violations):
                    return self.EXIT_POLICY_VIOLATION
            elif violation_type == 'caps-exceeded':
                if any('Caps exceeded' in violation for violation in self.policy_violations):
                    return self.EXIT_POLICY_VIOLATION
            elif violation_type == 'residuals':
                # Check for residual PII in results
                for result in self.results:
                    if result.get('residual_entities', 0) > 0:
                        return self.EXIT_POLICY_VIOLATION
        
        return self.EXIT_SUCCESS

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Cloak & Style - PII Data Scrubber",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  python -m core.cli run --in "document.docx" --out "output/"

  # Process directory recursively
  python -m core.cli run --in "documents/" --out "output/" --recursive

  # Dry run with specific file types
  python -m core.cli run --in "data/" --out "output/" --include "*.csv,*.xlsx" --dry-run

  # Generate all report formats
  python -m core.cli run --in "files/" --out "output/" --report html,json,csv
        """
    )
    
    # Main command
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run PII detection and masking')
    
    # Required arguments
    run_parser.add_argument('--in', dest='input_path', required=True,
                          help='Input file or directory path')
    run_parser.add_argument('--out', dest='output_dir', required=True,
                          help='Output directory path')
    
    # Optional arguments
    run_parser.add_argument('--recursive', action='store_true',
                          help='Process directories recursively')
    run_parser.add_argument('--include', dest='include_patterns',
                          help='File patterns to include (comma-separated, e.g., "*.docx,*.pdf")')
    run_parser.add_argument('--exclude', dest='exclude_patterns',
                          help='File patterns to exclude (comma-separated)')
    
    # Modes
    run_parser.add_argument('--dry-run', action='store_true',
                          help='Generate findings without modifying files')
    run_parser.add_argument('--review-queue', choices=['on', 'off'], default='off',
                          help='Enable review queue (default: off)')
    
    # Reporting
    run_parser.add_argument('--report', dest='report_formats',
                          default='html,json',
                          help='Report formats to generate (comma-separated: html,json,csv)')
    
    # Exit conditions
    run_parser.add_argument('--exit-on', dest='exit_on_violations',
                          help='Exit codes for policy violations (comma-separated: image-only-pdf,caps-exceeded,residuals)')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command != 'run':
        parser.print_help()
        return 1
    
    # Initialize CLI
    cli = CloakAndStyleCLI()
    
    # Parse patterns
    include_patterns = args.include_patterns.split(',') if args.include_patterns else None
    exclude_patterns = args.exclude_patterns.split(',') if args.exclude_patterns else None
    report_formats = args.report_formats.split(',') if args.report_formats else ['html', 'json']
    exit_on_violations = args.exit_on_violations.split(',') if args.exit_on_violations else []
    
    try:
        # Initialize engine
        if not cli.initialize_engine():
            return cli.EXIT_FATAL_ERROR
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect files
        files = cli.collect_files(
            args.input_path, 
            recursive=args.recursive,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns
        )
        
        if not files:
            logger.warning("No files found to process")
            return cli.EXIT_SUCCESS
        
        # Process files
        config = {
            'dry_run': args.dry_run,
            'review_queue': args.review_queue == 'on',
            'report_formats': report_formats
        }
        
        results = cli.process_files(files, str(output_dir), dry_run=args.dry_run)
        cli.results = results
        
        # Generate reports
        report_files = cli.generate_reports(results, str(output_dir), report_formats, config)
        
        # Print summary
        successful = sum(1 for r in results if r['status'] == 'success')
        errors = sum(1 for r in results if r['status'] in ['error', 'fatal_error'])
        
        logger.info(f"Processing complete: {successful} successful, {errors} errors")
        
        if report_files:
            logger.info(f"Reports generated: {', '.join(report_files.keys())}")
        
        # Determine exit code
        exit_code = cli.determine_exit_code(exit_on_violations)
        
        if exit_code == cli.EXIT_POLICY_VIOLATION:
            logger.warning("Policy violations detected - exiting with code 2")
        elif exit_code == cli.EXIT_FATAL_ERROR:
            logger.error("Fatal errors occurred - exiting with code 3")
        
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return cli.EXIT_FATAL_ERROR
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return cli.EXIT_FATAL_ERROR

if __name__ == "__main__":
    sys.exit(main())
