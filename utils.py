import time

import openai
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


def send_dummy_prompt_to_openai_api(
    prompt: str,
    message_placeholder: st.delta_generator.DeltaGenerator,
) -> str:
    """
    Send a prompt to the OpenAI API and return the parsed response as a string.

    Parameters
    ----------
    prompt: str

    Returns
    -------
    response_str: str

    """
    response = f'This is the "GPT API" (wink wink)! You just passed in:  \n{prompt}'

    response_str = ''

    # Simulate stream of response with milliseconds delay
    for response_chunk in response:
        response_str += response_chunk

        time.sleep(0.01)

        if message_placeholder is not None:
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(body=response_str + '▌')

    if message_placeholder is not None:
        message_placeholder.markdown(body=response_str)

    return response_str


def send_initial_prompt_to_openai_api(prompt: str) -> str:
    """
    Send a prompt to the OpenAI API and return the parsed response as a string.

    Parameters
    ----------
    prompt: str

    Returns
    -------
    response_str: str

    """
    # TODO
    with st.spinner(text='Thinking...'):
        time.sleep(2)

    return f'This is the "GPT API" (wink wink)! You just passed in:  \n{prompt}'


def send_subsequent_prompt_to_openai_api(
    prompt: str,
    message_placeholder: st.delta_generator.DeltaGenerator,
) -> str:
    """
    Send a prompt to the OpenAI API and return the parsed response as a string.

    Parameters
    ----------
    prompt: str

    Returns
    -------
    response_str: str

    """
    response_str = ''

    for response in openai.ChatCompletion.create(
        model=st.session_state["openai_model"],
        messages=[
            {'role': m['role'], 'content': m['content']}
            for m in st.session_state.messages
        ],  # TODO: get this formatting right
        stream=True,
    ):
        response_str += response.choices[0].delta.get('content', '')

        if message_placeholder is not None:
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(response_str + '▌')

    if message_placeholder is not None:
        message_placeholder.markdown(response_str)

    return response_str
