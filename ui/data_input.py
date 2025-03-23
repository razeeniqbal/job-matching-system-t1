"""
Data Input tab UI for the job matching system.
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Any

from modules.config_manager import ConfigManager
from modules.data_manager import DataManager
from modules.scoring_service import ScoringService

def render_data_input(config_manager: ConfigManager):
    """
    Render the data input tab with custom job form
    
    Args:
        config_manager: ConfigManager instance
    """
    st.header("Custom Job Matching Calculator")
    
    st.write("""
    Try out the job matching algorithm with your own data. Enter job requirements and
    talent profile information to see how the matching score is calculated.
    """)
    
    # Display the custom job form
    display_custom_job_form(config_manager)
    
    # Explain modular approach
    with st.expander("How It Works", expanded=False):
        st.markdown("""
        ### How It Works
        
        The scoring system follows these steps:
        
        1. **Input Validation**: Ensures all required fields are present
        2. **Core Skills Scoring**: Calculates the percentage of required skills matched
        3. **Experience Scoring**: Evaluates if candidate meets or exceeds requirements
        4. **Education Scoring**: Compares education levels in the hierarchy
        5. **Certifications Scoring**: Calculates the percentage of required certifications
        6. **Score Aggregation**: Applies weights and calculates final score
        
        Each scoring component is implemented as a separate module, making the system
        easy to maintain and extend.
        """)

def display_custom_job_form(config_manager: ConfigManager):
    """
    Display a form for adding a custom job application
    
    Args:
        config_manager: ConfigManager instance
    """
    with st.form("job_application_form"):
        st.write("**Job Requirements**")
        core_skills = st.text_input("Core Skills (comma-separated)", "Python, Machine Learning, SQL")
        min_experience = st.number_input("Minimum Experience (years)", min_value=0, value=3)
        education_options = config_manager.get_education_hierarchy()
        education = st.selectbox("Required Education", education_options)
        certifications = st.text_input("Required Certifications (comma-separated)", "AWS Certified")
        
        st.write("**Talent Profile**")
        talent_skills = st.text_input("Talent Skills (comma-separated)", "Python, Machine Learning, Deep Learning, SQL")
        talent_experience = st.number_input("Talent Experience (years)", min_value=0, value=4)
        talent_education = st.selectbox("Talent Education", education_options)
        talent_certifications = st.text_input("Talent Certifications (comma-separated)", "AWS Certified, Google Cloud Certified")
        
        submitted = st.form_submit_button("Calculate Match Score")
        
        if submitted:
            # Create job application dictionary
            job_app = DataManager.create_custom_job_app(
                core_skills=core_skills,
                min_experience=min_experience,
                education=education,
                certifications=certifications,
                talent_skills=talent_skills,
                talent_experience=talent_experience,
                talent_education=talent_education,
                talent_certifications=talent_certifications
            )
            
            # Get custom weights if they've been set
            if 'custom_weights' in st.session_state:
                scoring_service = ScoringService(config_manager, st.session_state.custom_weights)
            else:
                scoring_service = ScoringService(config_manager)
            
            # Score the job application
            result = scoring_service.score_job_application(job_app)
            
            # Display the results
            display_custom_job_results(result)

def display_custom_job_results(result: Dict[str, Any]):
    """
    Display the results of a custom job application scoring
    
    Args:
        result: Scoring result dictionary
    """
    # Display the result with more prominence
    st.write("### Match Score Results")
    
    # Create a metrics display for the total score
    st.metric(
        label="Overall Match Score", 
        value=f"{result['total_score']:.2f}%",
        delta=f"{result['total_score'] - 50:.2f}%" if result['total_score'] >= 50 else None,
        delta_color="normal"
    )
    
    # Component scores
    component_scores = {
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
    
    st.write("#### Component Scores:")
    st.dataframe(pd.DataFrame(component_scores))
    
    # Display detailed breakdown if debug mode is on
    if st.session_state.get('debug_mode', False):
        st.write("#### Debug Information:")
        st.json(result)