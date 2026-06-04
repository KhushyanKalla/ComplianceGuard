from pypdf import PdfReader
from google import genai
import os

def extract_text_from_pdf(pdf_file):
    # PdfReader accepts file object directly from request.FILES
    reader = PdfReader(pdf_file)
    
    full_text = ""
    
    # Loop through every page and collect all text
    for page in reader.pages:
        full_text += page.extract_text()
    
    return full_text


def analyze_contract_with_ai(contract_text):
    # Read API key from .env file via os.environ
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Guard check — if key missing, return clear error instead of crashing
    if not api_key:
        return "GEMINI_API_KEY not found in environment variables."
    
    client = genai.Client(api_key=api_key)
    
    # System instruction tells Gemini its role and what to do
    system_instruction = (
        "You are an expert corporate legal auditor. "
        "Analyze the following contract text. "
        "Identify potential high-risk clauses and return a clean summary."
        "At the end of your response, write RISK_SCORE: followed by a number between 0 and 100 based on overall contract risk."
    )
    
    # Send contract text to Gemini and get analysis back
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contract_text,
        config={'system_instruction': system_instruction}
    )
    
    return response.text