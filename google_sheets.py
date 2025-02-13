import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def append_job_application():
    try:
        # Define the scope
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # Load credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name("personalproject-450010-5bba86ae999f.json", scope)

        # Authenticate client
        client = gspread.authorize(creds)

        # Open the Google Sheet
        spreadsheet = client.open("Job Hunt 2025")
        worksheet = spreadsheet.worksheet("Sheet1")

        # Get application data
        # Read analysis result
        with open('inputs/02_analysis_result.json', 'r') as f:
            analysis = json.load(f)
            company_name = analysis['company_name']
            role = analysis['job_title']

        # Read URL
        with open('inputs/00_url.txt', 'r') as f:
            url = f.read().strip()

        # Get current date
        current_date = datetime.now()
        # Format as MM/DD/YYYY
        month = str(current_date.month).zfill(2)
        day = str(current_date.day).zfill(2)
        year = str(current_date.year)
        date_str = f"{month}/{day}/{year}"

        # Prepare row data
        new_row = [date_str, company_name, role, url]

        # Append the row to the sheet using RAW input option to prevent formula interpretation
        worksheet.append_row(new_row, value_input_option='USER_ENTERED')
        
        logger.info(f"Successfully added application for {role} at {company_name}")
        return True

    except Exception as e:
        logger.error(f"Error appending job application: {str(e)}")
        return False 