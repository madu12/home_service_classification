# Home Service Classification API

This project provides an API for classifying home service descriptions into categories such as plumbing, electrical, painting, etc. It uses machine learning models with different embedding techniques (TF-IDF, Word2Vec, BERT) to predict the service category based on the provided description.

## Installation and Setup

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Clone the Repository

```bash
git clone https://github.com/madu12/home_service_classification.git
cd home_service_classification
```

### Create and Activate a Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

### Install the Required Dependencies
```bash
pip install -r requirements.txt
```

### Set Up Environment Variables
Create a .env file in the root directory and add the following variables:
```
DATABASE_DRIVER=ODBC Driver 18 for SQL Server
DATABASE_SERVER=your_server_name
DATABASE_NAME=your_database_name
DATABASE_USERNAME=your_username
DATABASE_PASSWORD=your_password
GEMINI_API_KEY=your_gemini_api_key
```

### Database Setup
Ensure your database is set up and running. Use the following SQL queries to create the necessary tables:

```sql
-- Create 'categories' table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='categories' AND xtype='U')
BEGIN
    CREATE TABLE categories (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL UNIQUE
    );
    CREATE INDEX idx_category_name ON categories(name);
END;

-- Create 'service_requests' table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='service_requests' AND xtype='U')
BEGIN
    CREATE TABLE service_requests (
        id INT PRIMARY KEY IDENTITY(1,1),
        service_description NVARCHAR(MAX) NOT NULL,
        predicted_category_id INT NULL,
        user_confirmed_category_id INT NULL,
        created_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        is_feedback BIT DEFAULT 0,
        CONSTRAINT FK_predicted_category FOREIGN KEY (predicted_category_id) REFERENCES categories(id),
        CONSTRAINT FK_user_confirmed_category FOREIGN KEY (user_confirmed_category_id) REFERENCES categories(id)
    );
END;
```


## Training the Model

### Prepare Your Data

Ensure you have a CSV file named raw_data.csv in the data directory with the following format:
```csv
service_type,service_description
plumbing,Repair leaking faucet in bathroom sink
electrical,Install new ceiling fan in living room
painting,Paint kitchen cabinets white
```
### Run the Training Script
```bash
export PYTHONPATH=$(pwd)
python scripts/train_model.py
```

## Running the API

### Run the Application
```bash
python app.py
```

## API Endpoints

### Test Endpoint
- URL: /
- Method: GET
- Response:
    ```json
    {
        "message": "Home Service Classification API is running"
    }
    ```

### Predict Category
- URL: /predict
- Method: POST
- Request Body:
    ```json
    {
        "service_description": "I need someone to fix my leaking pipe and sink this Monday."
    }
    ```
- Response:
    ```json
    {
        "category": "painting",
        "confidence": 0.69,
        "suggested_by_gemini": "painting"
    }
    ```

### Confirmed Category
- URL: /confirm_category
- Method: POST
- Request Body:
    ```json
    {
        "service_description": "I need someone to fix my leaking pipe and sink this Monday.",
        "confirmed_category": "plumbing"
    }
    ```
- Response:
    ```json
    {
        "message": "Category confirmed successfully."
    }
    ```
## Troubleshooting

### Common Issues
1. Environment Variables: Ensure all required environment variables are set in the .env file.

2. Database Connection: Verify your database connection string and credentials.