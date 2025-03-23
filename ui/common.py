"""
Common UI elements for the job matching system.
"""
import streamlit as st
from typing import Dict

from modules.config_manager import ConfigManager

def display_weight_sliders(config_manager: ConfigManager) -> Dict[str, float]:
    """
    Display sliders for adjusting scoring weights
    
    Args:
        config_manager: ConfigManager instance
        
    Returns:
        Dictionary with adjusted weights
    """
    st.write("### Adjust Scoring Weights")
    st.write("Modify the weights for each scoring component (must sum to 100%)")
    
    weights = config_manager.get_weights()
    
    col1, col2 = st.columns(2)
    
    with col1:
        core_skills_weight = st.slider(
            "Core Skills Weight (%)", 
            min_value=0, 
            max_value=100, 
            value=int(weights.get("core_skills", 0.5) * 100),
            step=5
        )
        
        experience_weight = st.slider(
            "Experience Weight (%)", 
            min_value=0, 
            max_value=100, 
            value=int(weights.get("experience", 0.2) * 100),
            step=5
        )
    
    with col2:
        education_weight = st.slider(
            "Education Weight (%)", 
            min_value=0, 
            max_value=100, 
            value=int(weights.get("education", 0.15) * 100),
            step=5
        )
        
        certifications_weight = st.slider(
            "Certifications Weight (%)", 
            min_value=0, 
            max_value=100, 
            value=int(weights.get("certifications", 0.15) * 100),
            step=5
        )
    
    # Calculate total
    total = core_skills_weight + experience_weight + education_weight + certifications_weight
    
    if total != 100:
        st.warning(f"Weights sum to {total}%, but should be 100%. Results may be skewed.")
    
    # Convert to decimal
    return {
        "core_skills": core_skills_weight / 100,
        "experience": experience_weight / 100,
        "education": education_weight / 100,
        "certifications": certifications_weight / 100
    }

def display_json_structure_example():
    """Display example JSON structure in an expander"""
    with st.expander("View expected JSON structure"):
        st.code("""
[
  {
    "job_app_id": 201,
    "job_requirements": {
      "core_skills": ["Python", "Machine Learning", "SQL"],
      "min_experience": 3,
      "education": "Bachelor's",
      "certifications": ["AWS Certified"]
    },
    "talent_profile": {
      "skills": ["Python", "Machine Learning", "Deep Learning", "SQL"],
      "experience": 4,
      "education": "Master's",
      "certifications": ["AWS Certified", "Google Cloud Certified"]
    }
  },
  {
    "job_app_id": 202,
    "job_requirements": {
      "core_skills": ["Java", "Spring Boot", "Microservices"],
      "min_experience": 5,
      "education": "Bachelor's",
      "certifications": ["Oracle Java Certified"]
    },
    "talent_profile": {
      "skills": ["Java", "Spring Boot", "Microservices", "Kafka"],
      "experience": 3,
      "education": "Diploma",
      "certifications": ["Oracle Java Certified"]
    }
  }
]
        """, language="json")