#!/usr/bin/env python3
"""
Cloak & Style - PII Data Scrubber UI
Professional desktop application for PII masking
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                               QTextEdit, QProgressBar, QFileDialog, QMessageBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
                               QComboBox, QGroupBox, QSplitter, QFrame, QScrollArea)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QFont, QPalette, QColor

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

try:
    from detection_engine import PIIDetectionEngine, PIIEntity, DetectionResult
    from document_modifier import DocumentModifier, ModificationResult
    from report_generator import ReportGenerator
    from performance_optimizer import LaptopOptimizedProcessor, PerformanceCaps
except ImportError as e:
    print(f"Import error: {e}")
    # Create dummy classes for testing
    class PIIDetectionEngine:
        def __init__(self): pass
        def detect_pii(self, text): return None
    class DocumentModifier:
        def __init__(self, engine): pass
        def modify_file(self, file, output_dir): return None
    class ReportGenerator:
        def __init__(self): pass
        def generate_html_report(self, results, config, path): return path
        def generate_json_report(self, results, config, path): return path
        def generate_csv_findings(self, results, path): return path
    class LaptopOptimizedProcessor:
        def __init__(self): pass
        def process_files(self, files, func): return []

class ReviewQueueWidget(QWidget):
    """Review Queue for Accept/Reject functionality"""
    
    def __init__(self):
        super().__init__()
        self.entities = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Review Queue - Questionable Entities")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.accept_all_btn = QPushButton("Accept All")
        self.accept_all_btn.clicked.connect(self.accept_all)
        controls_layout.addWidget(self.accept_all_btn)
        
        self.reject_all_btn = QPushButton("Reject All")
        self.reject_all_btn.clicked.connect(self.reject_all)
        controls_layout.addWidget(self.reject_all_btn)
        
        self.clear_btn = QPushButton("Clear Queue")
        self.clear_btn.clicked.connect(self.clear_queue)
        controls_layout.addWidget(self.clear_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Entity table
        self.entity_table = QTableWidget()
        self.entity_table.setColumnCount(6)
        self.entity_table.setHorizontalHeaderLabels([
            "Entity Type", "Value", "Confidence", "Method", "Status", "Action"
        ])
        self.entity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.entity_table)
        
        self.setLayout(layout)
    
    def add_entities(self, entities):
        """Add entities to the review queue"""
        self.entities.extend(entities)
        self.update_table()
    
    def update_table(self):
        """Update the entity table"""
        self.entity_table.setRowCount(len(self.entities))
        
        for row, entity in enumerate(self.entities):
            # Entity type
            self.entity_table.setItem(row, 0, QTableWidgetItem(entity.entity_type))
            
            # Value (truncated for display)
            value = entity.value[:50] + "..." if len(entity.value) > 50 else entity.value
            self.entity_table.setItem(row, 1, QTableWidgetItem(value))
            
            # Confidence
            self.entity_table.setItem(row, 2, QTableWidgetItem(f"{entity.confidence:.2f}"))
            
            # Detection method
            self.entity_table.setItem(row, 3, QTableWidgetItem(entity.detection_method))
            
            # Status
            self.entity_table.setItem(row, 4, QTableWidgetItem(entity.status))
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            accept_btn = QPushButton("Accept")
            accept_btn.clicked.connect(lambda checked, row=row: self.accept_entity(row))
            action_layout.addWidget(accept_btn)
            
            reject_btn = QPushButton("Reject")
            reject_btn.clicked.connect(lambda checked, row=row: self.reject_entity(row))
            action_layout.addWidget(reject_btn)
            
            action_widget.setLayout(action_layout)
            self.entity_table.setCellWidget(row, 5, action_widget)
    
    def accept_entity(self, row):
        """Accept an entity"""
        if row < len(self.entities):
            self.entities[row].status = "accepted"
            self.update_table()
    
    def reject_entity(self, row):
        """Reject an entity"""
        if row < len(self.entities):
            self.entities[row].status = "rejected"
            self.update_table()
    
    def accept_all(self):
        """Accept all entities"""
        for entity in self.entities:
            entity.status = "accepted"
        self.update_table()
    
    def reject_all(self):
        """Reject all entities"""
        for entity in self.entities:
            entity.status = "rejected"
        self.update_table()
    
    def clear_queue(self):
        """Clear the review queue"""
        self.entities = []
        self.update_table()
    
    def get_accepted_entities(self):
        """Get all accepted entities"""
        return [e for e in self.entities if e.status == "accepted"]

class AdvancedOptionsWidget(QWidget):
    """Advanced options for processing"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Review Queue Options
        review_group = QGroupBox("Review Queue")
        review_layout = QVBoxLayout()
        
        self.enable_review_queue = QCheckBox("Enable Review Queue")
        self.enable_review_queue.setChecked(False)
        review_layout.addWidget(self.enable_review_queue)
        
        self.dry_run_mode = QCheckBox("Dry Run Mode (Preview Only)")
        self.dry_run_mode.setChecked(False)
        review_layout.addWidget(self.dry_run_mode)
        
        review_group.setLayout(review_layout)
        layout.addWidget(review_group)
        
        # Masking Options
        masking_group = QGroupBox("Masking Options")
        masking_layout = QVBoxLayout()
        
        masking_layout.addWidget(QLabel("Mask Format:"))
        self.mask_format = QComboBox()
        self.mask_format.addItems(["Token", "Asterisk", "Partial Reveal"])
        masking_layout.addWidget(self.mask_format)
        
        masking_group.setLayout(masking_layout)
        layout.addWidget(masking_group)
        
        # Entity Type Toggles
        entity_group = QGroupBox("Entity Type Toggles")
        entity_layout = QVBoxLayout()
        
        self.entity_toggles = {}
        entity_types = ["PERSON", "EMAIL", "PHONE", "SSN", "CREDIT_CARD", "IP_ADDRESS", "ADDRESS"]
        
        for entity_type in entity_types:
            checkbox = QCheckBox(entity_type)
            checkbox.setChecked(True)
            self.entity_toggles[entity_type] = checkbox
            entity_layout.addWidget(checkbox)
        
        entity_group.setLayout(entity_layout)
        layout.addWidget(entity_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_config(self):
        """Get current configuration"""
        return {
            "review_queue": self.enable_review_queue.isChecked(),
            "dry_run": self.dry_run_mode.isChecked(),
            "mask_format": self.mask_format.currentText().upper(),
            "enabled_entities": [entity for entity, checkbox in self.entity_toggles.items() 
                               if checkbox.isChecked()]
        }

class DiffPreviewWidget(QWidget):
    """Side-by-side diff preview"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Diff Preview")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header)
        
        # Split view
        splitter = QSplitter(Qt.Horizontal)
        
        # Original text
        original_group = QGroupBox("Original")
        original_layout = QVBoxLayout()
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        original_layout.addWidget(self.original_text)
        original_group.setLayout(original_layout)
        splitter.addWidget(original_group)
        
        # Masked text
        masked_group = QGroupBox("Masked")
        masked_layout = QVBoxLayout()
        self.masked_text = QTextEdit()
        self.masked_text.setReadOnly(True)
        masked_layout.addWidget(self.masked_text)
        masked_group.setLayout(masked_layout)
        splitter.addWidget(masked_group)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def set_texts(self, original, masked):
        """Set the original and masked texts"""
        self.original_text.setPlainText(original)
        self.masked_text.setPlainText(masked)
    
    def clear(self):
        """Clear the preview"""
        self.original_text.clear()
        self.masked_text.clear()

class ProgressWidget(QWidget):
    """Enhanced progress tracking with cancel capability"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.processing = False
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # File status list
        self.file_status = QTextEdit()
        self.file_status.setMaximumHeight(100)
        self.file_status.setReadOnly(True)
        layout.addWidget(self.file_status)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        button_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def start_processing(self):
        """Start processing files"""
        self.processing = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText("Processing...")
        self.file_status.clear()
    
    def cancel_processing(self):
        """Cancel processing"""
        self.processing = False
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText("Processing cancelled")
    
    def update_progress(self, value, status):
        """Update progress and status"""
        if self.processing:
            self.progress_bar.setValue(value)
            self.status_label.setText(status)
    
    def add_file_status(self, filename, status):
        """Add file status to the list"""
        self.file_status.append(f"{filename}: {status}")
    
    def processing_complete(self):
        """Mark processing as complete"""
        self.processing = False
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText("Processing complete")

class CloakAndStyleMainWindow(QMainWindow):
    """Main window for Cloak & Style application"""
    
    files_dropped = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.current_files = []
        self.detection_engine = None
        self.document_modifier = None
        self.review_queue = None
        self.report_generator = None
        self.performance_processor = None
        self.processing_results = []
        self.setup_ui()
        self.initialize_engine()
    
    def setup_ui(self):
        self.setWindowTitle("Cloak & Style - PII Data Scrubber")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Upload tab
        self.upload_tab = self.create_upload_tab()
        self.tab_widget.addTab(self.upload_tab, "Upload")
        
        # Options tab
        self.options_tab = self.create_options_tab()
        self.tab_widget.addTab(self.options_tab, "Options")
        
        # Review tab
        self.review_tab = self.create_review_tab()
        self.tab_widget.addTab(self.review_tab, "Review")
        
        # Results tab
        self.results_tab = self.create_results_tab()
        self.tab_widget.addTab(self.results_tab, "Results")
        
        main_layout.addWidget(self.tab_widget)
        
        # Progress widget
        self.progress_widget = ProgressWidget()
        main_layout.addWidget(self.progress_widget)
        
        central_widget.setLayout(main_layout)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def create_upload_tab(self):
        """Create the upload tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Upload Files for PII Scrubbing")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Drop zone
        self.drop_zone = QLabel("Drag and drop files here\nor click to browse")
        self.drop_zone.setAlignment(Qt.AlignCenter)
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                background-color: #f9f9f9;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #0078d4;
                background-color: #f0f8ff;
            }
        """)
        self.drop_zone.mousePressEvent = lambda event: self.browse_files()
        layout.addWidget(self.drop_zone)
        
        # File list
        self.file_list = QTextEdit()
        self.file_list.setMaximumHeight(150)
        self.file_list.setReadOnly(True)
        self.file_list.setPlaceholderText("No files selected")
        layout.addWidget(self.file_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        browse_btn = QPushButton("Browse Files")
        browse_btn.clicked.connect(self.browse_files)
        button_layout.addWidget(browse_btn)
        
        clear_btn = QPushButton("Clear Files")
        clear_btn.clicked.connect(self.clear_files)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_options_tab(self):
        """Create the options tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Processing Options")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Advanced options
        self.advanced_options = AdvancedOptionsWidget()
        layout.addWidget(self.advanced_options)
        
        widget.setLayout(layout)
        return widget
    
    def create_review_tab(self):
        """Create the review tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Review Queue")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Split view
        splitter = QSplitter(Qt.Horizontal)
        
        # Review queue
        self.review_queue = ReviewQueueWidget()
        splitter.addWidget(self.review_queue)
        
        # Diff preview
        self.diff_preview = DiffPreviewWidget()
        splitter.addWidget(self.diff_preview)
        
        layout.addWidget(splitter)
        widget.setLayout(layout)
        return widget
    
    def create_results_tab(self):
        """Create the results tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Processing Results")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Results text
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        open_output_btn = QPushButton("Open Output Folder")
        open_output_btn.clicked.connect(self.open_output_folder)
        button_layout.addWidget(open_output_btn)
        
        export_report_btn = QPushButton("Export Report")
        export_report_btn.clicked.connect(self.export_report)
        button_layout.addWidget(export_report_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def initialize_engine(self):
        """Initialize the detection engine"""
        try:
            self.detection_engine = PIIDetectionEngine()
            self.document_modifier = DocumentModifier(self.detection_engine)
            self.report_generator = ReportGenerator()
            self.performance_processor = LaptopOptimizedProcessor()
            print("✅ Detection engine initialized successfully")
        except Exception as e:
            print(f"⚠️ Error initializing detection engine: {e}")
            QMessageBox.warning(self, "Warning", 
                              f"Detection engine initialization failed: {e}\n"
                              "Some features may not work properly.")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_zone.setStyleSheet("""
                QLabel {
                    border: 2px dashed #0078d4;
                    border-radius: 10px;
                    padding: 40px;
                    background-color: #f0f8ff;
                    font-size: 14px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                background-color: #f9f9f9;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #0078d4;
                background-color: #f0f8ff;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                files.append(file_path)
        
        if files:
            self.add_files(files)
        
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                background-color: #f9f9f9;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #0078d4;
                background-color: #f0f8ff;
            }
        """)
    
    def browse_files(self, event=None):
        """Browse for files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "All Files (*.txt *.csv *.docx *.pptx *.xlsx *.pdf *.md *.log)"
        )
        
        if files:
            self.add_files(files)
    
    def add_files(self, files):
        """Add files to the list"""
        self.current_files.extend(files)
        self.update_file_list()
    
    def clear_files(self):
        """Clear the file list"""
        self.current_files = []
        self.update_file_list()
    
    def update_file_list(self):
        """Update the file list display"""
        if self.current_files:
            file_text = "\n".join([os.path.basename(f) for f in self.current_files])
            self.file_list.setPlainText(file_text)
        else:
            self.file_list.clear()
    
    def start_processing(self):
        """Start processing files"""
        if not self.current_files:
            QMessageBox.warning(self, "No Files", "Please select files to process.")
            return
        
        # Get configuration
        config = self.advanced_options.get_config()
        
        # Start processing
        self.progress_widget.start_processing()
        self.process_files(config)
    
    def process_files(self, config):
        """Process the selected files with performance optimization and reporting"""
        total_files = len(self.current_files)
        self.processing_results = []
        
        # Use performance-optimized processing
        def process_single_file(file_path):
            filename = os.path.basename(file_path)
            
            try:
                if config["dry_run"]:
                    # Dry run - just detect PII
                    result = self.detect_pii_in_file(file_path)
                    if result and result.questionable_entities:
                        self.review_queue.add_entities(result.questionable_entities)
                    
                    self.progress_widget.add_file_status(filename, "Preview completed")
                    return result
                else:
                    # Actual processing
                    output_dir = os.path.dirname(file_path)
                    modification_result = self.document_modifier.modify_file(file_path, output_dir)
                    
                    if modification_result.errors:
                        self.progress_widget.add_file_status(filename, f"Error: {modification_result.errors[0]}")
                    else:
                        self.progress_widget.add_file_status(filename, "Successfully processed")
                    
                    return modification_result
                
            except Exception as e:
                self.progress_widget.add_file_status(filename, f"Error: {str(e)}")
                return {'error': str(e), 'file': filename}
        
        # Process files with performance optimization
        try:
            results = self.performance_processor.process_files(self.current_files, process_single_file)
            self.processing_results = results
            
            # Generate reports
            if self.report_generator and results:
                self.generate_reports(config)
            
        except Exception as e:
            QMessageBox.critical(self, "Processing Error", f"Error during processing: {str(e)}")
        
        self.progress_widget.processing_complete()
        self.tab_widget.setCurrentIndex(3)  # Switch to results tab
    
    def generate_reports(self, config):
        """Generate HTML, JSON, and CSV reports"""
        try:
            # Create reports directory
            reports_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Generate reports
            html_path = self.report_generator.generate_html_report(
                self.processing_results, config, 
                os.path.join(reports_dir, f"pii_report_{timestamp}.html")
            )
            
            json_path = self.report_generator.generate_json_report(
                self.processing_results, config,
                os.path.join(reports_dir, f"pii_report_{timestamp}.json")
            )
            
            csv_path = self.report_generator.generate_csv_findings(
                self.processing_results,
                os.path.join(reports_dir, f"pii_findings_{timestamp}.csv")
            )
            
            # Update results display
            self.results_text.setPlainText(
                f"Processing completed successfully!\n\n"
                f"Files processed: {len(self.current_files)}\n"
                f"Reports generated:\n"
                f"  • HTML Report: {os.path.basename(html_path)}\n"
                f"  • JSON Report: {os.path.basename(json_path)}\n"
                f"  • CSV Findings: {os.path.basename(csv_path)}\n\n"
                f"Reports saved to: {reports_dir}"
            )
            
            # Store report paths for later access
            self.current_reports = {
                'html': html_path,
                'json': json_path,
                'csv': csv_path,
                'directory': reports_dir
            }
            
        except Exception as e:
            QMessageBox.warning(self, "Report Generation Error", 
                              f"Error generating reports: {str(e)}")
            self.results_text.setPlainText(f"Processing completed with report generation errors: {str(e)}")
    
    def detect_pii_in_file(self, file_path):
        """Detect PII in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.detection_engine.detect_pii(content)
        except Exception as e:
            print(f"Error detecting PII in {file_path}: {e}")
            return None
    
    def open_output_folder(self):
        """Open the output folder"""
        if self.current_files:
            output_dir = os.path.dirname(self.current_files[0])
            os.startfile(output_dir)
    
    def export_report(self):
        """Export processing report"""
        if hasattr(self, 'current_reports') and self.current_reports:
            try:
                # Open the reports directory
                os.startfile(self.current_reports['directory'])
                QMessageBox.information(self, "Reports Exported", 
                                      f"Reports opened in folder:\n{self.current_reports['directory']}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Error opening reports folder: {str(e)}")
        else:
            QMessageBox.information(self, "No Reports", "No reports available to export. Please process files first.")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = CloakAndStyleMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
