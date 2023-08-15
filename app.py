import time

import streamlit as st

from utils import read_newsletter_tab_of_spreadsheet, send_prompt_to_openai_api


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

    if 'initial_newsletter_draft' not in st.session_state:
        # Read parsed data from Google Spreadsheet, prepare initial prompt
        spreadsheet_str_representation = read_newsletter_tab_of_spreadsheet()

        # Send the initial newsletter prompt to OpenAI API
        st.session_state.initial_newsletter_draft = send_prompt_to_openai_api(
            prompt=spreadsheet_str_representation,
        )

        st.session_state.messages.append(
            {
                'role': 'assistant',
                'content': st.session_state.initial_newsletter_draft,
            }
        )

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    prompt = st.chat_input('What is up?')  # TODO

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
            response = send_prompt_to_openai_api(prompt=prompt)

        # Display assistant response in chat message container
        with st.chat_message(name='assistant'):
            message_placeholder = st.empty()
            full_response = ''

            # Simulate stream of response with milliseconds delay
            for response_chunk in response:
                full_response += response_chunk

                time.sleep(0.01)

                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(body=full_response + '▌')

            message_placeholder.markdown(body=full_response)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {
                'role': 'assistant',
                'content': response,
            }
        )
