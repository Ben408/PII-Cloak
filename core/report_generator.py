#!/usr/bin/env python3
"""
Report Generator for Cloak & Style
Generates HTML, JSON, and CSV reports for PII processing results
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict, is_dataclass

try:
    from .detection_engine import PIIEntity, DetectionResult
    from .file_processor import ProcessingResult
    from .document_modifier import ModificationResult
except ImportError:
    from detection_engine import PIIEntity, DetectionResult
    from file_processor import ProcessingResult
    from document_modifier import ModificationResult

class ReportGenerator:
    """Generates comprehensive reports for PII processing results"""
    
    def __init__(self):
        self.html_template = self._get_html_template()
        self.css_styles = self._get_css_styles()
    
    def generate_html_report(self, results: List[ProcessingResult], 
                           config: Dict[str, Any], output_path: str) -> str:
        """Generate human-readable HTML report"""
        
        # Prepare data for HTML template
        report_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_files': len(results),
            'total_entities': sum(len(r.entities_found) for r in results),
            'total_questionable': sum(len(r.questionable_entities) for r in results),
            'total_residual': sum(len(r.residual_entities) for r in results),
            'config_snapshot': config,
            'results': results,
            'entity_summary': self._generate_entity_summary(results),
            'confidence_histogram': self._generate_confidence_histogram(results),
            'file_summary': self._generate_file_summary(results)
        }
        
        # Generate HTML content
        html_content = self.html_template.format(
            css_styles=self.css_styles,
            timestamp=report_data['timestamp'],
            total_files=report_data['total_files'],
            total_entities=report_data['total_entities'],
            total_questionable=report_data['total_questionable'],
            total_residual=report_data['total_residual'],
            entity_summary_html=self._format_entity_summary_html(report_data['entity_summary']),
            confidence_histogram_html=self._format_confidence_histogram_html(report_data['confidence_histogram']),
            file_details_html=self._format_file_details_html(report_data['file_summary']),
            config_json=self._format_config_json(report_data['config_snapshot'])
        )
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_json_report(self, results: List[ProcessingResult], 
                           config: Dict[str, Any], output_path: str) -> str:
        """Generate machine-readable JSON report"""
        
        # Convert dataclasses to dictionaries
        report_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'tool': 'Cloak & Style'
            },
            'config': config,
            'summary': {
                'total_files': len(results),
                'total_entities': sum(len(r.entities_found) for r in results),
                'total_questionable': sum(len(r.questionable_entities) for r in results),
                'total_residual': sum(len(r.residual_entities) for r in results),
                'entity_summary': self._generate_entity_summary(results),
                'confidence_histogram': self._generate_confidence_histogram(results)
            },
            'results': [self._convert_dataclass_to_dict(r) for r in results]
        }
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def generate_csv_findings(self, results: List[ProcessingResult], 
                            output_path: str) -> str:
        """Generate CSV findings report"""
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'File', 'Entity_Type', 'Value', 'Confidence', 'Method', 
                'Status', 'Start_Pos', 'End_Pos', 'Processing_Time'
            ])
            
            # Write findings
            for result in results:
                for entity in result.entities_found:
                    writer.writerow([
                        os.path.basename(result.file_info.path),
                        entity.entity_type,
                        entity.value,
                        f"{entity.confidence:.3f}",
                        entity.detection_method,
                        entity.status,
                        entity.start_pos,
                        entity.end_pos,
                        f"{result.processing_time:.3f}"
                    ])
        
        return output_path
    
    def _generate_entity_summary(self, results: List[ProcessingResult]) -> Dict[str, int]:
        """Generate summary of entity types found"""
        summary = {}
        for result in results:
            for entity in result.entities_found:
                entity_type = entity.entity_type
                summary[entity_type] = summary.get(entity_type, 0) + 1
        return summary
    
    def _generate_confidence_histogram(self, results: List[ProcessingResult]) -> Dict[str, int]:
        """Generate confidence score histogram"""
        histogram = {
            '0.0-0.2': 0, '0.2-0.4': 0, '0.4-0.6': 0, 
            '0.6-0.8': 0, '0.8-1.0': 0
        }
        
        for result in results:
            for entity in result.entities_found:
                conf = entity.confidence
                if conf < 0.2:
                    histogram['0.0-0.2'] += 1
                elif conf < 0.4:
                    histogram['0.2-0.4'] += 1
                elif conf < 0.6:
                    histogram['0.4-0.6'] += 1
                elif conf < 0.8:
                    histogram['0.6-0.8'] += 1
                else:
                    histogram['0.8-1.0'] += 1
        
        return histogram
    
    def _generate_file_summary(self, results: List[ProcessingResult]) -> List[Dict[str, Any]]:
        """Generate summary for each file"""
        file_summary = []
        for result in results:
            file_summary.append({
                'filename': os.path.basename(result.file_info.path),
                'file_type': result.file_info.file_type,
                'file_size': result.file_info.file_size,
                'entities_found': len(result.entities_found),
                'questionable_entities': len(result.questionable_entities),
                'residual_entities': len(result.residual_entities),
                'processing_time': result.processing_time,
                'status': 'Success' if not result.errors else 'Error',
                'errors': result.errors
            })
        return file_summary
    
    def _convert_dataclass_to_dict(self, obj):
        """Convert dataclass objects to dictionaries"""
        if is_dataclass(obj):
            return asdict(obj)
        elif isinstance(obj, list):
            return [self._convert_dataclass_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_dataclass_to_dict(v) for k, v in obj.items()}
        else:
            return obj
    
    def _get_html_template(self) -> str:
        """Get HTML template for reports"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloak & Style - PII Processing Report</title>
    <style>
        {css_styles}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Cloak & Style - PII Processing Report</h1>
            <p class="timestamp">Generated: {timestamp}</p>
        </header>
        
        <section class="summary">
            <h2>Processing Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="label">Files Processed:</span>
                    <span class="value">{total_files}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Total Entities:</span>
                    <span class="value">{total_entities}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Questionable Entities:</span>
                    <span class="value">{total_questionable}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Residual Entities:</span>
                    <span class="value">{total_residual}</span>
                </div>
            </div>
        </section>
        
        <section class="entity-summary">
            <h2>Entity Type Summary</h2>
            <div class="entity-grid">
                {entity_summary_html}
            </div>
        </section>
        
        <section class="confidence-histogram">
            <h2>Confidence Distribution</h2>
            <div class="histogram">
                {confidence_histogram_html}
            </div>
        </section>
        
        <section class="file-details">
            <h2>File Processing Details</h2>
            <div class="file-table">
                {file_details_html}
            </div>
        </section>
        
        <section class="config">
            <h2>Configuration Snapshot</h2>
            <pre class="config-json">{config_json}</pre>
        </section>
        
        <footer>
            <p>Report generated by Cloak & Style - PII Data Scrubber</p>
            <p class="privacy-note">This report contains no raw PII data - only tokens and metadata for audit purposes.</p>
        </footer>
    </div>
