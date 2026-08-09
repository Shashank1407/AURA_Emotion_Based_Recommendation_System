import pandas as pd
import ast

def preprocess_data():
    """
    Loads the movies metadata, cleans it, engineers mood features,
    and saves the processed data.
    """
    print("Starting data preprocessing...")

    try:
        # Load the dataset
        df = pd.read_csv('data/movies_metadata.csv', low_memory=False)
        print("Dataset loaded successfully.")

        # Keep only necessary columns
        df = df[['id', 'title', 'overview', 'genres', 'release_date']].copy()

        # --- Data Cleaning ---
        df.dropna(subset=['title', 'overview'], inplace=True)
        # Ensure standard date format (YYYY-MM-DD) to avoid errors
        df = df[df['release_date'].str.len() == 10]
        df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
        df.dropna(subset=['release_year'], inplace=True)
        df['release_year'] = df['release_year'].astype(int)

        def clean_genres(genres_str):
            try:
                genres_list = ast.literal_eval(genres_str)
                return [g['name'] for g in genres_list]
            except (ValueError, SyntaxError):
                return []
        
        df['genres'] = df['genres'].apply(clean_genres)
        print("Genres cleaned.")

        # --- Mood Feature Engineering ---
        mood_map = {
            'Action': 'Adrenaline Rush', 'Adventure': 'Adventurous', 'Animation': 'Feel Good',
            'Comedy': 'Funny', 'Crime': 'Intense', 'Documentary': 'Thought-Provoking',
            'Drama': 'Emotional', 'Family': 'Heartwarming', 'Fantasy': 'Imaginative',
            'History': 'Thought-Provoking', 'Horror': 'Scary', 'Music': 'Feel Good',
            'Mystery': 'Intriguing', 'Romance': 'Romantic', 'Science Fiction': 'Imaginative',
            'Thriller': 'Intense', 'War': 'Intense', 'Western': 'Gritty'
        }

        def get_mood(genres):
            for genre in genres:
                if genre in mood_map:
                    return mood_map[genre]
            return 'Neutral'

        df['mood'] = df['genres'].apply(get_mood)
        print("Mood feature engineered.")
        
        # Filter out movies with no clear mood
        df = df[df['mood'] != 'Neutral']
        df.reset_index(drop=True, inplace=True)

        df.to_csv('data/preprocessed_movies.csv', index=False)
        print("Preprocessing complete. Saved to 'data/preprocessed_movies.csv'")

    except FileNotFoundError:
        print("Error: 'data/movies_metadata.csv' not found.")
        print("Please download the dataset and place it in the 'data/' directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    preprocess_data()