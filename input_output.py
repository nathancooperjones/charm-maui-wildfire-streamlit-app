import time
from typing import Any, Dict

import gspread_pandas
import pandas as pd
import requests
import streamlit as st


def read_google_spreadsheet(
    spread: str,
    sheet: int = 0,
    timeout: float = 7,
    max_retries: int = 3,
) -> gspread_pandas.spread.Spread:
    """
    Read a Google Spreadsheet using the ``gspread_pandas`` library.

    Parameters
    ----------
    spread: str
        URL of the Google Spreadsheet to read in
    sheet: int
        Sheet number of the Google Spreadsheet to read in
    timeout: float
        How long to wait, in seconds, for the server to send data before giving up
    max_retries: int
        Number of times to retry a request before giving up and displaying a Streamlit error message

    Returns
    -------
    gspread_pandas.spread.Spread

    """
    config = {
        'type': st.secrets['gcp']['type'],
        'project_id': st.secrets['gcp']['project_id'],
        'private_key_id': st.secrets['gcp']['private_key_id'],
        'private_key': st.secrets['gcp']['private_key'],
        'client_email': st.secrets['gcp']['client_email'],
        'client_id': st.secrets['gcp']['client_id'],
        'auth_uri': st.secrets['gcp']['auth_uri'],
        'token_uri': st.secrets['gcp']['token_uri'],
        'auth_provider_x509_cert_url': st.secrets['gcp']['auth_provider_x509_cert_url'],
        'client_x509_cert_url': st.secrets['gcp']['client_x509_cert_url'],
        'universe_domain': st.secrets['gcp']['universe_domain'],
    }

    client = gspread_pandas.client.Client(config=config)
    client.set_timeout(timeout=timeout)

    message_placeholder = st.empty()

    for retry_idx in range(max_retries):
        try:
            return gspread_pandas.spread.Spread(
                spread=spread,
                sheet=sheet,
                config=config,
                client=client,
            )
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
            retries_left = max_retries - retry_idx - 1

            message_placeholder.info(
                body=f'Retrying the connection to Google Sheets {retries_left} more time(s)...',
            )

            if retries_left > 0:
                time.sleep(1)

    # if we have made it here, we have failed - let's tell the user
    message_placeholder.error(
        "Hmm... we're currently having some trouble connecting to Google Sheets - please try "
        'refreshing the window to attempt the connection again. Sorry about this!'
    )
    st.stop()


def append_new_row_to_parsing_spreadsheet(
    spread: str = st.secrets['spreadsheets']['parsing_results_spreadsheet'],
    sheet: int = 0,
    **kwargs: Dict[Any, Any],
) -> None:
    """
    Append a new row to the asset tracker Google Spreadsheet.

    NOTE: This is **NOT** ACID-compliant. Calling this function twice at the same time may only
    append a single row.

    Parameters
    ----------
    spread: str
        URL of the spreadsheet to add the new row to
    sheet: int
        Sheet number of the Google Spreadsheet to write to
    **kwargs: keyword arguments
        Keyword arguments with keys being column names and values being the value to add in the
        corresponding spreadsheet cell

    Side Effects
    ------------
    Appends a new row to the Maui Wildfire Parsing Results Google Spreadsheet.

    """
    new_row_df = pd.DataFrame(data=[kwargs])

    sheet = read_google_spreadsheet(
        spread=spread,
        sheet=sheet,
    )

    new_row_index = sheet.get_sheet_dims()[0] + 1

    sheet.df_to_sheet(
        df=new_row_df,
        index=False,
        headers=None,
        start=(new_row_index, 1),
        replace=False,
    )
