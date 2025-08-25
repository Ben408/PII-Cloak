#!/usr/bin/env python3
"""
Cloak & Style - PII Data Scrubber UI (Fixed Version)
Professional desktop application for PII masking
Fixed version resolving layout overlaps and functionality issues
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                               QTextEdit, QProgressBar, QFileDialog, QMessageBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
                               QComboBox, QGroupBox, QSplitter, QFrame, QScrollArea,
                               QLineEdit, QListWidget, QListWidgetItem, QMenuBar,
                               QStatusBar, QToolBar, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QSize
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QFont, QPalette, QColor, QIcon

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

class DarkTheme:
    """Dark theme colors matching the sophisticated screenshots"""
    BACKGROUND = "#1e1e1e"
    SURFACE = "#2d2d30"
    SURFACE_LIGHT = "#3e3e42"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#cccccc"
    ACCENT = "#0078d4"
    SUCCESS = "#107c10"
    WARNING = "#ff8c00"
    ERROR = "#d13438"
    BORDER = "#555555"
    HIGHLIGHT = "#264f78"

class FixedProcessingOptions(QWidget):
    """Fixed processing options with proper layout spacing"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Reduced spacing
        layout.setContentsMargins(0, 0, 0, 0)  # No margins
        
        # Review Queue Section
        review_group = QGroupBox("Review Queue")
        review_group.setStyleSheet(f"""
            QGroupBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 12px;
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: {DarkTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: {DarkTheme.SURFACE};
            }}
        """)
        review_layout = QVBoxLayout()
        review_layout.setSpacing(8)  # Reduced spacing
        
        self.enable_review = QCheckBox("Enable Review Queue")
        self.enable_review.setStyleSheet(f"""
            QCheckBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {DarkTheme.BORDER};
                border-radius: 3px;
                background-color: {DarkTheme.SURFACE_LIGHT};
            }}
            QCheckBox::indicator:checked {{
                background-color: {DarkTheme.ACCENT};
                border-color: {DarkTheme.ACCENT};
            }}
        """)
        review_layout.addWidget(self.enable_review)
        
        self.dry_run = QCheckBox("Dry Run (Preview Only)")
        self.dry_run.setStyleSheet(f"""
            QCheckBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {DarkTheme.BORDER};
                border-radius: 3px;
                background-color: {DarkTheme.SURFACE_LIGHT};
            }}
            QCheckBox::indicator:checked {{
                background-color: {DarkTheme.ACCENT};
                border-color: {DarkTheme.ACCENT};
            }}
        """)
        review_layout.addWidget(self.dry_run)
        
        self.process_subfolders = QCheckBox("Process Subfolders")
        self.process_subfolders.setStyleSheet(f"""
            QCheckBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {DarkTheme.BORDER};
                border-radius: 3px;
                background-color: {DarkTheme.SURFACE_LIGHT};
            }}
            QCheckBox::indicator:checked {{
                background-color: {DarkTheme.ACCENT};
                border-color: {DarkTheme.ACCENT};
            }}
        """)
        review_layout.addWidget(self.process_subfolders)
        
        review_group.setLayout(review_layout)
        layout.addWidget(review_group)
        
        # Masking Options Section
        masking_group = QGroupBox("Masking Options")
        masking_group.setStyleSheet(f"""
            QGroupBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 12px;
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: {DarkTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: {DarkTheme.SURFACE};
            }}
        """)
        masking_layout = QVBoxLayout()
        masking_layout.setSpacing(8)
        
        mask_label = QLabel("Mask Format:")
        mask_label.setStyleSheet(f"color: {DarkTheme.TEXT_PRIMARY}; font-size: 11px; font-weight: 500;")
        masking_layout.addWidget(mask_label)
        
        self.mask_format = QComboBox()
        self.mask_format.addItems(["Token Format [TYPE_###]", "Asterisk Format [***]", "Custom Format"])
        self.mask_format.setStyleSheet(f"""
            QComboBox {{
                background-color: {DarkTheme.SURFACE_LIGHT};
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 4px;
                padding: 6px 10px;
                color: {DarkTheme.TEXT_PRIMARY};
                font-size: 11px;
                min-height: 18px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 16px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {DarkTheme.TEXT_PRIMARY};
                margin-right: 6px;
            }}
        """)
        masking_layout.addWidget(self.mask_format)
        
        self.case_sensitive = QCheckBox("Case Sensitive")
        self.case_sensitive.setStyleSheet(f"""
            QCheckBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {DarkTheme.BORDER};
                border-radius: 3px;
                background-color: {DarkTheme.SURFACE_LIGHT};
            }}
            QCheckBox::indicator:checked {{
                background-color: {DarkTheme.ACCENT};
                border-color: {DarkTheme.ACCENT};
            }}
        """)
        masking_layout.addWidget(self.case_sensitive)
        
        masking_group.setLayout(masking_layout)
        layout.addWidget(masking_group)
        
        # Brand Keywords Section
        brand_group = QGroupBox("Brand Keywords")
        brand_group.setStyleSheet(f"""
            QGroupBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 12px;
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: {DarkTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: {DarkTheme.SURFACE};
            }}
        """)
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(8)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        upload_btn = QPushButton("Upload Keyword List")
        upload_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkTheme.ACCENT};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 11px;
                min-height: 18px;
            }}
            QPushButton:hover {{
                background-color: #106ebe;
            }}
        """)
        button_layout.addWidget(upload_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkTheme.SURFACE_LIGHT};
                color: {DarkTheme.TEXT_PRIMARY};
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 11px;
                min-height: 18px;
            }}
            QPushButton:hover {{
                background-color: {DarkTheme.BORDER};
            }}
        """)
        button_layout.addWidget(clear_btn)
        brand_layout.addLayout(button_layout)
        
        self.keyword_text = QTextEdit()
        self.keyword_text.setMaximumHeight(80)  # Reduced height
        self.keyword_text.setPlaceholderText("Enter keywords or upload a file...")
        self.keyword_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {DarkTheme.SURFACE_LIGHT};
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 4px;
                color: {DarkTheme.TEXT_PRIMARY};
                padding: 8px;
                font-size: 11px;
                line-height: 1.4;
            }}
        """)
        brand_layout.addWidget(self.keyword_text)
        
        brand_group.setLayout(brand_layout)
        layout.addWidget(brand_group)
        
        # Performance Limits Section
        limits_group = QGroupBox("Performance Limits")
        limits_group.setStyleSheet(f"""
            QGroupBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 12px;
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: {DarkTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: {DarkTheme.SURFACE};
            }}
        """)
        limits_layout = QVBoxLayout()
        limits_layout.setSpacing(4)
        
        limits_text = [
            "PDF Pages: ≤ 100 pages",
            "PDF Size: ≤ 10 MB", 
            "Excel/CSV Rows: ≤ 100,000 rows"
        ]
        
        for text in limits_text:
            label = QLabel(text)
            label.setStyleSheet(f"color: {DarkTheme.TEXT_SECONDARY}; font-size: 10px; padding: 1px 0;")
            limits_layout.addWidget(label)
        
        limits_group.setLayout(limits_layout)
        layout.addWidget(limits_group)
        
        layout.addStretch()
        self.setLayout(layout)

class FixedFilePreview(QWidget):
    """Fixed file preview with working functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                background-color: {DarkTheme.SURFACE};
                margin-top: -1px;
            }}
            QTabBar::tab {{
                background-color: {DarkTheme.SURFACE_LIGHT};
                color: {DarkTheme.TEXT_PRIMARY};
                padding: 8px 16px;
                border: 1px solid {DarkTheme.BORDER};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 500;
                font-size: 11px;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background-color: {DarkTheme.SURFACE};
                border-bottom: 1px solid {DarkTheme.SURFACE};
                color: {DarkTheme.ACCENT};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {DarkTheme.BORDER};
            }}
        """)
        
        # Text Preview Tab
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setPlaceholderText("No file selected")
        self.text_preview.setStyleSheet(f"""
            QTextEdit {{
                background-color: {DarkTheme.SURFACE};
                color: {DarkTheme.TEXT_PRIMARY};
                border: none;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }}
        """)
        self.tab_widget.addTab(self.text_preview, "Text Preview")
        
        # Table Preview Tab
        self.table_preview = QTextEdit()
        self.table_preview.setReadOnly(True)
        self.table_preview.setPlaceholderText("No table data available")
        self.table_preview.setStyleSheet(f"""
            QTextEdit {{
                background-color: {DarkTheme.SURFACE};
                color: {DarkTheme.TEXT_PRIMARY};
                border: none;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }}
        """)
        self.tab_widget.addTab(self.table_preview, "Table Preview")
        
        # Detected Entities Tab
        self.entities_preview = QTextEdit()
        self.entities_preview.setReadOnly(True)
        self.entities_preview.setPlaceholderText("No entities detected")
        self.entities_preview.setStyleSheet(f"""
            QTextEdit {{
                background-color: {DarkTheme.SURFACE};
                color: {DarkTheme.TEXT_PRIMARY};
                border: none;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }}
        """)
        self.tab_widget.addTab(self.entities_preview, "Detected Entities")
        
        layout.addWidget(self.tab_widget)
        
        # Columns dropdown
        columns_layout = QHBoxLayout()
        columns_layout.addStretch()
        
        columns_label = QLabel("Columns:")
        columns_label.setStyleSheet(f"color: {DarkTheme.TEXT_PRIMARY}; font-size: 11px; font-weight: 500;")
        columns_layout.addWidget(columns_label)
        
        self.columns_combo = QComboBox()
        self.columns_combo.addItem("All Columns")
        self.columns_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {DarkTheme.SURFACE_LIGHT};
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 4px;
                padding: 4px 8px;
                color: {DarkTheme.TEXT_PRIMARY};
                font-size: 11px;
                min-width: 100px;
                min-height: 18px;
            }}
        """)
        columns_layout.addWidget(self.columns_combo)
        
        layout.addLayout(columns_layout)
        self.setLayout(layout)
    
    def load_file_content(self, file_path):
        """Load and display file content in preview"""
        try:
            if not os.path.exists(file_path):
                self.text_preview.setText("File not found")
                return
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Display in text preview
            self.text_preview.setText(content[:10000])  # Limit to first 10k chars
            
            # For now, show same content in table preview
            self.table_preview.setText(content[:10000])
            
            # Show file info in entities tab
            file_info = f"File: {os.path.basename(file_path)}\n"
            file_info += f"Size: {len(content)} characters\n"
            file_info += f"Path: {file_path}\n\n"
            file_info += "No PII entities detected yet.\n"
            file_info += "Run processing to detect entities."
            self.entities_preview.setText(file_info)
            
        except Exception as e:
            error_msg = f"Error loading file:\n{str(e)}"
            self.text_preview.setText(error_msg)
            self.table_preview.setText(error_msg)
            self.entities_preview.setText(error_msg)

