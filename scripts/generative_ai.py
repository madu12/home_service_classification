import google.generativeai as genai
from dotenv import load_dotenv
from database.repositories import get_existing_categories
import os

# Load environment variables from .env file
load_dotenv()

# Configure generative AI model with API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def generate_query(prompt):
    """
    Generates a response from the generative AI model based on the given prompt.
    
    Args:
        prompt (str): The input prompt to generate content.
    
    Returns:
        str: The cleaned JSON response from the model.
    """
    try:
        response = model.generate_content([prompt])
        raw_json = response.text
        cleaned_json = raw_json.replace("json", "").replace("```", "").strip()
        return cleaned_json
    except Exception as e:
        print(f"Error generating query: {e}")
        return None

def generate_category(service_description):
    """
    Generates the most appropriate category for a given home service description.
    
    Args:
        service_description (str): The description of the home service.
    
    Returns:
        str: The suggested or matched category name.
    """
    prompt = f"Classify the following home service description: '{service_description}'. Please provide the most appropriate category. Only return the category name."
    suggested_category = generate_query(prompt)

    if not suggested_category:
        print("Failed to generate suggested category.")
        return None

    existing_categories = get_existing_categories()

    if not existing_categories:
        # If no categories exist in the database, return the suggested category
        return suggested_category

    # Check for matching category or synonyms
    synonym_prompt = f"The suggested category is: '{suggested_category}'. The existing categories are:\n"
    synonym_prompt += '\n'.join(existing_categories)
    synonym_prompt += "\n\nPlease check if any synonyms or the same categories from the list above match the suggested category. Return the matching category name if it exists, otherwise return 'None'."

    matching_category = generate_query(synonym_prompt)

    if matching_category and matching_category != 'None':
        return matching_category
    else:
        return suggested_category