</body>
</html>
"""
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for HTML reports"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .timestamp {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        section {
            padding: 2rem;
            border-bottom: 1px solid #eee;
        }
        
        section h2 {
            color: #2c3e50;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .summary-item {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        
        .summary-item .label {
            display: block;
            font-weight: 600;
            color: #6c757d;
            margin-bottom: 0.5rem;
        }
        
        .summary-item .value {
            display: block;
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .entity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
        
        .entity-item {
            background: #e3f2fd;
            padding: 1rem;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #bbdefb;
        }
        
        .entity-count {
            font-size: 1.5rem;
            font-weight: bold;
            color: #1976d2;
        }
        
        .entity-type {
            font-size: 0.9rem;
            color: #424242;
            margin-top: 0.5rem;
        }
        
        .histogram {
            display: flex;
            align-items: end;
            height: 200px;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .histogram-bar {
            flex: 1;
            background: linear-gradient(to top, #4caf50, #8bc34a);
            border-radius: 4px 4px 0 0;
            position: relative;
            min-width: 60px;
        }
        
        .histogram-label {
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.8rem;
            color: #666;
        }
        
        .histogram-value {
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-weight: bold;
            color: #2c3e50;
        }
        
        .file-table {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        .status-success {
            color: #28a745;
            font-weight: 600;
        }
        
        .status-error {
            color: #dc3545;
            font-weight: 600;
        }
        
        .config-json {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            overflow-x: auto;
            border: 1px solid #dee2e6;
        }
        
        footer {
            background: #f8f9fa;
            padding: 2rem;
            text-align: center;
            color: #6c757d;
        }
        
        .privacy-note {
            margin-top: 1rem;
            font-style: italic;
            color: #495057;
        }
        
        @media (max-width: 768px) {
            .summary-grid {
                grid-template-columns: 1fr;
            }
            
            .entity-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .histogram {
                flex-direction: column;
                height: auto;
                align-items: stretch;
            }
            
            .histogram-bar {
                height: 40px;
                margin-bottom: 30px;
            }
        }
        """
    
    def _format_entity_summary_html(self, summary: Dict[str, int]) -> str:
        """Format entity summary for HTML"""
        html = ""
        for entity_type, count in summary.items():
            html += f"""
            <div class="entity-item">
                <div class="entity-count">{count}</div>
                <div class="entity-type">{entity_type}</div>
            </div>
            """
        return html
    
    def _format_confidence_histogram_html(self, histogram: Dict[str, int]) -> str:
        """Format confidence histogram for HTML"""
        max_count = max(histogram.values()) if histogram.values() else 1
        
        html = ""
        for range_label, count in histogram.items():
            height_percent = (count / max_count) * 100 if max_count > 0 else 0
            html += f"""
            <div class="histogram-bar" style="height: {height_percent}%;">
                <div class="histogram-value">{count}</div>
                <div class="histogram-label">{range_label}</div>
            </div>
            """
        return html
    
    def _format_file_details_html(self, file_summary: List[Dict[str, Any]]) -> str:
        """Format file details for HTML"""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Filename</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Entities</th>
                    <th>Questionable</th>
                    <th>Residual</th>
                    <th>Time (s)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for file_info in file_summary:
            status_class = "status-success" if file_info['status'] == 'Success' else "status-error"
            html += f"""
            <tr>
                <td>{file_info['filename']}</td>
                <td>{file_info['file_type']}</td>
                <td>{self._format_file_size(file_info['file_size'])}</td>
                <td>{file_info['entities_found']}</td>
                <td>{file_info['questionable_entities']}</td>
                <td>{file_info['residual_entities']}</td>
                <td>{file_info['processing_time']:.3f}</td>
                <td class="{status_class}">{file_info['status']}</td>
            </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        return html
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _format_config_json(self, config: Dict[str, Any]) -> str:
        """Format configuration as JSON for HTML display"""
        return json.dumps(config, indent=2, ensure_ascii=False)

# Test the report generator
if __name__ == "__main__":
    # Create sample data for testing
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
    
    # Sample data
    sample_results = [
        ProcessingResult(
            file_info=FileInfo("sample.csv", "csv", 1024),
            entities_found=[
                PIIEntity("EMAIL", "test@example.com", 0.95, "rule-based", "auto_masked", 0, 15),
                PIIEntity("PHONE", "555-123-4567", 0.92, "rule-based", "auto_masked", 20, 32)
            ],
            questionable_entities=[],
            residual_entities=[],
            processing_time=0.15,
            errors=[]
        )
    ]
    
    config = {
        "mask_format": "TOKEN",
        "enabled_entities": ["EMAIL", "PHONE", "SSN"],
        "review_queue": True,
        "dry_run": False
    }
    
    # Test report generation
    generator = ReportGenerator()
    
    # Generate reports
    html_path = generator.generate_html_report(sample_results, config, "test_report.html")
    json_path = generator.generate_json_report(sample_results, config, "test_report.json")
    csv_path = generator.generate_csv_findings(sample_results, "test_findings.csv")
    
    print(f"✅ Reports generated:")
    print(f"  HTML: {html_path}")
    print(f"  JSON: {json_path}")
    print(f"  CSV: {csv_path}")
