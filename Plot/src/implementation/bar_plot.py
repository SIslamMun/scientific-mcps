"""
Bar plot capabilities for categorical data visualization.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def create_bar_plot(
    file_path: str,
    x_column: str,
    y_column: str,
    title: str = "Bar Plot",
    output_path: str = "bar_plot.png"
) -> Dict[str, Any]:
    """
    Create a bar plot from data with automatic aggregation and styling.
    
    Args:
        file_path: Path to the data file
        x_column: Column name for x-axis (categorical)
        y_column: Column name for y-axis (numeric)
        title: Plot title
        output_path: Output image file path
        
    Returns:
        Dictionary with plot creation results and metadata
    """
    try:
        from .data_info import load_data
        
        df = load_data(file_path)
        
        # Validate columns exist
        if x_column not in df.columns:
            raise ValueError(f"Column '{x_column}' not found in data. Available columns: {list(df.columns)}")
        if y_column not in df.columns:
            raise ValueError(f"Column '{y_column}' not found in data. Available columns: {list(df.columns)}")
        
        # Clean and aggregate data
        clean_df = df[[x_column, y_column]].dropna()
        if clean_df.empty:
            raise ValueError("No valid data points found after removing NaN values")
        
        # Group by x_column and aggregate y_column (sum by default)
        aggregated_data = clean_df.groupby(x_column)[y_column].sum().reset_index()
        aggregated_data = aggregated_data.sort_values(y_column, ascending=False)
        
        # Create the plot
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create bar plot with gradient colors
        bars = ax.bar(aggregated_data[x_column], aggregated_data[y_column],
                     color=plt.cm.viridis(np.linspace(0, 1, len(aggregated_data))),
                     edgecolor='white', linewidth=1.2)
        
        # Styling
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(x_column, fontsize=14, fontweight='semibold')
        ax.set_ylabel(y_column, fontsize=14, fontweight='semibold')
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Rotate x-axis labels if needed
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Create output directory and save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            "status": "success",
            "output_path": output_path,
            "plot_type": "bar_plot",
            "categories": len(aggregated_data),
            "x_column": x_column,
            "y_column": y_column,
            "title": title,
            "metadata": {
                "aggregation_method": "sum",
                "top_category": aggregated_data.iloc[0][x_column],
                "max_value": float(aggregated_data[y_column].max()),
                "data_file": file_path
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating bar plot: {e}")
        return {
            "status": "error",
            "error": str(e),
            "suggestions": [
                "Ensure x_column contains categorical data",
                "Verify y_column contains numeric data for aggregation",
                "Check column names match those in dataset",
                "Validate output path is writable"
            ]
        }
