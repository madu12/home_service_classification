import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
from scripts.data_preprocessing import preprocess_text
from scripts.utils import save_model
from database.repositories import import_csv_to_db, load_initial_data, data_exists_in_db

# Preprocess data
def preprocess_data(df):
    """
    Preprocess the data by applying text preprocessing and tokenization.
    
    Args:
        df (pd.DataFrame): DataFrame containing raw data.
    
    Returns:
        pd.DataFrame: DataFrame with processed text and tokenized descriptions.
    """
    df['processed_description'] = df['service_description'].apply(preprocess_text)
    df['tokenized_descriptions'] = df['processed_description'].apply(lambda x: x.lower().split())
    return df

# Define function to average word vectors for a service description
def get_average_word2vec(tokens, model):
    """
    Calculate the average Word2Vec vector for a list of tokens.
    
    Args:
        tokens (list): List of tokens.
        model (Word2Vec): Trained Word2Vec model.
    
    Returns:
        np.ndarray: Averaged Word2Vec vector.
    """
    vectors = [model.wv[word] for word in tokens if word in model.wv]
    if len(vectors) == 0:
        return np.zeros(model.vector_size)
    else:
        return np.mean(vectors, axis=0)

# Define function for training and evaluating the model with given parameters
def train_and_evaluate_word2vec(df, vector_size, window, min_count):
    """
    Train and evaluate a Word2Vec model and a RandomForest classifier with given parameters.
    
    Args:
        df (pd.DataFrame): DataFrame containing preprocessed data.
        vector_size (int): Size of the Word2Vec vectors.
        window (int): Maximum distance between the current and predicted word within a sentence.
        min_count (int): Ignores all words with total frequency lower than this.
    
    Returns:
        tuple: Trained Word2Vec model, trained classifier, and evaluation score.
    """
    temp_model = Word2Vec(sentences=df['tokenized_descriptions'], vector_size=vector_size, window=window, min_count=min_count, workers=4)
    df['vector'] = df['tokenized_descriptions'].apply(lambda x: get_average_word2vec(x, temp_model))
    X = np.vstack(df['vector'])
    y = df['category']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the classifier
    temp_classifier = RandomForestClassifier()
    temp_classifier.fit(X_train, y_train)
    
    # Evaluate the classifier
    temp_score = temp_classifier.score(X_test, y_test)
    
    return temp_model, temp_classifier, temp_score

# Grid search function for the best Word2Vec parameters
def grid_search_word2vec(data):
    """
    Perform grid search to find the best parameters for the Word2Vec model.
    
    Args:
        data (pd.DataFrame): DataFrame containing preprocessed data.
    
    Returns:
        tuple: Best Word2Vec model, best classifier, best parameters, and best score.
    """
    best_model = None
    best_classifier = None
    best_params = {}
    best_score = 0

    # Grid search for the best Word2Vec parameters
    for vector_size in [50, 100, 150, 200]:
        for window in [3, 5, 7, 10]:
            for min_count in [1, 2, 3, 5]:
                temp_model, temp_classifier, temp_score = train_and_evaluate_word2vec(data, vector_size, window, min_count)
                if temp_score > best_score:
                    best_score = temp_score
                    best_model = temp_model
                    best_classifier = temp_classifier
                    best_params = {
                        'vector_size': vector_size,
                        'window': window,
                        'min_count': min_count
                    }
    return best_model, best_classifier, best_params, best_score

# Main function to import data and train the model
def main():
    data_filepath = 'data/raw_data.csv'  # Path to raw data CSV file

    try:
        # Check if data exists in the database
        if not data_exists_in_db(data_filepath):
            # Import CSV data
            import_csv_to_db(data_filepath)

        # Load initial data
        data = load_initial_data()
        data = preprocess_data(data)

        # Grid search for the best Word2Vec parameters
        best_model, best_classifier, best_params, best_score = grid_search_word2vec(data)

        # Display the best parameters and score
        print(f"Best Parameters: {best_params}")
        print(f"Best Score: {best_score}")

        # Generate the final Word2Vec model with the best parameters
        final_word2vec_model = Word2Vec(sentences=data['tokenized_descriptions'], vector_size=best_params['vector_size'], window=best_params['window'], min_count=best_params['min_count'], workers=4)
        data['vector'] = data['tokenized_descriptions'].apply(lambda x: get_average_word2vec(x, final_word2vec_model))

        # Generate TF-IDF features
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_features = tfidf_vectorizer.fit_transform(data['processed_description'])

        # Combine Word2Vec and TF-IDF features
        word2vec_features = np.vstack(data['vector'])
        combined_features = np.hstack([word2vec_features, tfidf_features.toarray()])

        # Save the vectorized descriptions for similarity-based prediction
        np.save('models/vectorized_descriptions_combined.npy', combined_features)
        data[['service_description', 'category']].to_csv('models/descriptions_combined.csv', index=False)

        # Prepare features and labels
        X = combined_features
        y = data['category']

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the final classifier
        final_classifier = RandomForestClassifier()
        final_classifier.fit(X_train, y_train)

        # Predict on the test set
        y_pred = final_classifier.predict(X_test)

        # Generate the classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        report_df = pd.DataFrame(report).transpose()
        print(report_df)

        # Save the models and feature dimensions
        save_model(final_word2vec_model, 'models/final_word2vec_model.pkl')
        save_model(tfidf_vectorizer, 'models/tfidf_vectorizer.pkl')
        save_model(final_classifier, 'models/final_classifier.pkl')
        np.save('models/combined_feature_dims.npy', np.array([word2vec_features.shape[1], tfidf_features.shape[1]]))

        # input_sentence = "I need someone for clean windows home".lower().split()
        # input_vector = get_average_word2vec(input_sentence, final_word2vec_model).reshape(1, -1)
        # input_tfidf = tfidf_vectorizer.transform(["I need someone for clean windows home"]).toarray()
        # combined_input_vector = np.hstack([input_vector, input_tfidf])

        # probability_estimates = final_classifier.predict_proba(combined_input_vector)
        # confidence = max(probability_estimates[0])
        # predicted_category = final_classifier.predict(combined_input_vector)[0]

        # print(f"Predicted Category: {predicted_category}")
        # print(f"Confidence: {confidence}")
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
