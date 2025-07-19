"""
Pytest configuration file for Plot MCP tests.
"""
import os
import warnings

# Set environment variable to suppress Jupyter deprecation warning
os.environ['JUPYTER_PLATFORM_DIRS'] = '1'

# Alternative: Filter the specific warning
warnings.filterwarnings(
    "ignore", 
    category=DeprecationWarning, 
    message="Jupyter is migrating its paths to use standard platformdirs.*"
)
