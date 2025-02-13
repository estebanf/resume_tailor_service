import re
from typing import Optional

def extract_job_id(url: str) -> Optional[str]:
    """
    Extract job ID from LinkedIn URL and return formatted URL.
    Example:
    Input: https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4137487466&discover=recommended
    Output: https://www.linkedin.com/jobs/view/4137487466
    """
    try:
        # Try to find the job ID using regex
        match = re.search(r'currentJobId=(\d+)', url)
        if match:
            job_id = match.group(1)
            return f"https://www.linkedin.com/jobs/view/{job_id}"
        return None
    except Exception as e:
        print(f"Error extracting job ID: {str(e)}")
        return None 