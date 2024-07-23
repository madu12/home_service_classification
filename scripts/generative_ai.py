import google.generativeai as genai
from dotenv import load_dotenv
from database.repositories import get_existing_categories
import os

# Load environment variables from .env file
load_dotenv()

# Configure generative AI model with API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def generate_query_by_gemini(prompt):
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

def generate_category_by_gemini(service_description):
    """
    Generates the most appropriate category for a given home service description.
    
    Args:
        service_description (str): The description of the home service.
    
    Returns:
        str: The suggested or matched category name.
    """
    prompt = (
        f"Classify the following home service description: '{service_description}'. "
        f"Please provide the most appropriate category. Only return the category name. "
        f"Do not include job date, time, or location data in the classification. "
        f"If the service description contains only date, time, or location data, return 'none'."
    )
    suggested_category = generate_query_by_gemini(prompt)

    if not suggested_category or suggested_category.lower() == 'none':
        print("Failed to generate suggested category.")
        return 'none'

    existing_categories = get_existing_categories()

    if not existing_categories:
        # If no categories exist in the database, return the suggested category
        return suggested_category

    # Check for matching category or synonyms
    synonym_prompt = (
        f"The suggested category is: '{suggested_category}'. The existing categories are:\n"
        f"{'\n'.join(existing_categories)}\n\n"
        "Please check if any synonyms or the same categories from the list above match the suggested category. "
        "Return the matching category name if it exists, otherwise return 'none'."
    )

    matching_category = generate_query_by_gemini(synonym_prompt)

    if matching_category and matching_category.lower() != 'none':
        return matching_category
    else:
        return suggested_category

def verify_predicted_category_is_correct_by_gemini(service_description, predicted_category):
    """
    Verifies if the predicted category matches the service description using the Gemini model.
    
    Args:
        service_description (str): The description of the home service.
        predicted_category (str): The category predicted by the model.
    
    Returns:
        dict: Verification status and reason.
    """
    if not service_description or not predicted_category:
        return {"status": "incorrect", "reason": "Missing service description or predicted category."}
    
    try:
        prompt = (
            f"Given the service description: '{service_description}', "
            f"verify if the category: '{predicted_category}' is correct. "
            f"Respond with 'correct' if it matches, otherwise respond with 'incorrect'."
        )
        
        verification_result = generate_query_by_gemini(prompt)
        
        if verification_result is None:
            return {"status": "incorrect", "reason": "No response from the Gemini model."}
        
        if verification_result == "correct":
            return {"status": "correct", "reason": "The predicted category is verified as correct."}
        else:
            return {"status": "incorrect", "reason": "The predicted category does not match the service description."}
    except Exception as e:
        return {"status": "incorrect", "reason": "Error occurred during category verification."}
