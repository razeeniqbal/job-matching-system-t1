"""
Configuration manager for the job matching system.
"""
import yaml
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages loading and accessing configuration settings"""
    
    def __init__(self, config_path: str = "config/scoring_config.yaml"):
        """
        Initialize with path to configuration file
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            Dictionary containing configuration values
        """
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found. Using default configuration.")
            return self._default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """
        Return default configuration if config file cannot be loaded
        
        Returns:
            Dictionary containing default configuration values
        """
        return {
            "weights": {
                "core_skills": 0.5,
                "experience": 0.2,
                "education": 0.15,
                "certifications": 0.15
            },
            "education_hierarchy": [
                "PhD", 
                "Master's", 
                "Bachelor's", 
                "Associate's", 
                "Diploma", 
                "High School"
            ],
            "thresholds": {
                "minimum_match_score": 40
            },
            "debug_mode": False
        }
    
    def get_weights(self) -> Dict[str, float]:
        """Get scoring weights"""
        return self.config.get("weights", {})
    
    def get_education_hierarchy(self) -> List[str]:
        """Get education level hierarchy (highest to lowest)"""
        return self.config.get("education_hierarchy", [])
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get threshold settings"""
        return self.config.get("thresholds", {})
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.config.get("debug_mode", False)