import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

def build_model():
    """
    Builds and saves the TF-IDF vectorizer and matrix, which are memory-efficient.
    """
    print("Starting model building...")
    
    try:
        df = pd.read_csv('data/preprocessed_movies.csv')
        print("Preprocessed data loaded successfully.")

        # Initialize the TF-IDF Vectorizer
        tfidf = TfidfVectorizer(stop_words='english')
        
        df['overview'] = df['overview'].fillna('')
        
        # Create the TF-IDF matrix
        tfidf_matrix = tfidf.fit_transform(df['overview'])
        
        print("TF-IDF matrix created successfully.")
        print(f"Shape of TF-IDF matrix: {tfidf_matrix.shape}")

        # Ensure the model directory exists
        if not os.path.exists('model'):
            os.makedirs('model')
            
        # Save both the matrix and the vectorizer
        model_components = {
            'tfidf_matrix': tfidf_matrix,
            'tfidf_vectorizer': tfidf
        }
        
        with open('model/tfidf_model.pkl', 'wb') as f:
            pickle.dump(model_components, f)
            
        print("Model building complete. TF-IDF components saved to 'model/tfidf_model.pkl'")

    except FileNotFoundError:
        print("Error: 'data/preprocessed_movies.csv' not found. Run 'data_preprocessing.py' first.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    build_model()