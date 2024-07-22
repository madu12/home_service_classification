import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scripts.save_load import load_model
from scripts.data_preprocessing import preprocess_text
from scripts.database_queries import store_service_request, get_category_id
from scripts.train_model import get_average_word2vec

def predict_with_embedding(description):
    # Load models and dimensions
    final_word2vec_model = load_model('models/final_word2vec_model.pkl')
    tfidf_vectorizer = load_model('models/tfidf_vectorizer.pkl')
    final_classifier = load_model('models/final_classifier.pkl')
    
    input_vector = get_average_word2vec(description.lower().split(), final_word2vec_model).reshape(1, -1)
    input_tfidf = tfidf_vectorizer.transform([description]).toarray()
    combined_input_vector = np.hstack([input_vector, input_tfidf])

    probability_estimates = final_classifier.predict_proba(combined_input_vector)
    confidence = max(probability_estimates[0])
    predicted_category = final_classifier.predict(combined_input_vector)[0]
    
    if not predicted_category:
        return None, None
    return predicted_category, confidence

def similarity_based_prediction(description):
    description_processed = preprocess_text(description)
    vectorized_descriptions = np.load('models/vectorized_descriptions_combined.npy')
    descriptions_df = pd.read_csv('models/descriptions_combined.csv')

    # Load models and dimensions
    final_word2vec_model = load_model('models/final_word2vec_model.pkl')
    tfidf_vectorizer = load_model('models/tfidf_vectorizer.pkl')
    combined_feature_dims = np.load('models/combined_feature_dims.npy')

    word2vec_dim, tfidf_dim = combined_feature_dims

    # Get Word2Vec features
    words = description_processed.split()
    description_vectorized_w2v = np.mean([final_word2vec_model.wv[word] for word in words if word in final_word2vec_model.wv], axis=0).reshape(1, -1)
    if np.isnan(description_vectorized_w2v).any():
        description_vectorized_w2v = np.zeros((1, word2vec_dim))

    # Get TF-IDF features
    description_vectorized_tfidf = tfidf_vectorizer.transform([description_processed]).toarray()

    # Combine features
    description_vectorized = np.hstack([description_vectorized_w2v, description_vectorized_tfidf])
    print(f"Vectorized description shape: {description_vectorized.shape}")

    similarities = cosine_similarity(description_vectorized, vectorized_descriptions)
    most_similar_index = np.argmax(similarities)
    most_similar_description = descriptions_df.iloc[most_similar_index]

    return most_similar_description['category'], similarities[0, most_similar_index]

def predict_category(description):
    predicted_category, confidence = predict_with_embedding(description)
    
    if not predicted_category:
        predicted_category, confidence = similarity_based_prediction(description)

    return predicted_category, confidence

def handle_user_input(service_description):
    predicted_category, confidence = predict_category(service_description)
    category_id = get_category_id(predicted_category)
    store_service_request(service_description, category_id, is_feedback=False)

    return predicted_category, confidence

def confirm_category(service_description, category_name):
    category_id = get_category_id(category_name)
    store_service_request(service_description, category_id, user_confirmed_category_id=category_id, is_feedback=True)

def correct_category(service_description, predicted_category_name, correct_category_name):
    predicted_category_id = get_category_id(predicted_category_name)
    correct_category_id = get_category_id(correct_category_name)
    store_service_request(service_description, predicted_category_id, user_confirmed_category_id=correct_category_id, is_feedback=True)
