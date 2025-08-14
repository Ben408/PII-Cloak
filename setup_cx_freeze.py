import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "os", "sys", "re", "json", "csv", "tempfile", "pathlib", "typing", 
        "dataclasses", "threading", "concurrent.futures", "time", "statistics", 
        "collections", "itertools", "functools", "logging", "warnings", "traceback",
        "torch", "transformers", "huggingface_hub", "openpyxl", "docx", "pptx", 
        "fitz", "chardet", "psutil", "PySide6"
    ],
    "excludes": ["pathlib"],  # Explicitly exclude pathlib
    "include_files": [
        ("core/", "core/"),
        ("pii-mask/", "pii-mask/"),
        ("README.md", "README.md"),
        ("LICENSE", "LICENSE"),
        ("install.bat", "install.bat")
    ],
    "optimize": 2,
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Cloak & Style PII Data Scrubber",
    version="1.0.0",
    description="Professional PII Data Scrubber with ML-powered detection",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "cloak_and_style_ui.py", 
            base=base,
            target_name="cloak_and_style.exe",
            icon=None  # Add icon path if you have one
        )
    ]
)
