"""
Data management for the job matching system.
Handles loading, validating, and processing job application data.
"""
import json
import logging
from typing import Dict, List, Any, Tuple

import streamlit as st

logger = logging.getLogger(__name__)

class DataManager:
    """Manages job application data"""
    
    @staticmethod
    @st.cache_data
    def load_sample_jobs() -> List[Dict[str, Any]]:
        """
        Load sample job data from file
        
        Returns:
            List of job application dictionaries
        """
        try:
            with open('data/sample_jobs.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Sample jobs file not found at 'data/sample_jobs.json'")
            return []
        except json.JSONDecodeError:
            logger.error("Invalid JSON in sample jobs file")
            return []
        except Exception as e:
            logger.error(f"Error loading sample jobs: {str(e)}")
            return []
    
    @staticmethod
    def validate_job_data(data: Any) -> Tuple[bool, str]:
        """
        Validate job application data structure
        
        Args:
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(data, list):
            return False, "Data must be a list of job applications"
        
        if len(data) == 0:
            return False, "Data list is empty"
        
        for job in data:
            # Check for required fields
            if "job_app_id" not in job:
                return False, f"Missing job_app_id in job application"
            if "job_requirements" not in job:
                return False, f"Missing job_requirements in job application {job.get('job_app_id', 'unknown')}"
            if "talent_profile" not in job:
                return False, f"Missing talent_profile in job application {job.get('job_app_id', 'unknown')}"
                
            # Check job requirements structure
            req = job.get("job_requirements", {})
            if not isinstance(req.get("core_skills", []), list):
                return False, f"core_skills must be a list in job application {job.get('job_app_id')}"
            
            # Check talent profile structure
            profile = job.get("talent_profile", {})
            if not isinstance(profile.get("skills", []), list):
                return False, f"skills must be a list in job application {job.get('job_app_id')}"
            if not isinstance(profile.get("certifications", []), list):
                return False, f"certifications must be a list in job application {job.get('job_app_id')}"
        
        return True, "Data is valid"
    
    @staticmethod
    def parse_uploaded_json(content: str) -> Tuple[bool, Any, str]:
        """
        Parse and validate uploaded JSON content
        
        Args:
            content: JSON string
            
        Returns:
            Tuple of (success, data, message)
        """
        try:
            data = json.loads(content)
            is_valid, message = DataManager.validate_job_data(data)
            if is_valid:
                return True, data, f"Successfully loaded {len(data)} job applications"
            else:
                return False, None, message
        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON format: {str(e)}"
        except Exception as e:
            return False, None, f"Error processing JSON: {str(e)}"
    
    @staticmethod
    def create_custom_job_app(
        core_skills: str,
        min_experience: int,
        education: str,
        certifications: str,
        talent_skills: str,
        talent_experience: int,
        talent_education: str,
        talent_certifications: str
    ) -> Dict[str, Any]:
        """
        Create a custom job application from form inputs
        
        Returns:
            Dictionary representing a job application
        """
        return {
            "job_app_id": 999,  # Temporary ID
            "job_requirements": {
                "core_skills": [skill.strip() for skill in core_skills.split(",") if skill.strip()],
                "min_experience": min_experience,
                "education": education,
                "certifications": [cert.strip() for cert in certifications.split(",") if cert.strip()]
            },
            "talent_profile": {
                "skills": [skill.strip() for skill in talent_skills.split(",") if skill.strip()],
                "experience": talent_experience,
                "education": talent_education,
                "certifications": [cert.strip() for cert in talent_certifications.split(",") if cert.strip()]
            }
        }