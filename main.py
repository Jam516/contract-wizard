#--------------------------------------------------------#
# Imports
#--------------------------------------------------------#
import streamlit as st
import requests
import os
import openai
import json

#--------------------------------------------------------#
# Page Config
#--------------------------------------------------------#

st.set_page_config(
  page_title="Contract Wizard",
  page_icon="🪄",
  layout="wide",
)

#--------------------------------------------------------#
# Functions
#--------------------------------------------------------#


def get_abi(contract):
  etherscan_key = os.environ['ETHERSCAN_KEY']
  response = requests.post(
    'https://api.etherscan.io/api?module=contract&action=getsourcecode&address='
    + contract + '&apikey=' + etherscan_key)
    
  raw_abi = response.json()['result'][0]['ABI']

  # Check if the API call was successful
  if raw_abi == 'Contract source code not verified':
    return 'source code not verified'
    
  shortened_abi = json.loads(raw_abi)
  summaries = []
  for item in shortened_abi:
    if item["type"] == "function":
      name = item["name"]
      inputs = [f"{i['name']}({i['type']})" for i in item["inputs"]]
      outputs = [f"{o['name']}({o['type']})" for o in item["outputs"]]
      summary = f"function {name}({', '.join(inputs)}) -> ({', '.join(outputs)})"
      summaries.append(summary)
    elif item["type"] == "event":
      name = item["name"]
      inputs = [f"{i['name']}({i['type']})" for i in item["inputs"]]
      summary = f"event {name}({', '.join(inputs)})"
      summaries.append(summary)

  output = "; ".join(summaries)
  return output


st.cache_data
def get_explanation(contract):
  context = get_abi(contract)

  if context == 'source code not verified':
    return 'source code not verified'
    
  openai.api_key = "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"
  prompt = f"""
  You are a smart contract expert. You answer user questions based on the context provided by the user above each question. If you don't know the answer you truthfully say "I don't know".
  
  Context: {context}
  
  Question:
  This is the ABI of an Ethereum smart contract. What does this contract do? I know you don't have all the information you need, please give me your best guess.
  """
  completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            temperature=0.7,
                                            messages=[{
                                              "role": "user",
                                              "content": prompt
                                            }])

  return completion.choices[0].message


#--------------------------------------------------------#
# Main Body
#--------------------------------------------------------#

# Create the title at the top of page
st.title('Contract Wizard 🪄')

# Create a builder label to show off
st.markdown("[By Kofi](https://twitter.com/0xKofi)")

# Create a text input that users can enter an ENS name or wallet address
st.subheader(
  'Enter the address of the smart contract you want to understand 👇')
'This only works for Ethereum contracts that are verified on Etherscan'

contract_address = st.text_input(' ',
                                 '0x6B175474E89094C44Da98b954EedeAC495271d0F')

explanation = get_explanation(contract_address)

if explanation != 'source code not verified':
  # Present the explanation
  st.subheader(explanation['content'])
else:
  st.subheader('Source code not verified OR Contract not found')
