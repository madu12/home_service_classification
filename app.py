import sys
import os
from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from flasgger import Swagger
from scripts.model_prediction import predict_category, confirm_category
from scripts.generative_ai import generate_category_by_gemini, verify_predicted_category_is_correct_by_gemini

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Default confidence threshold for predictions
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.7))

# Initialize Flask app
app = Flask(__name__)

# Initialize Swagger for API documentation
Swagger(app)

# Pydantic models for request and response validation
class PredictionRequest(BaseModel):
    service_description: str

class PredictionResponse(BaseModel):
    confidence: float
    category: str
    suggested_by_gemini: str
    verification_status_by_gemini: str
    verification_reason_by_gemini: str

class ConfirmationRequest(BaseModel):
    service_description: str
    confirmed_category: str

# Define a root endpoint
@app.route("/", methods=["GET"])
def read_root():
    """
    Root endpoint to check if API is running.
    ---
    responses:
        200:
            description: API is running
            examples:
                application/json: 
                    message: "Home Service Classification API is running"
    """
    return jsonify({"message": "Home Service Classification API is running"})

# Endpoint for predicting the category of a service description
@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict the category of a service description.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            service_description:
              type: string
              example: "Fix a leaking pipe"
          required:
            - service_description
    responses:
        200:
            description: Category prediction response
            schema:
                type: object
                properties:
                    confidence:
                        type: number
                    category:
                        type: string
                    suggested_by_gemini:
                        type: string
                    verification_status_by_gemini:
                        type: string
                    verification_reason_by_gemini:
                        type: string
        422:
            description: Validation Error
        500:
            description: Internal Server Error
    """
    try:
        data = request.json
        # Validate request data
        try:
            request_data = PredictionRequest(**data)
        except ValidationError as e:
            return jsonify(e.errors()), 422

        # Predict category using the trained model
        category, confidence = predict_category(request_data.service_description)
        
        # Generate category using generative AI (Gemini)
        suggested_by_gemini = generate_category_by_gemini(request_data.service_description)

        # Verify if the predicted category is correct using generative AI (Gemini)
        verification_result_by_gemini = verify_predicted_category_is_correct_by_gemini(
            request_data.service_description, category)

        response_data = PredictionResponse(
            confidence=confidence,
            category=category,
            suggested_by_gemini=suggested_by_gemini.lower(),
            verification_status_by_gemini=verification_result_by_gemini['status'],
            verification_reason_by_gemini=verification_result_by_gemini['reason']
        )

        return jsonify(response_data.dict())
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

# Endpoint for confirming a predicted category
@app.route("/confirm_category", methods=["POST"])
def confirm():
    """
    Confirm a predicted category for a service description.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            service_description:
              type: string
              example: "Fix a leaking pipe"
            confirmed_category:
              type: string
              example: "Plumbing"
          required:
            - service_description
            - confirmed_category
    responses:
        200:
            description: Category confirmed successfully
        422:
            description: Validation Error
        500:
            description: Internal Server Error
    """
    try:
        data = request.json
        # Validate request data
        try:
            request_data = ConfirmationRequest(**data)
        except ValidationError as e:
            return jsonify(e.errors()), 422

        confirm_category(request_data.service_description, request_data.confirmed_category)
        return jsonify({"message": "Category confirmed successfully."})
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

# Custom error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Resource not found"}), 404

# Custom error handler for 500 errors
@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
