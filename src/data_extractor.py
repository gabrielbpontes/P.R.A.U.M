"""
Extração de dados da API do Spotify
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from .auth import create_spotify_client
from .config.settings import AUDIO_FEATURES
from .utils import setup_logger, format_duration

logger = setup_logger(__name__)

class DataExtractor:
    """Classe para extrair dados do Spotify"""
    
    def __init__(self):
        self.sp = create_spotify_client()
    
    def get_user_playlists(self) -> Dict[str, str]:
        """
        Retorna todas as playlists do usuário
        
        Returns:
            Dict[str, str]: Dicionário {nome_da_playlist: id_da_playlist}
        """
        try:
            playlists = {}
            results = self.sp.current_user_playlists()
            
            while results:
                for playlist in results['items']:
                    playlists[playlist['name']] = playlist['id']
                
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
            
            logger.info(f"Encontradas {len(playlists)} playlists")
            return playlists
            
        except Exception as e:
            logger.error(f"Erro ao buscar playlists: {e}")
            return {}
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Extrai todas as músicas de uma playlist específica
        
        Args:
            playlist_id: ID da playlist no Spotify
            
        Returns:
            List[Dict]: Lista de dicionários com informações das músicas
        """
        tracks = []
        
        try:
            results = self.sp.playlist_tracks(playlist_id)
            
            while results:
                for item in results['items']:
                    track = item['track']
                    
                    if track:  
                        track_info = {
                            'id': track['id'],
                            'name': track['name'],
                            'artist': track['artists'][0]['name'],
                            'artist_id': track['artists'][0]['id'],
                            'album': track['album']['name'],
                            'album_id': track['album']['id'],
                            'duration_ms': track['duration_ms'],
                            'duration_formatted': format_duration(track['duration_ms']),
                            'popularity': track['popularity'],
                            'track_number': track['track_number'],
                            'explicit': track.get('explicit', False)
                        }
                        tracks.append(track_info)
                
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
            
            logger.info(f"Extraídas {len(tracks)} músicas da playlist {playlist_id}")
            
        except Exception as e:
            logger.error(f"Erro ao extrair músicas da playlist: {e}")
        
        return tracks
    
    def get_audio_features_batch(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Obtém audio features para um lote de tracks
        
        Args:
            track_ids: Lista de IDs das tracks
            
        Returns:
            List[Dict]: Lista de dicionários com audio features
        """
        audio_features = []
        
        try:
            # A API do Spotify limita a 100 tracks por request
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i:i + 100]
                features_batch = self.sp.audio_features(batch)
                
                audio_features.extend([f for f in features_batch if f])
            
            logger.info(f"Obtidas audio features para {len(audio_features)} músicas")
            
        except Exception as e:
            logger.error(f"Erro ao obter audio features: {e}")
        
        return audio_features
    
    def get_track_features(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém audio features para uma única track
        
        Args:
            track_id: ID da track
            
        Returns:
            Dict: Audio features da track
        """
        try:
            features = self.sp.audio_features([track_id])
            return features[0] if features else None
        except Exception as e:
            logger.error(f"Erro ao obter features da track {track_id}: {e}")
            return None
    
    def search_tracks(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca tracks no Spotify
        
        Args:
            query: Termo de busca
            limit: Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de tracks encontradas
        """
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = results['tracks']['items']
            
            logger.info(f"Encontradas {len(tracks)} tracks para busca: '{query}'")
            return tracks
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def get_playlist_dataframe(self, playlist_name: str) -> Optional[pd.DataFrame]:
        """
        Cria um DataFrame completo para uma playlist
        
        Args:
            playlist_name: Nome da playlist
            
        Returns:
            pd.DataFrame: DataFrame com todas as informações
        """
        try:
            playlists = self.get_user_playlists()
            
            if playlist_name not in playlists:
                logger.error(f"Playlist '{playlist_name}' não encontrada")
                return None
            
            playlist_id = playlists[playlist_name]
            
            tracks = self.get_playlist_tracks(playlist_id)
            
            if not tracks:
                logger.error("Nenhuma música encontrada na playlist")
                return None
            
            track_ids = [track['id'] for track in tracks]
            audio_features = self.get_audio_features_batch(track_ids)
            
            for i, track in enumerate(tracks):
                if i < len(audio_features) and audio_features[i]:
                    for feature in AUDIO_FEATURES:
                        if feature in audio_features[i]:
                            track[feature] = audio_features[i][feature]
            
            df = pd.DataFrame(tracks)
            
            df['playlist_name'] = playlist_name
            
            logger.info(f"DataFrame criado com {len(df)} músicas e {len(df.columns)} colunas")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao criar DataFrame: {e}")
            return None

def extract_playlist_data(playlist_name: str) -> Optional[pd.DataFrame]:
    """
    Função principal de extração de dados
    
    Args:
        playlist_name: Nome da playlist
        
    Returns:
        pd.DataFrame: DataFrame com os dados da playlist
    """
    extractor = DataExtractor()
    return extractor.get_playlist_dataframe(playlist_name)

if __name__ == "__main__":
    extractor = DataExtractor()
    
    playlists = extractor.get_user_playlists()
    print("Playlists disponíveis:")
    for name in list(playlists.keys())[:5]:
        print(f"  - {name}")
    
    if playlists:
        first_playlist = list(playlists.keys())[0]
        print(f"\nExtraindo dados da playlist: {first_playlist}")
        
        df = extractor.get_playlist_dataframe(first_playlist)
        if df is not None:
            print(f"\nPrimeiras 5 músicas:")
            print(df[['name', 'artist', 'danceability', 'energy']].head())