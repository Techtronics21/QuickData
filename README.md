<div align="center">

# QucikData

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An AI-powered data agent that processes data from CSV files or Google Sheets, performs searches using LLMs, and provides insights through a Streamlit interface.

[Features](#features) • [Screenshots](#screenshots) • [Quick Start](#quick-start-guide) • [Setup](#setup) • [Documentation](#project-structure)

<img src="assets/main-dashboard.png" alt="Main Dashboard" width="100%"/>

</div>

---

## ✨ Features

- 📊 Upload CSV files or connect to Google Sheets
- 🔍 Perform entity extraction and search using LLMs
- 📈 Display and download processed data

## 📸 Screenshots

<table style="border-spacing: 0 20px; border-collapse: separate;">
  <tr>
    <td width="100%" style="padding: 20px 0;">
      <img src="assets/data-upload.png" alt="Data Upload" width="100%"/>
      <p align="center"><i>Data Upload Interface</i></p>
    </td>
  </tr>
  <tr>
    <td width="100%" style="padding: 20px 0;">
      <img src="assets/search-interface.png" alt="Search Interface" width="100%"/>
      <p align="center"><i>Search Interface</i></p>
    </td>
  </tr>
  <tr>
    <td width="100%" style="padding: 20px 0;">
      <img src="assets/results-view.png" alt="Results View" width="100%"/>
      <p align="center"><i>Results View</i></p>
    </td>
  </tr>
</table>

## 🚀 Quick Start Guide

<details open>
<summary>Watch our quick demo video</summary>
<br>
<a href="https://youtu.be/your-video-id">
    <img src="assets/video-thumbnail.png" alt="Demo Video" width="100%"/>
</a>
</details>

### 📥 Step 1: Upload Data
1. Launch the application
2. Click "Upload CSV" or "Connect Google Sheets"
3. Select your data source

### ⚙️ Step 2: Process Data
1. Choose processing options
2. Click "Process Data"
3. Wait for AI analysis

### 📊 Step 3: View Results
1. Explore the processed data
2. Download results if needed
3. Perform additional searches

## 🛠️ Setup

<details>
<summary>Click to expand setup instructions</summary>

1. Clone the repository.

2. Create and activate a virtual environment:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Set up environment variables in the `.env` file:

   ```txt
   GEMINI_API_KEY=your_gemini_api_key
   SERPAPI_API_KEY=your_serpapi_api_key
   ```

5. Obtain Google Sheets API credentials:
   - Place your `credentials.json` file in the config directory.

6. Configure the application settings in `config.yaml`.

</details>

## 🎯 Running the Application

Run the setup script:

```sh
./setup.sh
```

Start the application:

```sh
./run.sh
```

Access the application at `http://localhost:8501`.

## Testing

Run the unit tests in the `tests` directory:

```sh
python -m unittest discover tests
```

## Project Structure
<details>
<summary> Click to expand to see the project structure </summary>
- `config/`: Configuration files
  - `config.yaml`: Application configuration
  - `credentials.json`: Google API credentials
  - `token.json`: OAuth token
- `src/`: Source code
  - `dashboard/`: UI components
    - `ui.py`: Streamlit interface
  - `services/`: Core services
    - `csv_handler.py`: CSV file operations
    - `llm_service.py`: Language model service
    - `search_service.py`: Search functionality
    - `sheets_handler.py`: Google Sheets integration
  - `utils/`: Utility functions
    - `env_utils.py`: Environment variables
    - `helpers.py`: Helper functions
    - `rate_limiter.py`: Rate limiting
    - `setup.py`: Setup utilities
  - `main.py`: Application entry point
- `tests/`: Unit tests
  - `test_csv_handler.py`
  - `test_llm_service.py`
  - `test_search_service.py`
  - `test_sheets_handler.py`
  - `test_ui.py`
- `.env`: Environment variables
- `README`: Project documentation
- `requirements.txt`: Dependencies
- `run.sh`: Run script
- `setup.sh`: Setup script
</details>
