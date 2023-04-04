#--------------------------------------------------------#
# Imports
#--------------------------------------------------------#
import streamlit as st
import tiktoken
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

etherscan_key = os.environ['ETHERSCAN_KEY']
polygonscan_key = os.environ['POLYGONSCAN_KEY']
optiscan_key = os.environ['OPTISCAN_KEY']
arbiscan_key = os.environ['ARBISCAN_KEY']
openai.api_key = os.environ['OPENAI_KEY']

def num_tokens_from_string(string: str) -> int:
  # Returns the number of tokens in a text string.
  encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
  num_tokens = len(encoding.encode(string))
  return num_tokens


st.cache_data
def get_explanation(contract, chain_l2):
  if chain_l2 == 'Ethereum':
    response = requests.post(
      'https://api.etherscan.io/api?module=contract&action=getsourcecode&address='
      + contract + '&apikey=' + etherscan_key)
  elif chain_l2 == 'Polygon':
    response = requests.post(
      'https://api.polygonscan.com/api?module=contract&action=getsourcecode&address='
      + contract + '&apikey=' + polygonscan_key)
  elif chain_l2 == 'Optimism':
    response = requests.post('https://api-optimistic.etherscan.io/api?module=contract&action=getsourcecode&address='+contract+'&apikey='+optiscan_key)
  elif chain_l2 == 'Arbitrum':
    response = requests.post('https://api.arbiscan.io/api?module=contract&action=getsourcecode&address='+contract+'&apikey='+arbiscan_key)

  source_code = response.json()['result'][0]['SourceCode']
  raw_abi = response.json()['result'][0]['ABI']

  if source_code == '':
    return 'Source code not verified OR Contract not found'

  if num_tokens_from_string(source_code) > 3500:
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

    prompt = "; ".join(summaries)

    if prompt == '':
      return 'Sorry I struggled to analyse this contract. Can we try another one please?'

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      temperature=0,
      messages=[{
        "role":
        "system",
        "content":
        "You are a smart contract expert. When I send you a smart contract ABI you will tell me what this contract does. I know you don't have all the information you need, please give me your best guess."
      }, {
        "role": "user",
        "content": prompt
      }])

    return completion.choices[0].message['content']
  else:
    prompt = source_code

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      temperature=0,
      messages=[{
        "role":
        "system",
        "content":
        "You are a smart contract expert. You are a good teacher. When I send you a Solidity smart contract you will give me a concise explanation of the contract. If you don't know what the contract does you truthfully say 'I don't know'."
      }, {
        "role": "user",
        "content": prompt
      }])

    return completion.choices[0].message['content']


#--------------------------------------------------------#
# Main Body
#--------------------------------------------------------#

# Create the title at the top of page
st.title('Contract Wizard 🪄')

# Create a builder label to show off
st.markdown("[By Kofi](https://twitter.com/0xKofi)")

chain_l2 = st.selectbox('Select chain/L2', ('Ethereum', 'Polygon', 'Optimism', 'Arbitrum'))

# Create a text input that users can enter an ENS name or wallet address
st.subheader(
  'Enter the address of the smart contract you want to understand 👇')
'This only works for contracts that are verified'

contract_address = st.text_input(' ',
                                 '0x6B175474E89094C44Da98b954EedeAC495271d0F')

with st.spinner('Analyzing contract...'):
  explanation = get_explanation(contract_address, chain_l2)

# Present the explanation
st.subheader(explanation)
