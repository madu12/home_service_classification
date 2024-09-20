from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from database.models import ServiceRequest, Category
from database.db_session import create_session

def get_category_id(category_name):
    """
    Retrieve the ID of a category by its name, creating it if it doesn't exist.
    
    Args:
        category_name (str): The name of the category.
    
    Returns:
        int: The ID of the category.
    """
    session = create_session()
    try:
        category = session.query(Category).filter_by(name=category_name).first()
        if category:
            return category.id
        else:
            new_category = Category(name=category_name)
            session.add(new_category)
            session.commit()
            return new_category.id
    except SQLAlchemyError as e:
        print(f"Error retrieving or creating category: {e}")
        session.rollback()
        return None
    finally:
        session.close()

def fetch_all_service_requests():
    """
    Fetch all records from the service_requests table, joined with categories.
    
    Returns:
        DataFrame: A DataFrame containing service descriptions and their categories.
    """
    session = create_session()
    query = """
    SELECT 
        sr.service_description, 
        COALESCE(c_user.name, c_pred.name) AS category
    FROM 
        service_requests sr
    LEFT JOIN 
        categories c_pred ON sr.predicted_category_id = c_pred.id
    LEFT JOIN 
        categories c_user ON sr.user_confirmed_category_id = c_user.id
    """
    try:
        data = pd.read_sql(query, session.bind)
        return data
    except SQLAlchemyError as e:
        print(f"Error fetching service requests: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def normalize_data(df):
    """
    Normalize the text data by converting to lowercase and stripping whitespace.
    
    Args:
        df (DataFrame): The DataFrame containing service descriptions and categories.
    
    Returns:
        DataFrame: The normalized DataFrame.
    """
    df['service_description'] = df['service_description'].str.lower().str.strip()
    df['category'] = df['category'].str.lower().str.strip()
    return df

def import_csv_to_db(csv_file):
    """
    Import data from a CSV file into the database, identifying and inserting new rows.
    
    Args:
        csv_file (str): The path to the CSV file.
    """
    session = create_session()
    try:
        csv_data = pd.read_csv(csv_file)
        if 'service_description' not in csv_data.columns or 'category' not in csv_data.columns:
            raise ValueError("CSV file must contain 'service_description' and 'category' columns")
        
        db_data = fetch_all_service_requests()
        
        # Normalize both CSV and DB data
        csv_data = normalize_data(csv_data)
        db_data = normalize_data(db_data)
        
        # Identify new rows
        new_data = csv_data.merge(db_data, on=['service_description', 'category'], how='left', indicator=True)
        new_data = new_data[new_data['_merge'] == 'left_only'].drop(columns=['_merge'])
        
        # Show the missing rows
        if not new_data.empty:
            print("Missing rows to be inserted:")
            print(new_data)
        else:
            print("No new rows to be inserted.")
        
        for _, row in new_data.iterrows():
            category_id = get_category_id(row['category'])
            service_request = ServiceRequest(
                service_description=row['service_description'],
                predicted_category_id=category_id,
                is_feedback=False
            )
            session.add(service_request)
        
        session.commit()
    except Exception as e:
        print(f"Error importing CSV to DB: {e}")
        session.rollback()
    finally:
        session.close()
def load_initial_data():
    """
    Load initial non-feedback data from the service_requests table.
    
    Returns:
        DataFrame: A DataFrame containing initial service descriptions and categories.
    """
    session = create_session()
    query = """
    SELECT sr.service_description, c.name as category
    FROM service_requests sr
    JOIN categories c ON sr.predicted_category_id = c.id
    WHERE sr.is_feedback = 0
    """
    try:
        data = pd.read_sql(query, session.bind)
        return data
    except SQLAlchemyError as e:
        print(f"Error loading initial data: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def get_feedback_data():
    """
    Retrieve feedback data from the service_requests table.
    
    Returns:
        DataFrame: A DataFrame containing service descriptions, predicted categories, and user-confirmed categories.
    """
    session = create_session()
    query = """
    SELECT sr.service_description, 
           c1.name as predicted_category, 
           c2.name as user_confirmed_category
    FROM service_requests sr
    JOIN categories c1 ON sr.predicted_category_id = c1.id
    LEFT JOIN categories c2 ON sr.user_confirmed_category_id = c2.id
    WHERE sr.is_feedback = 1
    """
    try:
        feedback_data = pd.read_sql(query, session.bind)
        return feedback_data
    except SQLAlchemyError as e:
        print(f"Error retrieving feedback data: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def get_existing_categories():
    """
    Retrieve all existing categories from the database.
    
    Returns:
        list: A list of category names.
    """
    session = create_session()
    try:
        result = session.execute(text("SELECT name FROM categories"))
        categories = [row[0] for row in result]
        return categories if categories else []
    except SQLAlchemyError as e:
        print(f"Error retrieving existing categories: {e}")
        return []
    finally:
        session.close()

def store_service_request(service_description, predicted_category_id=None, user_confirmed_category_id=None, is_feedback=False):
    """
    Store a service request in the database.
    
    Args:
        service_description (str): The description of the service.
        predicted_category_id (int): The ID of the predicted category.
        user_confirmed_category_id (int, optional): The ID of the user-confirmed category.
        is_feedback (bool, optional): Flag indicating if the request is feedback.
    """
    session = create_session()
    try:
        service_request = ServiceRequest(
            service_description=service_description,
            predicted_category_id=predicted_category_id,
            user_confirmed_category_id=user_confirmed_category_id,
            is_feedback=is_feedback
        )
        session.add(service_request)
        session.commit()
    except SQLAlchemyError as e:
        print(f"Error storing service request: {e}")
        session.rollback()
    finally:
        session.close()

def data_exists_in_db(csv_file):
    """
    Compare CSV data with existing database data to check if they are identical.
    
    Args:
        csv_file (str): The path to the CSV file.
    
    Returns:
        bool: True if the CSV data matches the database data, False otherwise.
    """
    try:
        csv_data = pd.read_csv(csv_file)
        db_data = fetch_all_service_requests()
        
        # Normalize both CSV and DB data
        csv_data = normalize_data(csv_data)
        db_data = normalize_data(db_data)
        
        # Sort and reset index for comparison
        csv_data = csv_data.sort_values(by=['service_description', 'category']).reset_index(drop=True)
        db_data = db_data.sort_values(by=['service_description', 'category']).reset_index(drop=True)
        
        return csv_data.equals(db_data)
    except Exception as e:
        print(f"Error comparing CSV to DB: {e}")
        return False

def get_category_by_name(category_name):
    """
    Retrieve a category by its name.
    
    Args:
        category_name (str): The name of the category.
    
    Returns:
        Category: The category object if found, else None.
    """
    try:
        session = create_session()
        return session.query(Category).filter_by(name=category_name).first()
    except SQLAlchemyError as e:
        print(f"Error retrieving category by name: {e}")
        return None
    finally:
        session.close()