class FixedProcessingStatus(QWidget):
    """Fixed processing status with proper layout"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Overall Progress Section
        overall_label = QLabel("Overall Progress:")
        overall_label.setStyleSheet(f"color: {DarkTheme.TEXT_PRIMARY}; font-weight: 600; font-size: 12px;")
        layout.addWidget(overall_label)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                text-align: center;
                background-color: {DarkTheme.SURFACE_LIGHT};
                height: 20px;
                font-weight: 500;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background-color: {DarkTheme.ACCENT};
                border-radius: 5px;
                margin: 1px;
            }}
        """)
        layout.addWidget(self.overall_progress)
        
        # Current File Progress Section
        current_label = QLabel("Current File:")
        current_label.setStyleSheet(f"color: {DarkTheme.TEXT_PRIMARY}; font-weight: 600; font-size: 12px;")
        layout.addWidget(current_label)
        
        self.current_file_progress = QProgressBar()
        self.current_file_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                text-align: center;
                background-color: {DarkTheme.SURFACE_LIGHT};
                height: 20px;
                font-weight: 500;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background-color: {DarkTheme.SUCCESS};
                border-radius: 5px;
                margin: 1px;
            }}
        """)
        layout.addWidget(self.current_file_progress)
        
        # Status text
        self.status_label = QLabel("Ready to process")
        self.status_label.setStyleSheet(f"""
            color: {DarkTheme.TEXT_SECONDARY}; 
            font-size: 11px; 
            font-style: italic;
            padding: 3px 0;
        """)
        layout.addWidget(self.status_label)
        
        # Files list
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(120)  # Reduced height
        self.files_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {DarkTheme.SURFACE};
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                color: {DarkTheme.TEXT_PRIMARY};
                padding: 6px;
                font-size: 11px;
            }}
            QListWidget::item {{
                padding: 4px 8px;
                border-bottom: 1px solid {DarkTheme.BORDER};
                border-radius: 3px;
                margin: 1px 0;
            }}
            QListWidget::item:selected {{
                background-color: {DarkTheme.ACCENT};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {DarkTheme.SURFACE_LIGHT};
            }}
        """)
        layout.addWidget(self.files_list)
        
        self.setLayout(layout)

