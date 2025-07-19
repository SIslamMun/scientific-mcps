"""
Line plot capabilities for data visualization.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def create_line_plot(
    file_path: str, 
    x_column: str, 
    y_column: str, 
    title: str = "Line Plot",
    output_path: str = "line_plot.png"
) -> Dict[str, Any]:
    """
    Create a line plot from data with professional styling.
    
    Args:
        file_path: Path to the data file
        x_column: Column name for x-axis
        y_column: Column name for y-axis
        title: Plot title
        output_path: Output image file path
        
    Returns:
        Dictionary with plot creation results and metadata
    """
    try:
        # Import data_info locally to avoid circular imports
        from .data_info import load_data
        
        df = load_data(file_path)
        
        # Validate columns exist
        if x_column not in df.columns:
            raise ValueError(f"Column '{x_column}' not found in data. Available columns: {list(df.columns)}")
        if y_column not in df.columns:
            raise ValueError(f"Column '{y_column}' not found in data. Available columns: {list(df.columns)}")
        
        # Clean data - remove NaN values
        clean_df = df[[x_column, y_column]].dropna()
        if clean_df.empty:
            raise ValueError("No valid data points found after removing NaN values")
        
        # Create the plot with professional styling
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create line plot
        ax.plot(clean_df[x_column], clean_df[y_column], 
                marker='o', linewidth=2.5, markersize=6, 
                color='#2E86AB', markerfacecolor='#A23B72', 
                markeredgecolor='white', markeredgewidth=1.5)
        
        # Styling
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(x_column, fontsize=14, fontweight='semibold')
        ax.set_ylabel(y_column, fontsize=14, fontweight='semibold')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Improve layout
        plt.tight_layout()
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save with high quality
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            "status": "success",
            "output_path": output_path,
            "plot_type": "line_plot",
            "data_points": len(clean_df),
            "x_column": x_column,
            "y_column": y_column,
            "title": title,
            "metadata": {
                "x_range": [float(clean_df[x_column].min()), float(clean_df[x_column].max())],
                "y_range": [float(clean_df[y_column].min()), float(clean_df[y_column].max())],
                "data_file": file_path
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating line plot: {e}")
        return {
            "status": "error",
            "error": str(e),
            "suggestions": [
                "Verify column names exist in the dataset",
                "Check for valid numeric data in specified columns",
                "Ensure output directory is writable",
                "Validate data file format and content"
            ]
        }
