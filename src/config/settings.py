"""
Configurações globais do projeto
"""

import os
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Validação das credenciais
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError(
        "Credenciais do Spotify não encontradas. "
        "Configure SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET no arquivo .env"
    )

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

# Logging
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")