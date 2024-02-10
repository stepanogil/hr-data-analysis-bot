import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from icecream import ic


load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

def chat(user_message, thread_id):
    
    # thread id    
    if thread_id is None:
        print(thread_id)
        raise ValueError("No thread ID. Please create a new thread before chatting.")
    
    # set assistant    
    # assistant_id = os.getenv('ASSISTANT_ID')    
    assistant_id = "asst_3aEPvVX4OriP2fYl7Evn4t7i"    
    
    # create thread
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_message
    )

    # Create the run
    run = client.beta.threads.runs.create(  
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    while True:
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )

        if run.status in ['completed', 'failed']:
            res = client.beta.threads.messages.list(thread_id=thread_id)

            # Initialize variables to store the extracted information
            extracted_text = None
            file_id = None

            # Check if content is from code interpreter (image + text)
            if len(res.data[0].content) > 1 and res.data[0].content[0].type == 'image_file' and res.data[0].content[1].type == 'text':
                # Extract image file id and LLM text response
                file_id = res.data[0].content[0].image_file.file_id
                extracted_text = res.data[0].content[1].text.value

            # If content is text only (from function call or LLM didn't use a tool)
            elif len(res.data[0].content) == 1 and res.data[0].content[0].type == 'text':
                # Extract LLM text response
                extracted_text = res.data[0].content[0].text.value

            # Return based on what was extracted
            if file_id and extracted_text:
                print(file_id)
                binary_img_file = client.files.content(file_id).content             
                return (binary_img_file, 
                        extracted_text)
                
            elif extracted_text:
                return extracted_text            
        
        else:
            continue

def new_thread():
    thread = client.beta.threads.create()
    return thread.id


def create_filtered_csv_and_pass_to_api(thread_id, period, location):        
    # load csv as df
    df = pd.read_csv('final_data.csv')
    
    # Initialize filter conditions to True
    location_condition = pd.Series([True] * len(df))
    period_condition = pd.Series([True] * len(df))

    # Assume 'n' will be 1000 for specific location and period
    n = 1000

    # Apply location filter if specific location is provided
    if location != 'All Locations':
        location_condition = df['location'] == location
    else:
        # If 'All Locations' is selected, set 'n' to 3000
        n = 3000

    # Apply period filter if specific period is provided
    if period != 'All Periods':
        period_condition = df['month-year'] == period
    else:
        # If 'All Periods' is selected, set 'n' to 3000
        n = 3000

    # Combine filters and apply
    filtered_df = df[location_condition & period_condition]

    # If both 'All Locations' and 'All Periods' are selected, ensure 'n' is 3000
    if location == 'All Locations' and period == 'All Periods':
        n = 3000

    # Sample 'n' records
    filtered_df = filtered_df.sample(n=min(n, len(filtered_df)), random_state=1)
        
    filtered_df.to_csv('data_for_analysis.csv', index=False)

    file = client.files.create(
        file=open('data_for_analysis.csv', "rb"),
        purpose="assistants"
        )
    
    client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=f"This is the overtime data of employees from {location} for period {period}. All amounts are in Php", file_ids=[file.id]
        )
    








    