import streamlit as st
import getpass
import json
import sys
import time
from pathlib import Path

import magic
import pandas as pd
import requests
from devtools import pprint
from tqdm import tqdm
from datetime import datetime


def global_search(
    index_name: str | list[str], query: str, community_level: int
) -> requests.Response:
    """Run a global query over the knowledge graph(s) associated with one or more indexes"""
    url = endpoint + "/query/global"
    # optional parameter: community level to query the graph at (default for global query = 1)
    request = {
        "index_name": index_name,
        "query": query,
        "community_level": community_level,
    }
    return requests.post(url, json=request, headers=headers)


def local_search(
    index_name: str | list[str], query: str, community_level: int
) -> requests.Response:
    """Run a local query over the knowledge graph(s) associated with one or more indexes"""
    url = endpoint + "/query/local"
    # optional parameter: community level to query the graph at (default for local query = 2)
    request = {
        "index_name": index_name,
        "query": query,
        "community_level": community_level,
    }
    return requests.post(url, json=request, headers=headers)


def parse_query_response(
    response: requests.Response, return_context_data: bool = False
) -> requests.Response | dict[list[dict]]:
    """
    Prints response['result'] value and optionally
    returns associated context data.
    """
    if response.ok:
        # print(json.loads(response.text)["result"])
        return json.loads(response.text)["result"]
    else:
        print(response.reason)
        print(response.content)
        return response


# update this with APIM subscription key
headers = {"Ocp-Apim-Subscription-Key": "XXXXXXXXX"}

index_name = "historydataindexv6"
endpoint = "https://apim-ihio43idbghmk.azure-api.us"


# Streamlit UI
st.title("AFRL History ChatBot: GraphRAG")

# Dropdown choices. If you have multiple indexes, add all the indexes here
indexes = ["historydataindexv6"]
selected_index = st.selectbox("Select a Index:", indexes)

query_types = ["local", "global"]
selected_query = st.selectbox("Select Query Type:", query_types)


community_level = ["1", "2", "3"]
selected_level = st.selectbox("Select a community level:", community_level)


# User input fields
user_question = st.text_input("Enter your question:", key="user_qn")

# Submit button
if st.button("Submit"):
    tempval = 0.5  # Fixed temperature value
    if selected_query == "local":
        local_response = local_search(
            index_name=selected_index,
            query=user_question,
            community_level=selected_level,
        )
        # print the result and save context data in a variable
        response_data = parse_query_response(local_response, return_context_data=True)
    else:
        global_response = global_search(
            index_name=selected_index,
            query=user_question,
            community_level=selected_level,
        )
        # print the result and save context data in a variable
        response_data = parse_query_response(global_response, return_context_data=True)

    st.write(f"**Answer:**\n\n{response_data}")
