import os
from google import genai


client = genai.Client(api_key='GEMINI_API_KEY')
dummy_contract = (
        "This Agreement is between Vendor X and Company Y. Vendor X can change pricing "
        "at any time without giving any prior notice to Company Y. All disputes will be "
        "settled in Vendor X's hometown court only."
        )
response = client.models.generate_content(model = "gemini-2.5-flash",contents = dummy_contract)
print(response.text)