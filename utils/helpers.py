"""
Helper utilities for the job matching system.
Contains common functions used across multiple modules.
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created, False on error
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {str(e)}")
        return False

def save_json_file(data: Any, file_path: str) -> bool:
    """
    Save data to a JSON file
    
    Args:
        data: Data to save
        file_path: Path to save the file
        
    Returns:
        True if successful, False on error
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        ensure_directory_exists(directory)
        
        # Write the file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {str(e)}")
        return False

def load_json_file(file_path: str) -> Tuple[bool, Any, str]:
    """
    Load data from a JSON file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Tuple of (success, data, message)
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return True, data, f"Successfully loaded data from {file_path}"
    except FileNotFoundError:
        return False, None, f"File not found: {file_path}"
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON in {file_path}: {str(e)}"
    except Exception as e:
        return False, None, f"Error loading {file_path}: {str(e)}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format a float as a percentage string
    
    Args:
        value: Float value to format
        decimal_places: Number of decimal places to include
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimal_places}f}%"

def calculate_percentage(numerator: Union[int, float], denominator: Union[int, float], 
                        default: float = 0.0) -> float:
    """
    Calculate percentage safely handling zero denominator
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return if denominator is zero
        
    Returns:
        Percentage value
    """
    if denominator == 0:
        return default
    return (numerator / denominator) * 100.0

def export_results_to_csv(results: List[Dict[str, Any]], file_path: str) -> bool:
    """
    Export scoring results to a CSV file
    
    Args:
        results: List of scoring result dictionaries
        file_path: Path to save the CSV file
        
    Returns:
        True if successful, False on error
    """
    try:
        # Create a simplified dataframe with results
        df = pd.DataFrame([{
            "job_app_id": r["job_app_id"],
            "total_score": r["total_score"],
            "core_skills_raw": r["scores"]["core_skills"]["raw_score"],
            "core_skills_weighted": r["scores"]["core_skills"]["weighted_score"],
            "experience_raw": r["scores"]["experience"]["raw_score"],
            "experience_weighted": r["scores"]["experience"]["weighted_score"],
            "education_raw": r["scores"]["education"]["raw_score"],
            "education_weighted": r["scores"]["education"]["weighted_score"],
            "certifications_raw": r["scores"]["certifications"]["raw_score"],
            "certifications_weighted": r["scores"]["certifications"]["weighted_score"]
        } for r in results])
        
        # Save to CSV
        df.to_csv(file_path, index=False)
        
        logger.info(f"Results exported to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting results to {file_path}: {str(e)}")
        return False

def export_results_to_json(results: List[Dict[str, Any]], file_path: str) -> bool:
    """
    Export scoring results to a JSON file
    
    Args:
        results: List of scoring result dictionaries
        file_path: Path to save the JSON file
        
    Returns:
        True if successful, False on error
    """
    # Create a simplified version for export
    export_data = [{
        "job_app_id": r["job_app_id"],
        "total_score": r["total_score"],
        "component_scores": {
            "core_skills": r["scores"]["core_skills"]["raw_score"],
            "experience": r["scores"]["experience"]["raw_score"],
            "education": r["scores"]["education"]["raw_score"],
            "certifications": r["scores"]["certifications"]["raw_score"]
        }
    } for r in results]
    
    # Save to file
    return save_json_file(export_data, file_path)

def create_component_breakdown(result: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a component breakdown DataFrame for a single job application result
    
    Args:
        result: Scoring result dictionary
        
    Returns:
        Pandas DataFrame with component breakdown
    """
    component_data = {
        "Component": ["Core Skills", "Experience", "Education", "Certifications"],
        "Raw Score": [
            result["scores"]["core_skills"]["raw_score"],
            result["scores"]["experience"]["raw_score"],
            result["scores"]["education"]["raw_score"],
            result["scores"]["certifications"]["raw_score"]
        ],
        "Weighted Score": [
            result["scores"]["core_skills"]["weighted_score"],
            result["scores"]["experience"]["weighted_score"],
            result["scores"]["education"]["weighted_score"],
            result["scores"]["certifications"]["weighted_score"]
        ]
    }
    
    # Calculate contribution percentage
    total_score = result["total_score"]
    if total_score > 0:
        component_data["Contribution (%)"] = [
            (result["scores"]["core_skills"]["weighted_score"] / total_score) * 100,
            (result["scores"]["experience"]["weighted_score"] / total_score) * 100,
            (result["scores"]["education"]["weighted_score"] / total_score) * 100,
            (result["scores"]["certifications"]["weighted_score"] / total_score) * 100
        ]
    else:
        component_data["Contribution (%)"] = [0, 0, 0, 0]
    
    return pd.DataFrame(component_data)

def find_job_app_by_id(job_apps: List[Dict[str, Any]], job_app_id: int) -> Optional[Dict[str, Any]]:
    """
    Find a job application by ID
    
    Args:
        job_apps: List of job applications
        job_app_id: ID to search for
        
    Returns:
        Job application dictionary or None if not found
    """
    for job_app in job_apps:
        if job_app.get("job_app_id") == job_app_id:
            return job_app
    return None

def get_matching_items(required_items: List[str], provided_items: List[str]) -> List[str]:
    """
    Get list of matching items between two lists
    
    Args:
        required_items: List of required items
        provided_items: List of provided items
        
    Returns:
        List of matching items
    """
    return [item for item in required_items if item in provided_items]

def get_missing_items(required_items: List[str], provided_items: List[str]) -> List[str]:
    """
    Get list of missing items that are required but not provided
    
    Args:
        required_items: List of required items
        provided_items: List of provided items
        
    Returns:
        List of missing items
    """
    return [item for item in required_items if item not in provided_items]

def get_extra_items(required_items: List[str], provided_items: List[str]) -> List[str]:
    """
    Get list of extra items that are provided but not required
    
    Args:
        required_items: List of required items
        provided_items: List of provided items
        
    Returns:
        List of extra items
    """
    return [item for item in provided_items if item not in required_items]