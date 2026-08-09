from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import random
import requests
from sklearn.metrics.pairwise import linear_kernel

app = Flask(__name__)
CORS(app)

# --- Load Data and Model ---
try:
    movies_df = pd.read_csv('data/preprocessed_movies.csv')
    
    # Load the TF-IDF model components
    with open('model/tfidf_model.pkl', 'rb') as f:
        model_components = pickle.load(f)
        tfidf_matrix = model_components['tfidf_matrix']

    indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()
    
    print("Data and TF-IDF model loaded successfully.")

except FileNotFoundError:
    print("Error: Make sure 'preprocessed_movies.csv' and 'tfidf_model.pkl' exist.")
    movies_df, tfidf_matrix, indices = None, None, None

# --- OMDb API Configuration ---
OMDB_API_KEY = 'abc910ee' # IMPORTANT: Replace with your own key
OMDB_API_URL = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}"

def get_movie_details(title, year):
    """Fetches movie poster and details from OMDb API."""
    try:
        params = {'t': title, 'y': str(year)}
        response = requests.get(OMDB_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('Response') == 'True':
            return {
                'poster': data.get('Poster', ''),
                'plot': data.get('Plot', 'N/A'),
                'imdbRating': data.get('imdbRating', 'N/A')
            }
    except requests.exceptions.RequestException:
        pass # Silently fail if API is down or key is invalid
    return {
        'poster': 'https://placehold.co/300x450/2d3748/ffffff?text=Poster+Not+Found',
        'plot': 'Plot details not available.',
        'imdbRating': 'N/A'
    }

def get_recommendations(title):
    """Generates recommendations for a given movie title on-the-fly."""
    if title not in indices:
        return []
        
    idx = indices[title]
    movie_vector = tfidf_matrix[idx]
    
    # Calculate similarity scores (this is the memory-efficient part)
    sim_scores = linear_kernel(movie_vector, tfidf_matrix).flatten()
    sim_scores = list(enumerate(sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    
    movie_indices = [i[0] for i in sim_scores]
    return movies_df['title'].iloc[movie_indices].tolist()

# --- Emotion to Genre Mapping ---
EMOTION_GENRE_MAP = {
    'Happy': ['Comedy', 'Family', 'Animation', 'Romance'],
    'Sad': ['Drama', 'Romance'],
    'Surprise': ['Adventure', 'Fantasy', 'Thriller'],
    'Angry': ['Action', 'Crime', 'Thriller'],
    'Disgust': ['Horror', 'Crime'],
    'Fear': ['Thriller', 'Horror', 'Mystery'],
    'Neutral': ['Drama', 'Documentary'],
    'Funny': ['Comedy', 'Family'],
    'Adventurous': ['Adventure', 'Action'],
    'Romantic': ['Romance', 'Drama'],
    'Emotional': ['Drama', 'Romance'],
    'Intense': ['Thriller', 'Action'],
    'Heartwarming': ['Family', 'Animation'],
    'Imaginative': ['Fantasy', 'Science Fiction'],
    'Thought-Provoking': ['Documentary', 'Drama']
}

@app.route('/recommend', methods=['GET'])
def recommend():
    """API endpoint for emotion/genre-based recommendations."""
    if movies_df is None:
        return jsonify({'error': 'Server data not loaded.'}), 500

    mood = request.args.get('mood')
    if not mood:
        return jsonify({'error': 'Mood parameter is required'}), 400

    # Map emotion to genres
    genres = EMOTION_GENRE_MAP.get(mood, [])
    if genres:
        genre_movies = movies_df[movies_df['genres'].apply(lambda g: any(genre in g for genre in genres))]
    else:
        genre_movies = movies_df

    if genre_movies.empty:
        return jsonify({'error': f'No movies found for mood/genres: {mood}'}), 404

    seed_movie_title = random.choice(genre_movies['title'].tolist())
    recommended_titles = get_recommendations(seed_movie_title)

    recommendations_with_details = []
    for title in recommended_titles:
        movie_data = movies_df[movies_df['title'] == title].iloc[0]
        year = int(movie_data['release_year'])
        details = get_movie_details(title, year)
        recommendations_with_details.append({
            'title': title, 'year': year, 'poster': details['poster'],
            'plot': details['plot'], 'imdbRating': details['imdbRating']
        })

    return jsonify(recommendations_with_details)

if __name__ == '__main__':
    if OMDB_API_KEY == 'YOUR_OMDB_API_KEY':
        print("\n⚠️  WARNING: OMDb API key is not set in app.py. Posters will not load.")
    app.run(debug=True)