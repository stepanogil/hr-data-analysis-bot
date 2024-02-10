import streamlit as st
import random
from backend import chat, new_thread, create_filtered_csv_and_pass_to_api
#from streamlit_chat import message
from st_chat_message import message
from io import BytesIO
import base64
from icecream import ic

# Streamlit app
#st.image("jg2.png", width=100)
st.markdown("")
st.markdown("")
st.markdown("")
st.header("Hi! I'm your HR Data Analyst.")
st.markdown("Click 'New Thread' to start your session.")


# Initialize session state variables if they don't exist
if "past" not in st.session_state:
    st.session_state["past"] = []
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "input_message_key" not in st.session_state:
    st.session_state["input_message_key"] = str(random.random())
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = None

chat_container = st.container()
user_input = st.text_input("Type your message and press Enter to send.", key=st.session_state["input_message_key"])

if st.button("Send"):
    if st.session_state["thread_id"] is not None:
        # Pass the file_id from session_state to the chat function        
        response = chat(user_input, st.session_state["thread_id"])

        # Check if response is a tuple (image and text)
        if isinstance(response, tuple):
            binary_img_file, response_text = response
            st.session_state["past"].append(user_input)
            # Convert binary image to a data URI
            img_data_uri = base64.b64encode(binary_img_file).decode('utf-8')            
            img_markdown = f"![image](data:image/jpeg;base64,{img_data_uri})"
            
            # Append image tag and text response to the chat history
            st.session_state["generated"].append(img_markdown)
            st.session_state["generated"].append(response_text)
            
            # Display text only response.
        else:
            st.session_state["past"].append(user_input)
            st.session_state["generated"].append(response)

        st.session_state["input_message_key"] = str(random.random())
        st.experimental_rerun()
    else:
        st.error("Please click 'New Session' to start your session.")

if st.session_state["generated"]:
    with chat_container:
        for i in range(len(st.session_state["generated"])):
            if i < len(st.session_state["past"]):
                message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
            message(st.session_state["generated"][i], key=str(i))

# New Thread
if st.sidebar.button('New Session'):
    st.session_state["thread_id"] = new_thread()    
    # print(st.session_state["thread_id"])
    st.success(f"Session started. Select the data you want to analyze using the options on the left.")

st.sidebar.title("Employee Overtime Data")
# dropdown
location = st.sidebar.selectbox("Location:", ["Factory A", "Factory B", "Factory C", "All Locations"])
period = st.sidebar.selectbox("Period Covered:", ["January 2014", "February 2014", "March 2014", "April 2014", "May 2014", "June 2014", "July 2014", "August 2014", "September 2014", "October 2014", "November 2014", "December 2014", "All Periods"])

if st.sidebar.button('Select'):
    create_filtered_csv_and_pass_to_api(st.session_state["thread_id"], period, location)    
    st.success(f"Overtime data for {location} location for {period} period has been loaded.\n\nWhat would you like to know or do next with this data?")    
    