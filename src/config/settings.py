import os
from dotenv import load_dotenv

load_dotenv()

# Spotify API Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

# API Scopes
SCOPE = " ".join([
    "playlist-read-private",
    "playlist-read-collaborative", 
    "user-library-read",
    "user-top-read"
])

# Audio Features for Analysis
AUDIO_FEATURES = [
    'danceability', 'energy', 'valence', 'acousticness',
    'instrumentalness', 'liveness', 'speechiness', 'tempo'
]

# Recommendation Settings
DEFAULT_NUM_RECOMMENDATIONS = 10
MAX_CANDIDATE_TRACKS = 500