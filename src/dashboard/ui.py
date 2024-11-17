import pandas as pd
import streamlit as st
import yaml

from services.llm_service import LLMService
from services.search_service import SearchService
from services.sheets_handler import GoogleSheetsHandler
from utils.env_utils import get_env_variable, load_env_variables

def set_custom_theme():
    st.set_page_config(
        page_title="AI Data Agent",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/yourusername/ai-data-agent',
            'Report a bug': "https://github.com/yourusername/ai-data-agent/issues",
            'About': "AI Data Agent - Automated data enrichment tool"
        }
    )
    
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stProgress > div > div > div > div {
            background-color: #1f77b4;
        }
        .stAlert > div {
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .footer {
            position: fixed;
            bottom: 0;
            right: 0;
            padding: 10px;
            font-size: 12px;
            color: #666;
        }
        .css-1v0mbdj.e115fcil1 {
            padding-top: 2em;
            text-align: center;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 80rem;
        }
        .stMarkdown {
            max-width: 100%;
        }
        .stExpander {
            border: 1px solid #f0f2f6;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .stDataFrame {
            border: 1px solid #f0f2f6;
            border-radius: 0.5rem;
            padding: 1rem;
        }
        div[data-testid="stSidebarNav"] {
            background-image: none;
        }
        </style>
    """, unsafe_allow_html=True)

def load_config():
    load_env_variables()
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Replace environment variables
    config["api_keys"]["serpapi"] = get_env_variable("SERPAPI_API_KEY")
    config["api_keys"]["groq"] = get_env_variable("GROQ_API_KEY")

    return config


def initialize_services(config):
    try:
        # Initialize services only once
        if "services_initialized" not in st.session_state:
            sheets_handler = GoogleSheetsHandler(
                config["google_sheets"]["credentials_file"]
            )
            llm_service = LLMService(config["api_keys"]["groq"])
            search_service = SearchService(config["api_keys"]["serpapi"])

            st.session_state["sheets_handler"] = sheets_handler
            st.session_state["llm_service"] = llm_service
            st.session_state["search_service"] = search_service
            st.session_state["services_initialized"] = True

        return (
            st.session_state["sheets_handler"],
            st.session_state["llm_service"],
            st.session_state["search_service"],
        )
    except Exception as e:
        st.error(f"Error initializing services: {str(e)}")
        return None, None, None


def extract_sheet_id_from_url(url: str) -> str:
    """Extract the sheet ID from a Google Sheets URL."""
    try:
        if "/spreadsheets/d/" in url:
            sheet_id = url.split("/spreadsheets/d/")[1].split("/")[0]
            return sheet_id
        raise ValueError("Invalid Google Sheets URL")
    except Exception:
        raise ValueError("Invalid Google Sheets URL format")


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


def main():
    try:
        set_custom_theme()
        
        # Sidebar navigation with improved styling
        with st.sidebar:
            # Center logo and make it bigger
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("logo.jpg", width=200)
            
            st.title("Navigation")
            page = st.radio("Select Page", ["Home", "Data Processing"])
            
            st.markdown("---")
            st.markdown("### About")
            st.info("AI Data Agent helps you enrich your data using AI and search services.")
            
            # Add copyright at bottom of sidebar
            st.markdown("---")
            st.markdown(
                "<div style='text-align: center; color: #666; font-size: 12px;'>© Arnav Thakur 2024</div>", 
                unsafe_allow_html=True
            )

        if page == "Home":
            st.title("QuickData")
            st.markdown("### Welcome to AI Data Agent!")
            st.markdown("""
                This tool helps you to:
                - Load data from CSV files or Google Sheets
                - Search for information about entities
                - Extract structured data using AI
            """)
            
        elif page == "Data Processing":
            st.title("Data Processing")
            
            config = load_config()
            services = initialize_services(config)
            
            if not all(services):
                st.error("⚠️ Service initialization failed. Check configuration.")
                return
                
            sheets_handler, llm_service, search_service = services
            
            # Store loaded data in session state to persist between page switches
            if "loaded_df" not in st.session_state:
                st.session_state.loaded_df = None
            
            with st.expander(" Select Data Source", expanded=True):
                data_source = st.radio("Choose your data source:", ["CSV Upload", "Google Sheets"])
                
                if data_source == "CSV Upload":
                    uploaded_file = st.file_uploader("Upload CSV file", type="csv", help="Upload your CSV file containing the entities")
                    if uploaded_file:
                        st.session_state.loaded_df = pd.read_csv(uploaded_file)
                        st.success("✅ CSV file loaded successfully!")
                else:
                    sheet_url = st.text_input("Enter Google Sheet URL", help="Paste the full URL of your Google Sheet")
                    if sheet_url:
                        try:
                            with st.spinner("📊 Loading sheet data..."):
                                sheet_id = extract_sheet_id_from_url(sheet_url)
                                st.session_state.loaded_df = sheets_handler.get_sheet_data(sheet_id)
                            st.success("✅ Sheet data loaded successfully!")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            if st.session_state.loaded_df is not None:
                df = st.session_state.loaded_df  # Use the persisted dataframe
                with st.expander("", expanded=True):
                    # Show data summary
                    st.markdown("### 📊 Data Summary")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"Total Rows: {len(df)}")
                    with col2:
                        st.info(f"Total Columns: {len(df.columns)}")
                    
                    # Column selection with preview
                    st.markdown("### 📋 Select Data")
                    selected_columns = st.multiselect(
                        "Choose columns to process",
                        df.columns,
                        help="Select one or more columns containing the entities to search for"
                    )
                    
                    if selected_columns:
                        # Show preview of selected data with height limit
                        st.markdown("#### Selected Data Preview")
                        st.dataframe(
                            df[selected_columns].head(3), 
                            use_container_width=False,
                            height=150,  # Limit height
                            width=630  # Limit width
                        )
                        
                        # Row range selection with visual feedback
                        st.markdown("### 📏 Data Range")
                        col1, col2 = st.columns(2)
                        with col1:
                            total_rows = len(df)
                            start_row, end_row = st.slider(
                                "Select row range",
                                0, total_rows, (0, total_rows),
                                help="Select the range of rows to process"
                            )
                        with col2:
                            st.info(f"Selected Range: {start_row} to {end_row} ({end_row - start_row} rows)")
                        
                        # Multiple prompts configuration
                        st.markdown("### 🔍 Search Configuration")
                        prompt_template = "Find information about {entity}"
                        prompts = []
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            prompt_base = st.text_input(
                                "What information do you want to find?",
                                value="Find the email address",
                                key="prompt_1"
                            )
                            prompts.append(f"{prompt_base} of {{entity}}")

                        # Add more prompts dynamically
                        if "num_prompts" not in st.session_state:
                            st.session_state.num_prompts = 1

                        if st.button("➕ Add Another Search"):
                            st.session_state.num_prompts += 1

                        for i in range(2, st.session_state.num_prompts + 1):
                            additional_prompt = st.text_input(
                                f"Additional information #{i}",
                                value="",
                                key=f"prompt_{i}"
                            )
                            if additional_prompt:
                                prompts.append(f"{additional_prompt} of {{entity}}")

                        # Export options
                        st.markdown("### 📤 Export Configuration")
                        export_option = st.radio(
                            "Choose export format:",
                            ["CSV", "Google Sheets"],
                            horizontal=True
                        )

                        # Process button with count summary
                        total_to_process = len(df.iloc[start_row:end_row]) * len(selected_columns)
                        st.info(f"🎯 Will process {total_to_process} items")
                        
                        if st.button("🚀 Start Processing", type="primary", use_container_width=True):
                            try:
                                with st.spinner("Processing data..."):
                                    progress_bar = st.progress(0)
                                    progress_cols = st.columns([2, 1])
                                    status_text = progress_cols[0].empty()
                                    count_text = progress_cols[1].empty()
                                    
                                    results = []
                                    selected_data = df.iloc[start_row:end_row]
                                    total = len(selected_data) * len(selected_columns)
                                    current = 0
                                    
                                    for column in selected_columns:
                                        for entity in selected_data[column].dropna():
                                            status_text.text(f"Processing {entity}...")
                                            count_text.text(f"Progress: {current + 1}/{total} entities")
                                            progress_bar.progress((current + 1) / total)
                                            
                                            query = prompt_template.replace("{entity}", str(entity))
                                            search_results = search_service.search(query)
                                            extracted_info = llm_service.extract_multiple_information(
                                                search_results, prompts
                                            )
                                            
                                            # Add single result with all sources
                                            sources = [result["url"] for result in search_results]
                                            results.append({
                                                "Column": column,
                                                "Entity": entity,
                                                "Sources": " | ".join(sources),
                                                "Extracted Information": extracted_info["result"]
                                            })
                                            current += 1
                                    
                                    progress_bar.progress(100)
                                    status_text.success("✨ Processing complete!")
                                    count_text.text(f"Completed: {total}/{total} entities")
                                    
                                    # Store results in session state
                                    st.session_state.results_df = pd.DataFrame(results)
                                    
                                    # Export results based on user selection
                                    results_df = pd.DataFrame(results)
                                    if export_option == "Google Sheets":
                                        sheet_url = sheets_handler.export_results(results_df)
                                        st.success(f"✅ Results exported to Google Sheets: [Open Sheet]({sheet_url})")
                                    else:
                                        st.download_button(
                                            label="📥 Download CSV",
                                            data=convert_df(results_df),
                                            file_name="results.csv",
                                            mime="text/csv",
                                        )

                            except Exception as e:
                                st.error(f"❌ Processing error: {str(e)}")
                                st.exception(e)

    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
