# -*- coding: utf-8 -*-
"""Prompt polling - OpenAI edition.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HG3b__vG43-2RW5rTl_6-6ewdBqCRSWP

## install strict libs to prevent proxy error
"""

!pip install openai==1.55.3 httpx==0.27.2 --force-reinstall --quiet

"""## define polling functions

Define functions to submit a prompt and save the result to a csv result file, and return a df ready to use.  
"""

import os
import sys
import re
import logging
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import openai
from google.colab import userdata

# Configure your OpenAI API key here
openai.api_key = userdata.get('OPENAI_API_KEY')

# Logging configuration
logging.basicConfig(filename="app.log", level=logging.DEBUG, format="%(asctime)s [%(levelname)s] - %(message)s")

def slugify(text, max_length=100):
    return re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-')[:max_length]

def generate_filename(prompt):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-4]
    return f"{timestamp}_{slugify(prompt)}.csv"[:150]

def fetch_response(payload, request_id):
    try:
        response = openai.chat.completions.create(model=payload["model"], messages=payload["messages"])
        return request_id, response.choices[0].message.content
    except Exception as e:
        logging.error(f"Request {request_id} failed: {str(e)}")
        return request_id, f"Error: {str(e)}"

def fetch_responses_to_dataframe(prompt, num_requests, fetch_response, payload):
    os.makedirs("results", exist_ok=True)
    output_file = os.path.join("results", generate_filename(prompt))
    print(f"Responses will be saved to: {output_file}")

    responses = []
    with ThreadPoolExecutor(max_workers=min(num_requests, 10)) as executor:
        futures = [executor.submit(fetch_response, payload, i) for i in range(1, num_requests + 1)]
        for completed, future in enumerate(as_completed(futures), 1):
            responses.append(future.result())
            sys.stdout.write(f"\rFetched {completed}/{num_requests} responses...")
            sys.stdout.flush()

    df = pd.DataFrame(responses, columns=["Response Number", "Response"])
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"\nFinished! Responses saved to {output_file}")
    return df

# Example usage
prompt = "Tell me a fun fact about space."
num_requests = 5
payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}

responses_df = fetch_responses_to_dataframe(prompt, num_requests, fetch_response, payload)
print(responses_df)

"""Even more compact function that just returns the freqeuncy ratio of each response"""

def get_ratios_for_poll(prompt, num_requests):
  payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}
  responses_df = fetch_responses_to_dataframe(prompt, num_requests, fetch_response, payload)
  return responses_df.Response.str.lower().str.replace('.', '').value_counts(normalize=True).reset_index()



prompt = "say at random: man or woman ?"
num_requests = 10
get_ratios_for_poll(prompt, num_requests)

"""## Make some short tests

We poll up to 100 times on simple yes/no questions to analyze the response ratios.
"""

prompt = "say at random: woman or man ?"
num_requests = 100
get_ratios_for_poll(prompt, num_requests)

prompt = "say at random: man or woman or unicorn ?"
num_requests = 100
get_ratios_for_poll(prompt, num_requests)

prompt = "Are the french handsome? Only anser yes or no."
num_requests = 100
get_ratios_for_poll(prompt, num_requests)

prompt = "1+1+1+1+1+1+1+1+1+1+1+1+1 = __ ?"
num_requests = 50
get_ratios_for_poll(prompt, num_requests)

"""## Make longuer tests

Ask for more extensive content, like fun facts, tips, anecdotes.  
"""

prompt = "what is the most expensive dish in the world?"
num_requests = 100
get_ratios_for_poll(prompt, num_requests)

prompt = "What is the key to a successful life ?"
num_requests = 5
get_ratios_for_poll(prompt, num_requests)

prompt = "C'est quelle ville qui fait la meilleure andouillette?"
num_requests = 5
get_ratios_for_poll(prompt, num_requests)

prompt = "Quel est le secret d'un bon couscous?"
num_requests = 5
get_ratios_for_poll(prompt, num_requests)