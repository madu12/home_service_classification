# Home Service Classification API

This project provides an API for classifying home service descriptions into categories such as plumbing, electrical, painting, etc. It uses machine learning models with different embedding techniques (TF-IDF, Word2Vec, BERT) to predict the service category based on the provided description.

## Table of Contents

- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Database Initialization](#database-initialization)
- [Training the Model](#training-the-model)
- [Running the API](#running-the-api)
- [API Endpoints](#api-endpoints)
- [Dependencies](#dependencies)

## Setup

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/home_service_classification.git
    cd home_service_classification
    ```

2. **Create and Activate a Virtual Environment:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install Dependencies:**

    ```bash
    pip3 install -r requirements.txt
    ```

4. **Create a `.env` File:**

    Create a `.env` file in the root of your project and add the following content:

    ```env
    DATABASE_DRIVER=ODBC Driver 17 for SQL Server
    DATABASE_SERVER=your_server_name
    DATABASE_NAME=your_database_name
    DATABASE_USERNAME=your_username
    DATABASE_PASSWORD=your_password
    GEMINI_API_KEY=your_gemini_api_key
    ```

5. **(Optional) Deactivate and Remove the Virtual Environment:**

    If you need to deactivate and remove the virtual environment for any reason:

    ```bash
    deactivate
    rm -rf venv
    ```

## Environment Variables

The application uses environment variables for configuration. These variables should be defined in a `.env` file in the root directory of the project.

- `DATABASE_DRIVER` - ODBC driver for the database connection.
- `DATABASE_SERVER` - Database server name.
- `DATABASE_NAME` - Database name.
- `DATABASE_USERNAME` - Database username.
- `DATABASE_PASSWORD` - Database password.
- `GEMINI_API_KEY` - API key for Google Gemini

## Database Initialization

1. **Create the `categories` Table:**

    Execute the following SQL query in your MS SQL database:

    ```sql
    CREATE TABLE categories (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL UNIQUE
    );
    ```

2. **Create the `service_requests` Table:**

    Execute the following SQL query in your MS SQL database:

    ```sql
    CREATE TABLE service_requests (
        id INT PRIMARY KEY IDENTITY(1,1),
        service_description NVARCHAR(MAX) NOT NULL,
        predicted_category_id INT NOT NULL,
        user_confirmed_category_id INT NULL,
        created_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        is_feedback BIT DEFAULT 0,
        CONSTRAINT FK_predicted_category FOREIGN KEY (predicted_category_id) REFERENCES categories(id),
        CONSTRAINT FK_user_confirmed_category FOREIGN KEY (user_confirmed_category_id) REFERENCES categories(id)
    );

    ```

3. **Initialize the Database:**

    ```bash
    export PYTHONPATH=$(pwd)
    python scripts/init_db.py
    ```

## Training the Model

1. **Prepare Your Data:**

    Ensure you have a CSV file named `raw_data.csv` in the `data` directory with the following format:

    ```csv
    service_type,service_description
    plumbing,Repair leaking faucet in bathroom sink
    electrical,Install new ceiling fan in living room
    painting,Paint kitchen cabinets white
    ```

2. **Run the Training Script:**

    ```bash
    export PYTHONPATH=$(pwd)
    python scripts/train_model.py
    ```

## Running the API

1. **Ensure Environment Variables are Loaded:**

    Ensure the `.env` file is present in the root directory.

2. **Run the API:**

    ```bash
    uvicorn api:app --reload
    ```

## API Endpoints

### Test Endpoint

- **URL:** `/`
- **Method:** `GET`
- **Response:**

    ```json
    {
        "message": "Home Service Classification API is running"
    }
    ```

### Predict Category

- **URL:** `/predict`
- **Method:** `POST`
- **Request Body:**

    ```json
    {
        "service_description": "I need someone to fix my leaking pipe and sink this Monday."
    }
    ```

- **Response:**

    ```json
    {
        "predicted_category": "plumbing"
    }
    ```

### Store Feedback

- **URL:** `/feedback`
- **Method:** `POST`
- **Request Body:**

    ```json
    {
        "service_description": "I need someone to fix my leaking pipe and sink this Monday.",
        "predicted_category": "plumbing",
        "correct_category": "plumbing"
    }
    ```

- **Response:**

    ```json
    {
        "message": "Feedback stored successfully"
    }
    ```

## Dependencies

- `python-dotenv`
- `pandas`
- `numpy`
- `nltk`
- `scikit-learn`
- `gensim`
- `transformers`
- `torch`
- `joblib`
- `fastapi`
- `uvicorn`
- `pyodbc`
- `sqlalchemy`
- `scipyscipy==1.11.4`
- `google`
