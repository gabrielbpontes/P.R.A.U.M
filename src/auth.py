"""
Autenticação com a API do Spotify
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SCOPE
from .utils import setup_logger

logger = setup_logger(__name__)

def create_spotify_client() -> spotipy.Spotify:
    """
    Cria e retorna um cliente autenticado do Spotify
    
    Returns:
        spotipy.Spotify: Cliente autenticado
        
    Raises:
        spotipy.SpotifyException: Se a autenticação falhar
    """
    try:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SCOPE,
            cache_path=".spotify_cache"
        )
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        

        user = sp.current_user()
        logger.info(f"Autenticado como: {user.get('display_name', 'Usuário')}")
        
        return sp
        
    except Exception as e:
        logger.error(f"Falha na autenticação: {e}")
        raise

def test_connection() -> bool:
    """Testa a conexão com a API do Spotify"""
    try:
        sp = create_spotify_client()
        user = sp.current_user()
        print(f"Conectado como: {user.get('display_name', 'Usuário')}")
        return True
    except Exception as e:
        print(f"Falha na conexão: {e}")
        return False

if __name__ == "__main__":
    # Teste de conexão
    if test_connection():
        print("Conexão estabelecida com sucesso!")
    else:
        print("Verifique suas credenciais no arquivo .env")