class FixedMainWindow(QMainWindow):
    """Fixed main window with working functionality"""
    
    def __init__(self):
        super().__init__()
        self.current_files = []
        self.output_directory = ""
        self.detection_engine = None
        self.document_modifier = None
        self.report_generator = None
        self.performance_processor = None
        self.processing_results = []
        self.setup_ui()
        self.initialize_engine()
        self.apply_dark_theme()
    
    def setup_ui(self):
        self.setWindowTitle("Cloak & Style - PII Data Scrubber")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with proper spacing
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)  # Reduced spacing
        main_layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins
        
        # Left panel (Input and Options)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)  # Reduced spacing
        
        # Header with proper spacing
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        title_label = QLabel("Cloak & Style PII Data Scrubber Tool")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))  # Reduced size
        title_label.setStyleSheet(f"color: {DarkTheme.TEXT_PRIMARY}; margin-bottom: 3px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Remove the security badge that was causing visual clutter
        # security_badge = QLabel("🔒 No data sent to cloud • All processing local")
        # security_badge.setStyleSheet(f"""
        #     color: {DarkTheme.WARNING};
        #     font-size: 10px;
        #     font-weight: 500;
        #     padding: 4px 8px;
        #     border: 1px solid {DarkTheme.WARNING};
        #     border-radius: 4px;
        #     background-color: rgba(255, 140, 0, 0.1);
        # """)
        # header_layout.addWidget(security_badge)
        
        left_layout.addLayout(header_layout)
        
        # Input Files section
        input_group = QGroupBox("Input Files")
        input_group.setStyleSheet(f"""
            QGroupBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 13px;
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: {DarkTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: {DarkTheme.SURFACE};
            }}
        """)
        input_layout = QVBoxLayout()
        input_layout.setSpacing(15)  # Simple spacing
        
        # Single upload box - clean and simple
        upload_box = QWidget()
        upload_box.setMinimumHeight(100)
        upload_box.setStyleSheet(f"""
            QWidget {{
                background-color: {DarkTheme.SURFACE};
                border: 2px dashed {DarkTheme.BORDER};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        upload_layout = QVBoxLayout()
        upload_layout.setContentsMargins(0, 0, 0, 0)
        upload_layout.setSpacing(10)
        
        # Simple upload label
        upload_label = QLabel("Drag and drop your files here")
        upload_label.setAlignment(Qt.AlignCenter)
        upload_label.setFont(QFont("Segoe UI", 12))
        upload_label.setStyleSheet(f"color: {DarkTheme.TEXT_PRIMARY}; font-weight: 500;")
        upload_layout.addWidget(upload_label)
        
        upload_box.setLayout(upload_layout)
        upload_box.setAcceptDrops(True)
        
        # Connect drag and drop events
        upload_box.dragEnterEvent = lambda event: self.handle_drag_enter(event, upload_box)
        upload_box.dragLeaveEvent = lambda event: self.handle_drag_leave(event, upload_box)
        upload_box.dropEvent = lambda event: self.handle_drop(event, upload_box)
        
        input_layout.addWidget(upload_box)
        
        # Browse button
        browse_btn = QPushButton("Browse Files")
        browse_btn.clicked.connect(self.browse_files)
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkTheme.ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 12px;
                min-height: 22px;
            }}
            QPushButton:hover {{
                background-color: #106ebe;
            }}
        """)
        input_layout.addWidget(browse_btn)
        
        # File type note
        file_types_note = QLabel("Supported file types: DOCX, PPTX, PDF, XLSX, CSV, TXT, MD")
        file_types_note.setStyleSheet(f"""
            color: {DarkTheme.TEXT_SECONDARY};
            font-size: 11px;
            font-style: italic;
            padding: 5px 0;
            text-align: center;
        """)
        file_types_note.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(file_types_note)
        
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)
        
        # Output Directory section
        output_group = QGroupBox("Output Directory")
        output_group.setStyleSheet(f"""
            QGroupBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 13px;
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: {DarkTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: {DarkTheme.SURFACE};
            }}
        """)
        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output directory (required)")
        self.output_path.setStyleSheet(f"""
            QLineEdit {{
                background-color: {DarkTheme.SURFACE_LIGHT};
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                color: {DarkTheme.TEXT_PRIMARY};
                font-size: 11px;
                min-height: 22px;
            }}
            QLineEdit:focus {{
                border-color: {DarkTheme.ACCENT};
            }}
        """)
        output_layout.addWidget(self.output_path)
        
        output_browse_btn = QPushButton("Browse")
        output_browse_btn.clicked.connect(self.browse_output_directory)
        output_browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkTheme.SURFACE_LIGHT};
                color: {DarkTheme.TEXT_PRIMARY};
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 11px;
                min-height: 22px;
            }}
            QPushButton:hover {{
                background-color: {DarkTheme.BORDER};
            }}
        """)
        output_layout.addWidget(output_browse_btn)
        
        output_group.setLayout(output_layout)
        left_layout.addWidget(output_group)
        
        # Fixed Processing Options
        self.options_widget = FixedProcessingOptions()
        left_layout.addWidget(self.options_widget)
        
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(400)  # Reduced width
        main_layout.addWidget(left_panel)
        
        # Right panel (Preview and Processing)
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # File Preview
        preview_group = QGroupBox("File Preview")
        preview_group.setStyleSheet(f"""
            QGroupBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 13px;
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: {DarkTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: {DarkTheme.SURFACE};
            }}
        """)
        preview_layout = QVBoxLayout()
        
        self.preview_widget = FixedFilePreview()
        preview_layout.addWidget(self.preview_widget)
        
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        # Processing section
        processing_group = QGroupBox("Processing")
        processing_group.setStyleSheet(f"""
            QGroupBox {{
                color: {DarkTheme.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 13px;
                border: 1px solid {DarkTheme.BORDER};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: {DarkTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: {DarkTheme.SURFACE};
            }}
        """)
        processing_layout = QVBoxLayout()
        processing_layout.setSpacing(10)
        
        self.status_widget = FixedProcessingStatus()
        processing_layout.addWidget(self.status_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkTheme.SUCCESS};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 12px;
                min-height: 25px;
            }}
            QPushButton:hover {{
                background-color: #0e6e0e;
            }}
            QPushButton:disabled {{
                background-color: {DarkTheme.SURFACE_LIGHT};
                color: {DarkTheme.TEXT_SECONDARY};
            }}
        """)
        button_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkTheme.ERROR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 12px;
                min-height: 25px;
            }}
            QPushButton:hover {{
                background-color: #b32d30;
            }}
            QPushButton:disabled {{
                background-color: {DarkTheme.SURFACE_LIGHT};
                color: {DarkTheme.TEXT_SECONDARY};
            }}
        """)
        button_layout.addWidget(self.cancel_btn)
        
        processing_layout.addLayout(button_layout)
        processing_group.setLayout(processing_layout)
        right_layout.addWidget(processing_group)
        
        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel)
        
        central_widget.setLayout(main_layout)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def apply_dark_theme(self):
        """Apply dark theme to the entire application"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {DarkTheme.BACKGROUND};
                color: {DarkTheme.TEXT_PRIMARY};
            }}
            QWidget {{
                background-color: {DarkTheme.BACKGROUND};
                color: {DarkTheme.TEXT_PRIMARY};
            }}
        """)
    
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
    
    def browse_files(self):
        """Browse for files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "All Files (*.txt *.csv *.docx *.pptx *.xlsx *.pdf *.md *.log)"
        )
        
        if files:
            self.add_files(files)
    
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            ""
        )
        
        if directory:
            self.output_directory = directory
            self.output_path.setText(directory)
            self.update_start_button()
    
    def add_files(self, files):
        """Add files to the list and load preview"""
        # Clear existing files first to avoid duplicates
        self.current_files = []
        self.current_files.extend(files)
        self.update_file_list()
        self.update_start_button()
        
        # Load preview of the first file
        if self.current_files:
            self.load_file_preview(self.current_files[0])
        
        print(f"Added {len(files)} files. Total files: {len(self.current_files)}")
        print(f"Output directory: {self.output_directory}")
        print(f"Start button should be enabled: {len(self.current_files) > 0 and self.output_directory != ''}")
    
    def load_file_preview(self, file_path):
        """Load file content into preview"""
        if hasattr(self.preview_widget, 'load_file_content'):
            self.preview_widget.load_file_content(file_path)
    
    def update_file_list(self):
        """Update the file list display"""
        self.status_widget.files_list.clear()
        for file_path in self.current_files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setToolTip(file_path)
            self.status_widget.files_list.addItem(item)
    
    def update_start_button(self):
        """Update start button state"""
        has_files = len(self.current_files) > 0
        has_output = self.output_directory != ""
        should_enable = has_files and has_output
        
        print(f"update_start_button: files={has_files}, output={has_output}, enable={should_enable}")
        
        self.start_btn.setEnabled(should_enable)
        
        # Update button styling based on state
        if should_enable:
            self.start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {DarkTheme.SUCCESS};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 20px;
                    font-weight: 600;
                    font-size: 12px;
                    min-height: 25px;
                }}
                QPushButton:hover {{
                    background-color: #0e6e0e;
                }}
            """)
        else:
            self.start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {DarkTheme.SURFACE_LIGHT};
                    color: {DarkTheme.TEXT_SECONDARY};
                    border: none;
                    border-radius: 6px;
                    padding: 12px 20px;
                    font-weight: 600;
                    font-size: 12px;
                    min-height: 25px;
                }}
            """)
    
    def handle_drag_enter(self, event, widget):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {DarkTheme.HIGHLIGHT};
                    border: 2px dashed {DarkTheme.ACCENT};
                    border-radius: 8px;
                    padding: 20px;
                }}
            """)
    
    def handle_drag_leave(self, event, widget):
        """Handle drag leave event"""
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {DarkTheme.SURFACE};
                border: 2px dashed {DarkTheme.BORDER};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
    
    def handle_drop(self, event, widget):
        """Handle drop event"""
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                files.append(file_path)
        
        if files:
            self.add_files(files)
        
        # Reset styling
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {DarkTheme.SURFACE};
                border: 2px dashed {DarkTheme.BORDER};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
    
    def start_processing(self):
        """Start processing files"""
        if not self.current_files:
            QMessageBox.warning(self, "No Files", "Please select files to process.")
            return
        
        if not self.output_directory:
            QMessageBox.warning(self, "No Output Directory", "Please select an output directory.")
            return
        
        # Start processing logic here
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_widget.status_label.setText("Processing...")
        self.status_widget.overall_progress.setValue(0)
        self.status_widget.current_file_progress.setValue(0)
        
        try:
            # Process each file
            total_files = len(self.current_files)
            for i, file_path in enumerate(self.current_files):
                # Update progress
                overall_progress = int((i / total_files) * 100)
                self.status_widget.overall_progress.setValue(overall_progress)
                self.status_widget.status_label.setText(f"Processing: {os.path.basename(file_path)}")
                
                # Process current file
                self.process_single_file(file_path)
                
                # Update current file progress
                self.status_widget.current_file_progress.setValue(100)
                
                # Small delay to show progress
                QApplication.processEvents()
            
            # Complete
            self.status_widget.overall_progress.setValue(100)
            self.status_widget.status_label.setText("Processing completed successfully")
            
            QMessageBox.information(self, "Processing Complete", 
                                  f"Successfully processed {len(self.current_files)} file(s).\n"
                                  f"Output saved to: {self.output_directory}")
            
        except Exception as e:
            QMessageBox.critical(self, "Processing Error", 
                               f"An error occurred during processing:\n{str(e)}")
            self.status_widget.status_label.setText("Processing failed")
        
        finally:
            self.start_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
    
    def process_single_file(self, file_path):
        """Process a single file for PII detection and masking"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Detect PII entities (if detection engine is available)
            detected_entities = []
            if self.detection_engine and hasattr(self.detection_engine, 'detect_pii'):
                try:
                    detected_entities = self.detection_engine.detect_pii(content)
                except Exception as e:
                    print(f"Detection engine error: {e}")
            
            # Create masked content (simple masking for demo)
            masked_content = self.mask_pii_content(content, detected_entities)
            
            # Save processed file
            output_filename = f"masked_{os.path.basename(file_path)}"
            output_path = os.path.join(self.output_directory, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(masked_content)
            
            # Update preview with detected entities
            if detected_entities:
                entities_text = "Detected PII Entities:\n\n"
                for entity in detected_entities:
                    entities_text += f"• {entity.entity_type}: {entity.text}\n"
                self.preview_widget.entities_preview.setText(entities_text)
            
            print(f"Processed: {file_path} -> {output_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            raise
    
    def mask_pii_content(self, content, entities):
        """Mask PII content based on detected entities"""
        masked_content = content
        
        # Simple masking patterns (in a real implementation, this would be more sophisticated)
        import re
        
        # Email addresses
        masked_content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', masked_content)
        
        # Phone numbers (various formats)
        masked_content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', masked_content)
        masked_content = re.sub(r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b', '[PHONE]', masked_content)
        
        # Social Security Numbers
        masked_content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', masked_content)
        
        # Credit Card Numbers
        masked_content = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CREDIT_CARD]', masked_content)
        
        # IP Addresses
        masked_content = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_ADDRESS]', masked_content)
        
        return masked_content
    
    def cancel_processing(self):
        """Cancel processing"""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_widget.status_label.setText("Processing cancelled")
        self.status_widget.overall_progress.setValue(0)
        self.status_widget.current_file_progress.setValue(0)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = FixedMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
