from bs4 import BeautifulSoup
import html2text
import re
from typing import Optional

def get_text_preview(text: str, preview_length: int = 100) -> str:
    """Returns a preview of the text showing first and last N characters."""
    if not text:
        return ""
    if len(text) <= preview_length * 2:
        return text
        
    start = text[:preview_length]
    end = text[-preview_length:]
    return f"{start}\n[...]\n{end}"

async def process_job_html(html: str) -> Optional[str]:
    """
    Process LinkedIn job post HTML and convert it to readable markdown.
    Strips out everything from "Insights about this job's applicants" and below.
    """
    try:
        # Configure html2text
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        converter.ignore_images = True
        converter.ignore_emphasis = False
        converter.body_width = 0
        converter.ul_item_mark = '-'
        
        # Convert HTML to markdown
        markdown_text = converter.handle(html)
        
        # Split into lines and process
        lines = markdown_text.splitlines()
        
        # Find the insights line
        insights_index = -1
        for i, line in enumerate(lines):
            if "Insights about this job’s applicants" in line:
                insights_index = i
                break
        
        # Keep only content before insights
        if insights_index != -1:
            lines = lines[:insights_index]
        
        # Remove empty lines
        lines = [line for line in lines if line.strip()]
        
        # Join back into markdown
        cleaned_text = '\n'.join(lines)
        
        # Print the whole processed content
        # if cleaned_text:
            # print("\n=== Processed Content ===")
            # print(cleaned_text)
            # print("=======================\n")
        
        return cleaned_text
            
    except Exception as e:
        print(f"Error processing HTML: {str(e)}")
        return None 