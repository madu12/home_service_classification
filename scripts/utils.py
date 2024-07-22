import joblib

def save_model(model, filename):
    """
    Save a machine learning model to a file using joblib.
    
    Args:
        model: The machine learning model to be saved.
        filename (str): The path to the file where the model will be saved.
    """
    try:
        joblib.dump(model, filename)
        print(f"Model saved successfully to {filename}")
    except Exception as e:
        print(f"Error saving model: {e}")

def load_model(filename):
    """
    Load a machine learning model from a file using joblib.
    
    Args:
        filename (str): The path to the file from which the model will be loaded.
    
    Returns:
        The loaded machine learning model.
    """
    try:
        model = joblib.load(filename)
        print(f"Model loaded successfully from {filename}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
