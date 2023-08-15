import time

import streamlit as st

from utils import read_newsletter_tab_of_spreadsheet, send_dummy_prompt_to_openai_api


st.markdown(body='# Charm Maui Wildfires Newsletter Generator')

st.markdown(body='We can add a description about this app here! :)')

st.markdown('-----')

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []

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
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    if 'initial_newsletter_draft' not in st.session_state:
        # Read parsed data from Google Spreadsheet, prepare initial prompt
        spreadsheet_str_representation = read_newsletter_tab_of_spreadsheet()

        # Send the initial newsletter prompt to OpenAI API
        with st.chat_message(name='assistant'):
            message_placeholder = st.empty()

            st.session_state.initial_newsletter_draft = send_dummy_prompt_to_openai_api(
                prompt=spreadsheet_str_representation,
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

        with st.spinner(text='Thinking...'):
            time.sleep(2)

        # Display assistant response in chat message container
        with st.chat_message(name='assistant'):
            message_placeholder = st.empty()

            response = send_dummy_prompt_to_openai_api(
                prompt=prompt,
                message_placeholder=message_placeholder,
            )

        # Add assistant response to chat history
        st.session_state.messages.append(
            {
                'role': 'assistant',
                'content': response,
            }
        )
