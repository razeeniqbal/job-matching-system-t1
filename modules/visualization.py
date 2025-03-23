"""
Visualization module for the job matching system.
Handles creating charts and visualizations for job matching data.
"""
import json
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Any

class Visualizer:
    """Handles visualization of job matching data"""
    
    @staticmethod
    def create_results_dataframe(results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create a DataFrame from scoring results
        
        Args:
            results: List of scoring result dictionaries
            
        Returns:
            Pandas DataFrame with formatted results
        """
        # Convert to dataframe for display
        results_df = pd.DataFrame([
            {
                "Job App ID": r["job_app_id"],
                "Total Score": r["total_score"],
                "Core Skills": r["scores"]["core_skills"]["raw_score"],
                "Experience": r["scores"]["experience"]["raw_score"],
                "Education": r["scores"]["education"]["raw_score"],
                "Certifications": r["scores"]["certifications"]["raw_score"]
            } for r in results
        ])
        
        return results_df
    
    @staticmethod
    def format_results_dataframe(results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Format results DataFrame with percentages
        
        Args:
            results_df: Raw results DataFrame
            
        Returns:
            Formatted DataFrame with percentages
        """
        # Format the results dataframe to include % signs and round to 2 decimal places
        formatted_df = results_df.copy()
        for col in ['Core Skills', 'Experience', 'Education', 'Certifications']:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2f}%")
        formatted_df["Total Score"] = formatted_df["Total Score"].apply(lambda x: f"{x:.2f}%")
        
        return formatted_df
    
    @staticmethod
    def display_component_scores_table(results_df: pd.DataFrame):
        """
        Display component scores as a formatted table
        
        Args:
            results_df: Results DataFrame
        """
        # Format the dataframe
        formatted_df = Visualizer.format_results_dataframe(results_df)
        
        # Display as a dataframe
        st.dataframe(
            formatted_df, 
            hide_index=True,
            use_container_width=True
        )
    
    @staticmethod
    def display_total_scores_chart(results_df: pd.DataFrame):
        """
        Display total scores as a bar chart
        
        Args:
            results_df: Results DataFrame
        """
        # Create a bar chart of total scores
        st.write("Total Scores by Job Application")
        st.bar_chart(results_df.set_index("Job App ID")["Total Score"])
    
    @staticmethod
    def display_component_scores_chart(results_df: pd.DataFrame):
        """
        Display component scores as a grouped bar chart
        
        Args:
            results_df: Results DataFrame
        """
        st.write("Component Scores by Job Application")
        
        # Reshape data for grouped bar chart
        component_df = results_df.melt(
            id_vars=["Job App ID"],
            value_vars=["Core Skills", "Experience", "Education", "Certifications"],
            var_name="Component",
            value_name="Score"
        )
        
        # Create pivot table for visualization
        # Using "mean" as a string instead of np.mean function to avoid FutureWarning
        chart_data = pd.pivot_table(
            component_df,
            values="Score",
            index=["Job App ID"],
            columns=["Component"],
            aggfunc="mean"  # Changed from np.mean to "mean"
        )
        
        # Display the chart
        st.bar_chart(chart_data)
    
    @staticmethod
    def display_final_scores_table(results: List[Dict[str, Any]]):
        """
        Display final scores as a sorted table
        
        Args:
            results: List of scoring result dictionaries
        """
        # Create a simplified dataframe with just ID and total score
        final_scores_df = pd.DataFrame([
            {
                "Job Application ID": r["job_app_id"],
                "Total Match Score (%)": r["total_score"]
            } for r in results
        ]).sort_values(by="Total Match Score (%)", ascending=False)
        
        # Format the total score with 2 decimal places
        final_scores_df["Total Match Score (%)"] = final_scores_df["Total Match Score (%)"].apply(lambda x: f"{x:.2f}%")
        
        # Display as a styled table
        st.dataframe(
            final_scores_df,
            hide_index=True,
            use_container_width=True
        )
    
    @staticmethod
    def export_results(results: List[Dict[str, Any]]):
        """
        Create export buttons for results
        
        Args:
            results: List of scoring result dictionaries
        """
        st.subheader("Export Results")
        
        # Convert results to various formats for export
        results_json = json.dumps([{
            "job_app_id": r["job_app_id"],
            "total_score": r["total_score"]
        } for r in results], indent=2)
        
        # Create download buttons for different formats
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON download
            st.download_button(
                label="Download JSON Results",
                data=results_json,
                file_name="job_matching_results.json",
                mime="application/json"
            )
        
        with col2:
            # CSV download
            csv_data = pd.DataFrame([{
                "job_app_id": r["job_app_id"],
                "total_score": r["total_score"]
            } for r in results]).to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="Download CSV Results",
                data=csv_data,
                file_name="job_matching_results.csv",
                mime="text/csv"
            )
    
    @staticmethod
    def display_debug_information(results: List[Dict[str, Any]]):
        """
        Display detailed debug information for results
        
        Args:
            results: List of scoring result dictionaries
        """
        st.header("Debug Information")
        for result in results:
            with st.expander(f"Job Application {result['job_app_id']} - Score: {result['total_score']}"):
                st.json(result)