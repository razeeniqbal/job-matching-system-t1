"""
Scoring service for the job matching system.
Handles calculating scores for job applications.
"""
import logging
from typing import Dict, List, Any

from modules.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ScoringService:
    """Service for scoring candidate matches"""
    
    def __init__(self, config_manager: ConfigManager, custom_weights: Dict[str, float] = None):
        """
        Initialize with configuration manager and optional custom weights
        
        Args:
            config_manager: ConfigManager instance
            custom_weights: Optional dictionary of custom weights
        """
        self.config = config_manager
        self.weights = custom_weights or self.config.get_weights()
    
    def score_core_skills(self, job_requirements: Dict[str, Any], talent_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate core skills score
        
        Args:
            job_requirements: Job requirements dictionary
            talent_profile: Talent profile dictionary
            
        Returns:
            Dictionary with raw_score and weighted_score
        """
        required_skills = job_requirements.get("core_skills", [])
        candidate_skills = talent_profile.get("skills", [])
        
        if not required_skills:
            return {"raw_score": 0, "weighted_score": 0}
        
        # Find matching skills
        matching_skills = [skill for skill in required_skills if skill in candidate_skills]
        
        # Calculate percentage match
        match_percentage = (len(matching_skills) / len(required_skills)) * 100
        weighted_score = match_percentage * self.weights.get("core_skills", 0.5)
        
        return {
            "raw_score": match_percentage,
            "weighted_score": weighted_score
        }
    
    def score_experience(self, job_requirements: Dict[str, Any], talent_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate experience score
        
        Args:
            job_requirements: Job requirements dictionary
            talent_profile: Talent profile dictionary
            
        Returns:
            Dictionary with raw_score and weighted_score
        """
        min_experience = job_requirements.get("min_experience", 0)
        candidate_experience = talent_profile.get("experience", 0)
        
        if min_experience == 0:
            raw_score = 100
        else:
            experience_ratio = (candidate_experience / min_experience) * 100
            raw_score = min(experience_ratio, 100)
        
        return {
            "raw_score": raw_score,
            "weighted_score": raw_score * self.weights.get("experience", 0.2)
        }
    
    def score_education(self, job_requirements: Dict[str, Any], talent_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate education score
        
        Args:
            job_requirements: Job requirements dictionary
            talent_profile: Talent profile dictionary
            
        Returns:
            Dictionary with raw_score and weighted_score
        """
        education_hierarchy = self.config.get_education_hierarchy()
        required_education = job_requirements.get("education", "")
        candidate_education = talent_profile.get("education", "")
        
        if not required_education or not candidate_education:
            return {"raw_score": 0, "weighted_score": 0}
        
        try:
            required_level = education_hierarchy.index(required_education)
            candidate_level = education_hierarchy.index(candidate_education)
            
            # Lower index means higher level in hierarchy
            if candidate_level <= required_level:  # Meets or exceeds
                raw_score = 100
            else:
                # Calculate partial score based on distance in hierarchy
                max_distance = len(education_hierarchy) - 1
                actual_distance = candidate_level - required_level
                raw_score = max(0, 100 - (actual_distance / max_distance) * 100)
                
        except ValueError:
            raw_score = 0
        
        return {
            "raw_score": raw_score,
            "weighted_score": raw_score * self.weights.get("education", 0.15)
        }
    
    def score_certifications(self, job_requirements: Dict[str, Any], talent_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate certifications score
        
        Args:
            job_requirements: Job requirements dictionary
            talent_profile: Talent profile dictionary
            
        Returns:
            Dictionary with raw_score and weighted_score
        """
        required_certs = job_requirements.get("certifications", [])
        candidate_certs = talent_profile.get("certifications", [])
        
        if not required_certs:
            return {"raw_score": 100, "weighted_score": 100 * self.weights.get("certifications", 0.15)}
        
        # Find matching certifications
        matching_certs = [cert for cert in required_certs if cert in candidate_certs]
        
        # Calculate percentage match
        match_percentage = (len(matching_certs) / len(required_certs)) * 100
        
        return {
            "raw_score": match_percentage,
            "weighted_score": match_percentage * self.weights.get("certifications", 0.15)
        }
    
    def score_job_application(self, job_app: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a job application
        
        Args:
            job_app: Job application dictionary
            
        Returns:
            Dictionary with scoring results
        """
        job_requirements = job_app.get("job_requirements", {})
        talent_profile = job_app.get("talent_profile", {})
        
        # Calculate individual scores
        core_skills_score = self.score_core_skills(job_requirements, talent_profile)
        education_score = self.score_education(job_requirements, talent_profile)
        experience_score = self.score_experience(job_requirements, talent_profile)
        certifications_score = self.score_certifications(job_requirements, talent_profile)
        
        # Calculate total weighted score
        try:
            total_weighted_score = (
                core_skills_score.get("weighted_score", 0) +
                education_score.get("weighted_score", 0) +
                experience_score.get("weighted_score", 0) +
                certifications_score.get("weighted_score", 0)
            )
        except Exception as e:
            logger.error(f"Error calculating total score: {str(e)}")
            total_weighted_score = 0
        
        return {
            "job_app_id": job_app.get("job_app_id"),
            "total_score": round(total_weighted_score, 2),
            "scores": {
                "core_skills": core_skills_score,
                "education": education_score,
                "experience": experience_score,
                "certifications": certifications_score
            }
        }
    
    def score_all_applications(self, job_apps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score all job applications
        
        Args:
            job_apps: List of job application dictionaries
            
        Returns:
            List of scoring result dictionaries
        """
        return [self.score_job_application(job_app) for job_app in job_apps]