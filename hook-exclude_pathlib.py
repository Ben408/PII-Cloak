# Custom PyInstaller hook to exclude pathlib
from PyInstaller.utils.hooks import collect_all

# Explicitly exclude pathlib
excludedimports = ['pathlib']

# Don't collect any modules
def hook(hook_api):
    pass
