"""
Funções utilitárias compartilhadas
"""

import logging
from typing import List, Dict, Any
import pandas as pd

def setup_logger(name: str = __name__) -> logging.Logger:
    """Configura um logger para o módulo"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        from .config.settings import LOG_LEVEL
        logger.setLevel(getattr(logging, LOG_LEVEL))
    
    return logger

def normalize_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza features para análise comparativa
    """
    df_normalized = df.copy()
    
    # Normaliza tempo (BPM) para escala 0-1
    if 'tempo' in df_normalized.columns:
        df_normalized['tempo_normalized'] = (df_normalized['tempo'] - 50) / 200  # Assume 50-250 BPM
    
    # Normaliza loudness para escala 0-1
    if 'loudness' in df_normalized.columns:
        df_normalized['loudness_normalized'] = (df_normalized['loudness'] + 60) / 60  # -60 a 0 dB
    
    return df_normalized

def format_duration(ms: int) -> str:
    """Formata milissegundos para MM:SS"""
    seconds = int(ms / 1000)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"

def validate_playlist_name(playlist_name: str, available_playlists: Dict[str, str]) -> bool:
    """Valida se o nome da playlist existe"""
    return playlist_name in available_playlists