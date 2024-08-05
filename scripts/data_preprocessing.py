import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK data
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

def preprocess_text(text):
    """
    Preprocesses the input text by removing special characters, digits, 
    tokenizing, and lemmatizing the words, and removing stopwords.
    
    Args:
        text (str): The input text to preprocess.
    
    Returns:
        str: The preprocessed text.
    """
    # Initialize the lemmatizer and stop words
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    # Remove special characters and digits using regex
    text = re.sub(r'[^a-zA-Z\s]', '', text, re.I | re.A)
    
    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    
    # Lemmatize tokens and remove stop words
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens if token.lower() not in stop_words]
    
    # Join tokens back into a single string
    return ' '.join(tokens)
