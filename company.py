import json
import subprocess
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from models import Analysis,CompanyResearch


template = PromptTemplate.from_template("""
Provide a comprehensive report  about '{company_name}' . Include a overview, their mission, values, financial_health, market_penetration, competitors, challenges it faces and opportunities it could embrace

{format_instructions}

Reply only with the JSON document that follows the provided schema. Do not add preamble or commentary.
""")


output_parser = JsonOutputParser(pydantic_object=CompanyResearch)
formatted_template = template.partial(format_instructions=output_parser.get_format_instructions())

def get_company_prompt():
    # read 02_analysis_result.json as Analysis
    with open('inputs/02_analysis_result.json', 'r') as file:
        data = json.load(file)
        analysis_result = Analysis(**data)

    # write the prompt to a file called prompts/prompt_01.txt
    with open('prompts/company.txt', 'w') as file:
        file.write(formatted_template.format(company_name=analysis_result.company_name))


def save_company_data():
    # Read the content of the clipboard
    clipboard_content = subprocess.check_output(['pbpaste']).decode('utf-8')
    # write the content to a file called company_data.json
    data = json.loads(clipboard_content)
    with open('inputs/07_company_data.json', 'w') as file:
        json.dump(data, file, indent=4)
