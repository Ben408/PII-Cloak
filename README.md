# Cloak & Style - PII Data Scrubber

**Professional PII (Personally Identifiable Information) data scrubbing tool for content professionals.**

[![Windows](https://img.shields.io/badge/Windows-10%2F11-blue.svg)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

Cloak & Style is a comprehensive desktop utility that identifies, masks, and redacts personally identifiable information from business documents. It combines rule-based detection with advanced ML-powered recognition to ensure thorough PII removal while maintaining document integrity.

**Key Features:**
- 🔍 **Hybrid Detection**: Rule-based patterns + ML-powered NER
- 📄 **Multi-Format Support**: CSV, XLSX, DOCX, PPTX, PDF, TXT, MD, LOG
- 🎨 **Professional UI**: Drag-and-drop interface with real-time preview
- 🔄 **Review Queue**: Accept/Reject findings with confidence scoring
- 📊 **Comprehensive Reports**: HTML, JSON, and CSV outputs
- ⚡ **Performance Optimized**: Laptop-grade processing with caps enforcement
- 🖥️ **CLI Support**: Full command-line interface for automation

## 🚀 Quick Start

### Installation

1. **Download** the latest release from [GitHub Releases](https://github.com/your-org/cloak-and-style/releases)
2. **Extract** the ZIP file to a folder
3. **Run** `install.bat` as a regular user (no admin rights required)
4. **Launch** from Desktop shortcut or Start Menu

### System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 8-16 GB recommended
- **Storage**: 500 MB free space
- **Permissions**: User-level installation (no admin required)

### First Run

1. **Launch** Cloak & Style
2. **Drag & Drop** files or folders to process
3. **Select** output directory (required)
4. **Configure** options (Review Queue, Dry-run, etc.)
5. **Run** processing and review results

## 📋 Supported File Types

| Format | Features | Advanced Capabilities |
|--------|----------|----------------------|
| **CSV** | Full-text scan, per-cell masking | Streaming for large files |
| **XLSX** | Cell values, comments, formulas | Formula literal masking |
| **DOCX** | Body, headers, footnotes, comments | Tracked changes, hyperlinks |
| **PPTX** | Shapes, tables, speaker notes | Chart labels, alt text |
| **PDF** | Text extraction, page processing | HTML/TXT output, image-only detection |
| **TXT** | Full-text processing | Encoding detection, chunked processing |
| **MD** | Markdown text processing | Link handling |
| **LOG** | Log file processing | Timestamp preservation |

## 🔧 PII Detection Capabilities

### Entity Types Detected

- **Personal Information**: Names, addresses, dates of birth
- **Contact Details**: Email addresses, phone numbers
- **Financial Data**: Credit card numbers, bank accounts
- **Government IDs**: Social Security Numbers, national IDs
- **Technical Data**: IP addresses, usernames, coordinates
- **Custom Keywords**: Brand names, sensitive terms

### Detection Methods

1. **Rule-Based Detection**: High-precision regex patterns with validation
2. **ML-Powered NER**: LongTransformer model for complex entities
3. **Hybrid Fusion**: Combines both methods with intelligent precedence
4. **Residual Validation**: Re-scans outputs to ensure complete masking

## 🎛️ Scrubbing Modes

### Three Processing Options

| Mode | Description | Use Case |
|------|-------------|----------|
| **Mask** | Replace with tokens (e.g., `[EMAIL_001]`) | Standard processing |
| **Redact** | Replace with `[REDACTED]` | Compliance requirements |
| **Remove** | Delete content entirely | Maximum privacy |

### Partial Reveal Policy

- ✅ **Allowed**: PERSON, BRAND keywords (when using Mask mode)
- ❌ **Never Allowed**: EMAIL, CREDIT_CARD, PHONE, IP, SSN/NationalID
- ⚠️ **Structured identifiers** must be fully masked or redacted

## 🖥️ User Interface

### Main Features

- **Drag & Drop**: Intuitive file upload with visual feedback
- **Tabbed Interface**: Upload, Options, Review, Results
- **Real-time Progress**: Per-file status with cancel capability
- **Review Queue**: Accept/Reject findings with filters
- **Diff Preview**: Side-by-side comparison of original vs masked
- **Advanced Options**: Configuration for masking format and entity types

### Review Queue

- **Filter & Sort**: By entity type, confidence, file
- **Bulk Actions**: Accept/Reject by type, file, or exact matches
- **Preview Pane**: Textual diffs and PDF HTML previews
- **Export**: Generate masked artifacts after approval

## 💻 Command Line Interface

### Basic Usage

```bash
# Process a single file
cloak_and_style.exe --in "document.docx" --out "C:\output"

# Process folder recursively
cloak_and_style.exe --in "C:\documents" --out "C:\masked" --recursive

# Dry-run with reports
cloak_and_style.exe --in "C:\data" --out "C:\output" --dry-run --report html,json,csv
```

### Advanced Options

```bash
# Include specific file types
cloak_and_style.exe --in "C:\data" --out "C:\output" --include "*.docx;*.pdf"

# Exclude certain files
cloak_and_style.exe --in "C:\data" --out "C:\output" --exclude "*.tmp"

# Configure exit behavior
cloak_and_style.exe --in "C:\data" --out "C:\output" --exit-on image-only-pdf,caps-exceeded

# Enable review queue in CLI
cloak_and_style.exe --in "C:\data" --out "C:\output" --review-queue on
```

### Exit Codes

- **0**: Success (with or without warnings)
- **2**: Policy violations (image-only PDFs, caps exceeded, residuals)
- **3**: Fatal errors

## 📊 Performance & Limits

### Processing Caps

| File Type | Limit | Action |
|-----------|-------|--------|
| **CSV/XLSX** | 100,000 rows | Skip file, report error |
| **PDF** | 100 pages OR 10 MB | Skip file, report error |
| **Memory** | 8-16 GB peak | Optimized for laptop use |

### Performance Targets

- **Typical Files**: < 30 seconds for 25-page PDFs or 50k-row spreadsheets
- **Large Files**: Responsive progress UI with memory management
- **Batch Processing**: Parallel processing with configurable limits

## 🔒 Privacy & Security

### Local Processing

- ✅ **Offline Only**: No network calls during processing
- ✅ **No Telemetry**: Zero analytics or tracking
- ✅ **No PII Persistence**: Mappings exist in memory only
- ✅ **Temp File Cleanup**: Automatic cleanup on exit

### Data Handling

- **Input**: Files are read and processed locally
- **Processing**: All detection and masking happens in memory
- **Output**: Only masked tokens and metadata in reports
- **Storage**: No raw PII written to disk

## 📈 Reports & Outputs

### Report Types

1. **HTML Report**: Professional summary with styling
2. **JSON Report**: Machine-readable data for integration
3. **CSV Findings**: Detailed entity list for review

### Report Contents

- **Processing Summary**: Files processed, entities found, timing
- **Entity Statistics**: Counts by type, confidence histograms
- **Questionable Entities**: Low-confidence detections for review
- **Warnings**: Image-only PDFs, embedded objects, caps violations
- **Configuration**: Settings snapshot for audit trail

### Output Policy

- **Required Output Directory**: Explicit location selection
- **Mirror Tree Structure**: Preserves input folder hierarchy
- **Versioned Naming**: Automatic `file (2).ext` for conflicts
- **No In-Place Writes**: Original files never modified

## 🛠️ Configuration

### Default Settings

```json
{
  "language": "en",
  "entities": ["PERSON","ADDRESS","EMAIL","PHONE","IP","CREDIT_CARD","BANK_ACCT","NATIONAL_ID","DOB","USERNAME","GEO"],
  "mask_format": "TOKEN",
  "review_queue": false,
  "dry_run": false,
  "caps": {"pdf_pages": 100, "pdf_mb": 10, "rows": 100000},
  "reports": ["html","json"],
  "validation": {"residual_action": "warn", "min_confidence": 0.35, "questionable_band": [0.35,0.65]},
  "backend": "pii-masker"
}
```

### Customization

- **Entity Selection**: Enable/disable specific PII types
- **Confidence Thresholds**: Adjust detection sensitivity
- **Masking Format**: Choose between tokens and asterisks
- **Performance Tuning**: Configure memory and processing limits

## 🧪 Testing & Validation

### Test Coverage

- **Unit Tests**: 50+ test cases across all components
- **Integration Tests**: End-to-end processing workflows
- **Performance Tests**: Memory and timing validation
- **Security Tests**: Privacy and data handling verification

### Quality Assurance

- **0 Residual PII**: No PII remains above confidence threshold
- **100% Consistency**: Same entities masked identically within runs
- **Caps Enforcement**: Proper handling of file size limits
- **Error Recovery**: Graceful handling of malformed files

## 🚨 Error Handling

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| **Image-only PDF** | No extractable text | Use OCR tools or skip file |
| **Caps Exceeded** | File too large | Split files or increase limits |
| **Unsupported Type** | JSON/XML files | Convert to supported format |
| **Write Conflict** | Output exists | Automatic versioning applied |

### Error Messages

- **Clear Descriptions**: Specific error causes and solutions
- **Actionable Guidance**: Step-by-step resolution steps
- **Report Integration**: All errors logged in summary reports
- **Non-Blocking**: Continue processing other files when possible

## 🔄 Updates & Maintenance

### Version History

- **v1.0.0**: Initial release with core functionality
- **Future**: Language packs, OCR support, advanced features

### Support

- **Documentation**: Comprehensive guides and examples
- **Issues**: GitHub issue tracking for bugs and features
- **Community**: User forums and discussion groups

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. **Clone** the repository
2. **Install** dependencies: `pip install -r requirements.txt`
3. **Run** tests: `python -m pytest test/`
4. **Build** executable: `pyinstaller cloak_and_style.spec`

## 🙏 Acknowledgments

- **PII Masker**: LongTransformer model for entity detection
- **PySide6**: Modern Qt-based GUI framework
- **Open Source Community**: Libraries and tools that made this possible

## 📞 Support

- **Documentation**: [Wiki](https://github.com/your-org/cloak-and-style/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/cloak-and-style/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/cloak-and-style/discussions)

---

**Cloak & Style** - Making data privacy elegant and accessible. 🎭✨
