from datetime import date, datetime

import openai
import pytz
import streamlit as st

from utils import (
    read_newsletter_tab_of_spreadsheet,
    send_dummy_prompt,
    send_prompt_to_openai_api,
)


DUMMY_MODE = False  # e.g. should we actually send requests to OpenAI or not

EMAIL_SUMMARY_AVATAR = '📧'


st.set_page_config(
    page_title='Maui Wildfires Newsletter Generator',
    page_icon='📰',
    layout='centered',
    initial_sidebar_state='collapsed',
    menu_items=None,
)

st.markdown(body='# Maui Wildfires Newsletter Generator')

st.markdown(
    body=(
        'We are processing emails to find relevant information for Maui wildfire relief and '
        'assistance for residents. This app presents an interactive way to draft newsletters. '
        'All output from this tool should be reviewed by a human before sending out to others.'
    )
)

st.markdown('-----')

# Initialize OpenAI and session state variables
openai.api_key = st.secrets['openai']['api_key']

hawaii_current_datetime = datetime.now(tz=pytz.timezone(zone='Pacific/Honolulu'))

if 'messages' not in st.session_state:
    st.session_state.messages = []

    with open(file='initial_prompt.txt', mode='r') as fp:
        initial_prompt_string = fp.read()

    initial_prompt_string += f'The current date today is: {hawaii_current_datetime.date()}'

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
    with button_placeholder.container():
        datetimes_selected = st.date_input(
            label='Select a date range of emails to consider',
            value=(date(year=2023, month=8, day=8), hawaii_current_datetime),
            max_value=hawaii_current_datetime,
            help='By default, all emails will be considered, regardless of the time it was sent',
            format='MM/DD/YYYY',
        )

        if len(datetimes_selected) == 1:
            min_datetime = datetimes_selected[0]
            max_datetime = datetime(year=3005, month=1, day=1)
        else:
            min_datetime, max_datetime = datetimes_selected

        # convert ``date``s to ``datetime``s
        min_datetime = datetime.combine(date=min_datetime, time=datetime.min.time())
        max_datetime = datetime.combine(date=max_datetime, time=datetime.max.time())

        if st.button(label='Generate newsletter!'):
            st.session_state.generation_mode = True


# Kick off chat with OpenAI API
if st.session_state.generation_mode:
    button_placeholder.empty()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if (
            st.session_state.get('hide_email_summaries') is True
            and message.get('avatar') == EMAIL_SUMMARY_AVATAR
        ):
            continue

        if message['role'] != 'system':
            with st.chat_message(message['role'], avatar=message.get('avatar')):
                st.markdown(message['content'])

    if 'initial_newsletter_draft' not in st.session_state:
        # Read parsed data from Google Spreadsheet, prepare initial prompt
        spreadsheet_str_representation = read_newsletter_tab_of_spreadsheet(
            min_datetime=min_datetime,
            max_datetime=max_datetime,
        )

        with st.chat_message(name='user', avatar=EMAIL_SUMMARY_AVATAR):
            st.markdown(body=spreadsheet_str_representation)

        st.session_state.messages.append(
            {
                'role': 'user',
                'content': spreadsheet_str_representation,
                'avatar': EMAIL_SUMMARY_AVATAR,
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
