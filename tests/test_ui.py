from unittest.mock import mock_open, patch

import pandas as pd
import pytest
import yaml

from dashboard.ui import (
    convert_df,
    extract_sheet_id_from_url,
    initialize_services,
    load_config,
)


@pytest.fixture
def mock_config():
    return {
        "api_keys": {"serpapi": "mock-serpapi-key", "gemini": "mock-gemini-key"},
        "google_sheets": {"credentials_file": "mock-credentials.json"},
    }


@patch("dashboard.ui.load_env_variables")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=yaml.dump(
        {
            "api_keys": {"serpapi": "", "gemini": ""},
            "google_sheets": {"credentials_file": "mock-credentials.json"},
        }
    ),
)
@patch("dashboard.ui.get_env_variable")
def test_load_config(mock_get_env, mock_file, mock_load_env):
    mock_get_env.side_effect = ["mock-serpapi-key", "mock-gemini-key"]

    config = load_config()

    assert config["api_keys"]["serpapi"] == "mock-serpapi-key"
    assert config["api_keys"]["gemini"] == "mock-gemini-key"
    assert config["google_sheets"]["credentials_file"] == "mock-credentials.json"


@patch("streamlit.session_state", {})
def test_initialize_services(mock_config):
    with patch("dashboard.ui.GoogleSheetsHandler") as mock_sheets:
        with patch("dashboard.ui.LLMService") as mock_llm:
            with patch("dashboard.ui.SearchService") as mock_search:
                sheets, llm, search = initialize_services(mock_config)

                mock_sheets.assert_called_once_with(
                    mock_config["google_sheets"]["credentials_file"]
                )
                mock_llm.assert_called_once_with(mock_config["api_keys"]["gemini"])
                mock_search.assert_called_once_with(mock_config["api_keys"]["serpapi"])


def test_extract_sheet_id_from_url():
    # Test valid URL
    url = "https://docs.google.com/spreadsheets/d/abc123xyz/edit#gid=0"
    assert extract_sheet_id_from_url(url) == "abc123xyz"

    # Test invalid URL
    with pytest.raises(ValueError):
        extract_sheet_id_from_url("https://invalid-url.com")


def test_convert_df():
    # Create test DataFrame
    test_df = pd.DataFrame({"col1": ["a", "b"], "col2": [1, 2]})

    # Convert to CSV
    csv_data = convert_df(test_df)

    # Check if output is bytes and contains expected content
    assert isinstance(csv_data, bytes)
    assert b"col1,col2" in csv_data
    assert b"a,1" in csv_data
    assert b"b,2" in csv_data
