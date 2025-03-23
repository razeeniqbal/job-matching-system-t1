"""
Data Upload tab UI for the job matching system.
"""
import streamlit as st
import json
from typing import Dict, List, Any

from modules.data_manager import DataManager
from ui.common import display_json_structure_example

def render_data_upload():
    """Render the data upload tab with file upload and JSON input options"""
    st.header("Upload Job Application Data")
    
    st.write("""
    Upload your own JSON file containing job applications data or paste JSON content directly.
    The data should follow the same structure as the sample data.
    """)
    
    # Create tabs for different input methods
    upload_tab, paste_tab = st.tabs(["Upload JSON File", "Paste JSON Content"])
    
    with upload_tab:
        handle_file_upload()
    
    with paste_tab:
        handle_json_paste()
    
    # Add sample data option
    st.markdown("---")
    st.write("### Or use sample data")
    
    if st.button("Load Sample Data"):
        sample_data = DataManager.load_sample_jobs()
        st.session_state.data_to_analyze = sample_data
        st.session_state.using_uploaded_data = False
        st.rerun()

    # Display example JSON structure
    display_json_structure_example()

def handle_file_upload():
    """Handle file upload functionality"""
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
                st.session_state.uploaded_data = data
                
                # Show preview
                with st.expander("Preview uploaded data", expanded=False):
                    st.json(data)
                
                # Add button to run analysis on uploaded data
                if st.button("Process Uploaded Data", key="process_upload"):
                    st.session_state.data_to_analyze = data
                    st.session_state.using_uploaded_data = True
                    st.rerun()
            else:
                st.error(f"Invalid data format: {message}")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def handle_json_paste():
    """Handle JSON paste functionality"""
    json_text = st.text_area("Paste JSON content here", height=300)
    
    if st.button("Process JSON", key="process_json"):
        if json_text:
            try:
                # Process the pasted JSON
                success, data, message = DataManager.parse_uploaded_json(json_text)
                
                if success:
                    st.success(f"JSON processed successfully! {len(data)} job applications loaded.")
                    
                    # Store the data in session state
                    st.session_state.uploaded_data = data
                    
                    # Add button to run analysis on uploaded data
                    if st.button("Process Pasted Data", key="process_paste"):
                        st.session_state.data_to_analyze = data
                        st.session_state.using_uploaded_data = True
                        st.rerun()
                else:
                    st.error(f"Invalid data format: {message}")
                    
            except Exception as e:
                st.error(f"Error processing JSON: {str(e)}")
        else:
            st.warning("Please paste JSON content before processing.")