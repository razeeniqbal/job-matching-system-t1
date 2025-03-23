"""
Dashboard tab UI for the job matching system.
"""
import streamlit as st
from typing import Dict, List, Any

from modules.config_manager import ConfigManager
from modules.data_manager import DataManager
from modules.scoring_service import ScoringService
from modules.visualization import Visualizer
from ui.common import display_weight_sliders

def render_dashboard(config_manager: ConfigManager):
    """
    Render the dashboard tab
    
    Args:
        config_manager: ConfigManager instance
    """
    # Check if we have data to analyze
    if st.session_state.data_to_analyze is not None:
        # Show header
        st.header("Job Matching Analysis Dashboard")
        
        # Show data source
        if st.session_state.get('using_uploaded_data', False):
            st.info("Analyzing custom uploaded data")
        else:
            st.info("Analyzing sample data")
        
        # Get the data
        job_data = st.session_state.data_to_analyze
        
        # Display number of job applications
        st.write(f"**Number of job applications:** {len(job_data)}")
        
        # Display weight adjustment sliders
        custom_weights = display_weight_sliders(config_manager)
        st.session_state.custom_weights = custom_weights
        
        # Initialize scoring service with custom weights
        scoring_service = ScoringService(config_manager, custom_weights)
        
        # Score all applications
        results = scoring_service.score_all_applications(job_data)
        
        # Convert to dataframe for visualization
        results_df = Visualizer.create_results_dataframe(results)
        
        # Display component scores table
        st.subheader("Job Application Component Scores")
        Visualizer.display_component_scores_table(results_df)
        
        # Visualize results
        st.subheader("Score Visualization")
        
        # Display total scores chart
        Visualizer.display_total_scores_chart(results_df)
        
        # Display component scores chart
        Visualizer.display_component_scores_chart(results_df)
        
        # Display final scores table
        st.header("Final Match Scores")
        Visualizer.display_final_scores_table(results)
        
        # Export options
        Visualizer.export_results(results)
        
        # Show detailed breakdown if debug mode is on
        if st.session_state.get('debug_mode', False):
            Visualizer.display_debug_information(results)
            
    else:
        # No data to analyze, show instructions
        st.info("No data loaded yet. Please go to the 'Upload Data' tab to load data or click below to use sample data.")
        
        if st.button("Use Sample Data"):
            # Load sample data
            sample_data = DataManager.load_sample_jobs()
            
            # Store in session state
            st.session_state.data_to_analyze = sample_data
            st.session_state.using_uploaded_data = False
            
            # Rerun to refresh with data
            st.rerun()