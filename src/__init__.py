"""
P.R.A.U.M - Um sistema inteligente de recomendação de músicas
"""

__version__ = "0.1.0"
__author__ = "Gabriel Pontes"

from .auth import create_spotify_client
from .recommender import MusicRecommender
from .analyzer import PlaylistAnalyzer, analyze_playlist

__all__ = [
    "create_spotify_client",
    "MusicRecommender", 
    "PlaylistAnalyzer",
    "analyze_playlist",
]