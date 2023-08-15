import streamlit as st

from input_output import read_google_spreadsheet


def read_newsletter_tab_of_spreadsheet() -> str:
    """
    Read the newsletter parsed results table from the Spreadsheet and convert it all into a single
    prompt string we can send to OpenAI.

    Returns
    -------
    newsletter_results_prompt: str

    """
    with st.spinner(text='Reading from Google Spreadsheets...'):
        spreadsheet_df = (
            read_google_spreadsheet(
                spread=st.secrets['spreadsheets']['parsing_results_spreadsheet'],
                sheet=0,
            )
            .sheet_to_df(index=None)
        )

    spreadsheet_str_representation = ''

    for idx, row in spreadsheet_df.iterrows():
        # add a line separator to the end of every email except the last
        if idx != 0:
            spreadsheet_str_representation += '  \n-----  \n  \n'

        spreadsheet_str_representation += (
            f'Email ID: {row["id"]}  \n'
            f'Email Date: {row["date"]}  \n'
            f'Email Body: {row["body"]}  \n'
        )

    return spreadsheet_str_representation


def send_prompt_to_openai_api(prompt: str) -> str:
    """
    Send a prompt to the OpenAI API and return the parsed response as a string.

    Parameters
    ----------
    prompt: str

    Returns
    -------
    response_str: str

    """
    return f'This is the "GPT API" (wink wink)! You just passed in:  \n{prompt}'
