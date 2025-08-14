# Runtime hook to handle pathlib issue
import sys
import os

# Try to remove pathlib from sys.modules if it exists
if 'pathlib' in sys.modules:
    del sys.modules['pathlib']

# Also try to remove from sys.path
sys.path = [p for p in sys.path if 'pathlib' not in p]
