import time

import openai
import streamlit as st
import tiktoken

from input_output import read_google_spreadsheet


TIKTOKEN_TOKENIZER = tiktoken.encoding_for_model(model_name=st.secrets['openai']['model'])


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

    # filter irrelevant emails out if they do NOT contain relief information
    spreadsheet_df_filtered = (
        spreadsheet_df[
            ~spreadsheet_df['relief_info'].str.lower().str.strip().str.contains('na')
        ]
        .reset_index(drop=True)
    )

    spreadsheet_str_representation = ''

    for idx, row in spreadsheet_df_filtered.iterrows():
        # add a line separator to the end of every email except the last
        if idx != 0:
            spreadsheet_str_representation += '  \n-----  \n  \n'

        spreadsheet_str_representation += (
            f'Email ID: {row["id"]}  \n'
            f'Email Date: {row["date"]}  \n'
            # f'Email Body: {row["body"]}  \n'
            f'Summarized Relief Info: {row["relief_info"]}  \n'
        )

    return spreadsheet_str_representation


def send_dummy_prompt(message_placeholder: st.delta_generator.DeltaGenerator) -> str:
    """
    Send a prompt to the OpenAI API and return the parsed response as a string.

    Parameters
    ----------
    message_placeholder: st.empty
        Placeholder to display markdown of message to. If ``None``, message will not be displayed

    Returns
    -------
    response_str: str

    """
    prompt = '  \n  \n'.join(
        [
            f'{message["role"]}:  \n  \n{message["content"]}'
            for message in st.session_state.messages
        ]
    )

    response = f'Greetings! This is the fake "GPT API"! You just passed in:  \n{prompt}'

    response_str = ''

    # Simulate stream of response with milliseconds delay
    for response_chunk in response:
        response_str += response_chunk

        time.sleep(0.001)

        if message_placeholder is not None:
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(body=response_str + '▌')

    if message_placeholder is not None:
        message_placeholder.markdown(body=response_str)

    return response_str


def send_prompt_to_openai_api(message_placeholder: st.delta_generator.DeltaGenerator) -> str:
    """
    Send a prompt to the OpenAI API and return the parsed response as a string.

    Parameters
    ----------
    message_placeholder: st.empty
        Placeholder to display markdown of message to. If ``None``, message will not be displayed

    Returns
    -------
    response_str: str

    """
    messages = []
    total_tokens = 0

    for message in reversed(st.session_state.messages):
        content_to_add = {'role': message['role'], 'content': message['content']}
        tokens_for_message = len(TIKTOKEN_TOKENIZER.encode(text=content_to_add['content']))

        if total_tokens + tokens_for_message > st.secrets['openai']['max_input_tokens']:
            break

        messages.insert(0, content_to_add)
        total_tokens += tokens_for_message

    response_str = ''

    for response in openai.ChatCompletion.create(
        model=st.secrets['openai']['model'],
        messages=messages,
        stream=True,
    ):
        response_str += response.choices[0].delta.get('content', '')

        if message_placeholder is not None:
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(response_str + '▌')

    if message_placeholder is not None:
        message_placeholder.markdown(response_str)

    return response_str
