"""
Job Matching System - Integrated Process Flow
Main application entry point
"""
import os
import logging
import streamlit as st
import json
import pandas as pd

# Import modules
from modules.config_manager import ConfigManager
from modules.data_manager import DataManager
from modules.scoring_service import ScoringService
from modules.visualization import Visualizer
from utils.helpers import format_percentage

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("job_matching_app")

# Create required directories
os.makedirs('config', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="Job Matching System",
    page_icon="💼",
    layout="wide"
)

# App title and description
st.title("Job Matching System")
st.markdown("""
This application demonstrates the job matching system that scores talent profiles against job requirements.
""")

# Load configuration
@st.cache_resource
def load_config():
    """Load configuration with caching"""
    return ConfigManager()

config_manager = load_config()

# Debug mode toggle in sidebar
with st.sidebar:
    st.header("Settings")
    debug_mode = st.checkbox("Debug Mode", value=False)
    st.session_state.debug_mode = debug_mode
    
    # About section
    st.markdown("---")
    st.info("Job Matching System - v1.0")

# Main content container
main_container = st.container()

with main_container:
    # Create tabs for input method selection
    input_method_tab, config_tab = st.tabs(["Data Input", "Scoring Configuration"])
    
    with config_tab:
        st.header("Scoring Configuration")
        
        # Display weight adjustment sliders
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
                step=5,
                key="core_skills_weight"
            )
            
            experience_weight = st.slider(
                "Experience Weight (%)", 
                min_value=0, 
                max_value=100, 
                value=int(weights.get("experience", 0.2) * 100),
                step=5,
                key="exp_weight"
            )
        
        with col2:
            education_weight = st.slider(
                "Education Weight (%)", 
                min_value=0, 
                max_value=100, 
                value=int(weights.get("education", 0.15) * 100),
                step=5,
                key="edu_weight"
            )
            
            certifications_weight = st.slider(
                "Certifications Weight (%)", 
                min_value=0, 
                max_value=100, 
                value=int(weights.get("certifications", 0.15) * 100),
                step=5,
                key="cert_weight"
            )
        
        # Calculate total
        total = core_skills_weight + experience_weight + education_weight + certifications_weight
        
        if total != 100:
            st.warning(f"Weights sum to {total}%, but should be 100%. Results may be skewed.")
        
        # Convert to decimal and store in session state
        st.session_state.custom_weights = {
            "core_skills": core_skills_weight / 100,
            "experience": experience_weight / 100,
            "education": education_weight / 100,
            "certifications": certifications_weight / 100
        }
        
        # Education hierarchy display
        st.write("### Education Hierarchy")
        education_hierarchy = config_manager.get_education_hierarchy()
        st.info("Education levels from highest to lowest: " + " > ".join(education_hierarchy))
    
    with input_method_tab:
        st.header("Data Input")
        
        # Create tabs for different input methods (reordered as requested)
        sample_tab, paste_tab, form_tab, upload_tab = st.tabs([
            "Sample Data",
            "Paste JSON", 
            "Custom Form", 
            "Upload JSON File"
        ])
        
        with sample_tab:
            st.write("Use sample data provided with the application")
            
            if st.button("Load Sample Data"):
                # Load sample data
                sample_data = DataManager.load_sample_jobs()
                
                if sample_data:
                    st.success(f"Sample data loaded successfully! {len(sample_data)} job applications available.")
                    
                    # Store in session state
                    st.session_state.job_data = sample_data
                    st.session_state.data_source = "sample"
                    
                    # Show preview
                    with st.expander("Preview sample data", expanded=False):
                        st.json(sample_data)
                    
                    # Trigger processing
                    st.session_state.trigger_processing = True
                else:
                    st.error("Error loading sample data. Please check if sample data file exists.")
        
        with paste_tab:
            st.write("Paste JSON content directly")
            json_text = st.text_area("Paste JSON content here", height=200)
            
            if st.button("Process JSON", key="process_json"):
                if json_text:
                    try:
                        # Process the pasted JSON
                        success, data, message = DataManager.parse_uploaded_json(json_text)
                        
                        if success:
                            st.success(f"JSON processed successfully! {len(data)} job applications loaded.")
                            
                            # Store the data in session state
                            st.session_state.job_data = data
                            st.session_state.data_source = "paste"
                            
                            # Trigger processing
                            st.session_state.trigger_processing = True
                        else:
                            st.error(f"Invalid data format: {message}")
                            
                    except Exception as e:
                        st.error(f"Error processing JSON: {str(e)}")
                else:
                    st.warning("Please paste JSON content before processing.")
        
        with form_tab:
            st.write("Create a custom job application")
            
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
                    
                    # Store in session state as a list with one item
                    st.session_state.job_data = [job_app]
                    st.session_state.data_source = "form"
                    
                    # Trigger processing
                    st.session_state.trigger_processing = True
        
        with upload_tab:
            st.write("Upload a JSON file containing job applications data")
            uploaded_file = st.file_uploader("Choose a JSON file", type="json")
            
            if uploaded_file is not None:
                try:
                    # Read the uploaded file
                    content = uploaded_file.read().decode('utf-8')
                    
                    # Process the uploaded content
                    success, data, message = DataManager.parse_uploaded_json(content)
                    
                    if success:
                        st.success(f"File uploaded successfully! {len(data)} job applications loaded.")
                        
                        # Store the data in session state
                        st.session_state.job_data = data
                        st.session_state.data_source = "upload"
                        
                        # Show preview
                        with st.expander("Preview uploaded data", expanded=False):
                            st.json(data)
                        
                        # Trigger processing
                        st.session_state.trigger_processing = True
                    else:
                        st.error(f"Invalid data format: {message}")
                        
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
    
    # Process data and show results immediately after input
    # No separate header or divider to create seamless flow
    if st.session_state.get('trigger_processing', False) and st.session_state.get('job_data') is not None:
        # Get the job data
        job_data = st.session_state.job_data
        
        # Get custom weights if set
        if 'custom_weights' in st.session_state:
            scoring_service = ScoringService(config_manager, st.session_state.custom_weights)
        else:
            scoring_service = ScoringService(config_manager)
        
        # Score all applications
        results = scoring_service.score_all_applications(job_data)
        
        # Convert to dataframe for visualization
        results_df = Visualizer.create_results_dataframe(results)
        
        # Display data source as a small badge
        data_source = st.session_state.get('data_source', 'unknown')
        source_labels = {
            'upload': '📤 Uploaded Data',
            'paste': '📋 Pasted JSON',
            'form': '📝 Custom Form',
            'sample': '📊 Sample Data'
        }
        
        # Directly show the results without tabs for a more seamless experience
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.subheader("Match Score Results")
            st.caption(source_labels.get(data_source, 'Data'))
            # Display final scores table with a more compact design
            Visualizer.display_final_scores_table(results)
            
            # Export options in an expander to save space
            with st.expander("Export Options"):
                Visualizer.export_results(results)
        
        with col2:
            # Show visualizations right next to the results
            st.subheader("Score Visualization")
            Visualizer.display_total_scores_chart(results_df)
            
            # Show component score breakdown for the selected job application
            if len(results) > 1:
                # If multiple results, let user select which one to examine
                job_ids = [str(r["job_app_id"]) for r in results]
                selected_job_id = st.selectbox("Select job application for detailed breakdown:", 
                                            job_ids, key="job_selector")
                
                # Find the selected result
                selected_result = next((r for r in results if str(r["job_app_id"]) == selected_job_id), results[0])
            else:
                # For single result (like from form input)
                selected_result = results[0]
            
            # Component scores for selected job
            st.write(f"**Component Breakdown for Job {selected_result['job_app_id']}**")
            component_scores = {
                "Component": ["Core Skills", "Experience", "Education", "Certifications"],
                "Raw Score": [
                    selected_result["scores"]["core_skills"]["raw_score"],
                    selected_result["scores"]["experience"]["raw_score"],
                    selected_result["scores"]["education"]["raw_score"],
                    selected_result["scores"]["certifications"]["raw_score"]
                ],
                "Weighted Score": [
                    selected_result["scores"]["core_skills"]["weighted_score"],
                    selected_result["scores"]["experience"]["weighted_score"],
                    selected_result["scores"]["education"]["weighted_score"],
                    selected_result["scores"]["certifications"]["weighted_score"]
                ]
            }
            
            # Create a DataFrame and display
            scores_df = pd.DataFrame(component_scores)
            st.dataframe(scores_df)
        
        # Display component score charts below in full width
        st.write("**Component Scores Comparison**")
        Visualizer.display_component_scores_chart(results_df)
        
        # Show detailed breakdown if debug mode is on
        if st.session_state.get('debug_mode', False):
            st.subheader("Debug Information")
            for result in results:
                with st.expander(f"Job Application {result['job_app_id']} - Score: {result['total_score']}"):
                    st.json(result)
    
    # Show JSON structure example in the sidebar
    with st.sidebar:
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
  }
]
            """, language="json")