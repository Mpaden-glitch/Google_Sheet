import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth
import pandas as pd
import numpy as np
import json

def get_budget_data(scope, sheetId, range):
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", scope)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", scope
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=sheetId, range=range)
        .execute()
    )
  
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return

  
    columns = []
    budget = []
    for row in values:
      columns += [row[0]]
      budget += [row[2]]
    results = dict(map(lambda i,j : (i,j) , columns,budget))
    return results
  except HttpError as err:
    print(err)

def get_spending_data(scope, sheetId, range):
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", scope)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", scope
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=sheetId, range=range)
        .execute()
    )
  
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return

  
    columns = []
    spending = []
    i = 0
    for row in values:
      if i == 0:
        i += 1
        columns += row
      else:
        spending += row
    results = dict(map(lambda i,j : (i,j) , columns,spending))
    return results
  except HttpError as err:
    print(err)

def convert_array(arr):
  conv_arr = np.array(list(arr), dtype=str)
  arr_str = np.char.strip(conv_arr,  chars ='$')
  output_arr = arr_str.astype(np.float64)
  return output_arr

def update_values(scope,spreadsheet_id, range_name, value_input_option, _values):
  """
  Creates the batch_update the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", scope)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", scope
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  # pylint: disable=maybe-no-member
  try:
    service = build("sheets", "v4", credentials=creds)
    body = {"values": _values}
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body,
        )
        .execute()
    )
    print(f"{result.get('updatedCells')} cells updated.")
    return result
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def main():
  # If modifying these scopes, delete the file token.json.
  SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# The ID and range of a sample spreadsheet.
  budget_id = "1qGAI9dOSqq7PE6VlqvSfpPyOEh9x0eGk2bhr_vmu73A"
  budget_range = "Current Budget!B28:D52"

  budget = get_budget_data(SCOPES, budget_id, budget_range)
  df_budget = pd.DataFrame(budget,index=['i',])

  spending_id = "1qGAI9dOSqq7PE6VlqvSfpPyOEh9x0eGk2bhr_vmu73A"
  spending_range = "Current Month!A1:Y2"

  spending = get_spending_data(SCOPES, spending_id, spending_range)
  df_spending = pd.DataFrame(spending,index=['i',])

  frow_budget = df_budget.iloc[[0]].values[0]
  frow_spending = df_spending.iloc[[0]].values[0]

  output_budget = convert_array(frow_budget)
  output_spending = convert_array(frow_spending)

  left_over = output_budget - output_spending

  update_id = "1qGAI9dOSqq7PE6VlqvSfpPyOEh9x0eGk2bhr_vmu73A"
  update_range = "Current Month Leftover!A2:Y2"
  arr_json = json.dumps(left_over.tolist())

  list_arr = arr_json[1:-1].split(",")

 
  update_values(
    SCOPES,
    update_id,
    update_range,
    "USER_ENTERED",
    [list_arr],
)

  


if __name__ == "__main__":
  main()