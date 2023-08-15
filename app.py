from datetime import date

import openai
import streamlit as st

from utils import (
    read_newsletter_tab_of_spreadsheet,
    send_dummy_prompt,
    send_prompt_to_openai_api,
)


DUMMY_MODE = False  # e.g. should we actually send requests to OpenAI or not


st.markdown(body='# Charm Maui Wildfires Newsletter Generator')

st.markdown(body='TODO: add a description about this app here!')

st.markdown('-----')

# Initialize OpenAI and session state variables
openai.api_key = st.secrets['openai']['api_key']

if 'messages' not in st.session_state:
    st.session_state.messages = []

    with open(file='initial_prompt.txt', mode='r') as fp:
        initial_prompt_string = fp.read()

    initial_prompt_string += f'The current date today is: {date.today()}'

    st.session_state.messages.append(
        {
            'role': 'system',
            'content': initial_prompt_string,
        }
    )

if 'generation_mode' not in st.session_state:
    st.session_state.generation_mode = False


# Set up button to begin generation
button_placeholder = st.empty()

if not st.session_state.generation_mode:
    if button_placeholder.button(label='Generate newsletter!'):
        st.session_state.generation_mode = True


# Kick off chat with OpenAI API
if st.session_state.generation_mode:
    button_placeholder.empty()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message['role'] != 'system':
            with st.chat_message(message['role'], avatar=message.get('avatar')):
                st.markdown(message['content'])

    if 'initial_newsletter_draft' not in st.session_state:
        # Read parsed data from Google Spreadsheet, prepare initial prompt
        spreadsheet_str_representation = read_newsletter_tab_of_spreadsheet()

        avatar = '📧'

        with st.chat_message(name='user', avatar=avatar):
            st.markdown(body=spreadsheet_str_representation)

        st.session_state.messages.append(
            {
                'role': 'user',
                'content': spreadsheet_str_representation,
                'avatar': avatar,
            }
        )

        # Send the initial newsletter prompt to OpenAI API
        with st.chat_message(name='assistant'):
            message_placeholder = st.empty()

            with st.spinner(text='Generating a response...'):
                if DUMMY_MODE:
                    st.session_state.initial_newsletter_draft = send_dummy_prompt(
                        message_placeholder=message_placeholder,
                    )
                else:
                    st.session_state.initial_newsletter_draft = send_prompt_to_openai_api(
                        message_placeholder=message_placeholder,
                    )

        st.session_state.messages.append(
            {
                'role': 'assistant',
                'content': st.session_state.initial_newsletter_draft,
            }
        )

    prompt = st.chat_input(placeholder='What would you like to change about this newsletter draft?')

    if prompt:
        # Display user message in chat message container
        with st.chat_message(name='user'):
            st.markdown(body=prompt)

        # Add user message to chat history
        st.session_state.messages.append(
            {
                'role': 'user',
                'content': prompt,
            }
        )

        # Display assistant response in chat message container
        with st.chat_message(name='assistant'):
            message_placeholder = st.empty()

            with st.spinner(text='Generating a response...'):
                if DUMMY_MODE:
                    response = send_dummy_prompt(
                        message_placeholder=message_placeholder,
                    )
                else:
                    response = send_prompt_to_openai_api(
                        message_placeholder=message_placeholder,
                    )

        # Add assistant response to chat history
        st.session_state.messages.append(
            {
                'role': 'assistant',
                'content': response,
            }
        )
