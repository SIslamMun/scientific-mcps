"""
Data information capabilities for plot MCP server.
"""
import os
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from CSV or Excel file.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        pandas DataFrame with the data
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise

def get_data_info(file_path: str) -> Dict[str, Any]:
    """
    Get comprehensive information about the data file.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        Dictionary containing detailed data information
    """
    try:
        df = load_data(file_path)
        
        # Basic information
        info = {
            "status": "success",
            "file_path": file_path,
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "null_counts": df.isnull().sum().to_dict(),
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
            "head": df.head().to_dict(),
            "summary_statistics": {}
        }
        
        # Summary statistics for numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            info["summary_statistics"] = df[numeric_columns].describe().to_dict()
            
        return info
        
    except Exception as e:
        logger.error(f"Error getting data info: {e}")
        return {
            "status": "error",
            "error": str(e),
            "suggestions": [
                "Verify file path exists and is accessible",
                "Ensure file format is supported (CSV, XLSX, XLS)",
                "Check file permissions",
                "Validate file is not corrupted"
            ]
        }
