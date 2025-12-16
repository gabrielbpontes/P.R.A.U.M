"""
Análise exploratória de playlists
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import plotly.graph_objects as go
import plotly.express as px

from .data_extractor import extract_playlist_data
from .config.settings import AUDIO_FEATURES
from .utils import setup_logger, normalize_features

logger = setup_logger(__name__)

@dataclass
class PlaylistProfile:
    """Perfil musical de uma playlist"""
    name: str
    track_count: int
    unique_artists: int
    avg_duration: float
    avg_popularity: float
    features_mean: Dict[str, float]
    features_std: Dict[str, float]
    top_artists: Dict[str, int]
    audio_mood: str

class PlaylistAnalyzer:
    """Analisador de playlists"""
    
    def __init__(self):
        self.setup_visualization()
    
    def setup_visualization(self):
        """Configura o estilo dos gráficos"""
        plt.style.use('default')
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def analyze_playlist(self, playlist_name: str) -> Optional[PlaylistProfile]:
        """
        Analisa uma playlist e retorna seu perfil
        
        Args:
            playlist_name: Nome da playlist
            
        Returns:
            PlaylistProfile: Perfil da playlist
        """
        logger.info(f"Analisando playlist: {playlist_name}")
        
        df = extract_playlist_data(playlist_name)
        if df is None or df.empty:
            logger.error(f"Não foi possível analisar a playlist '{playlist_name}'")
            return None
        
        track_count = len(df)
        unique_artists = df['artist'].nunique()
        avg_duration = df['duration_ms'].mean() / 60000 
        avg_popularity = df['popularity'].mean()
        
        features_mean = {}
        features_std = {}
        
        for feature in AUDIO_FEATURES:
            if feature in df.columns:
                features_mean[feature] = df[feature].mean()
                features_std[feature] = df[feature].std()

        top_artists = df['artist'].value_counts().head(5).to_dict()
        
        audio_mood = self._determine_mood(features_mean)
        
        profile = PlaylistProfile(
            name=playlist_name,
            track_count=track_count,
            unique_artists=unique_artists,
            avg_duration=avg_duration,
            avg_popularity=avg_popularity,
            features_mean=features_mean,
            features_std=features_std,
            top_artists=top_artists,
            audio_mood=audio_mood
        )
        
        logger.info(f"Análise concluída para '{playlist_name}'")
        return profile
    
    def _determine_mood(self, features_mean: Dict[str, float]) -> str:
        """Determina o 'mood' da playlist baseado nas audio features"""
        mood_rules = [
            (features_mean.get('energy', 0) > 0.7 and features_mean.get('danceability', 0) > 0.7, "Energética/Dançante"),
            (features_mean.get('energy', 0) < 0.3 and features_mean.get('acousticness', 0) > 0.7, "Calma/Acústica"),
            (features_mean.get('valence', 0) > 0.7, "Feliz/Positiva"),
            (features_mean.get('valence', 0) < 0.3, "Melancólica/Triste"),
            (features_mean.get('instrumentalness', 0) > 0.7, "Instrumental"),
            (features_mean.get('speechiness', 0) > 0.66, "Falada/Poética"),
        ]
        
        for condition, mood in mood_rules:
            if condition:
                return mood
        
        return "Mista/Equilibrada"
    
    def plot_feature_distribution(self, df: pd.DataFrame, save_path: Optional[str] = None):
        """
        Plota distribuição das audio features
        
        Args:
            df: DataFrame com as músicas
            save_path: Caminho para salvar o gráfico (opcional)
        """
        features_to_plot = [f for f in AUDIO_FEATURES if f in df.columns]
        
        if not features_to_plot:
            logger.warning("Nenhuma audio feature disponível para plotar")
            return
        
        n_features = len(features_to_plot)
        n_cols = 3
        n_rows = (n_features + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = axes.ravel() if n_rows > 1 else [axes]
        
        for i, feature in enumerate(features_to_plot):
            ax = axes[i]
            ax.hist(df[feature], bins=20, alpha=0.7, edgecolor='black', color='skyblue')
            ax.set_title(f'Distribuição de {feature}', fontsize=12)
            ax.set_xlabel(feature)
            ax.set_ylabel('Frequência')
            ax.grid(True, alpha=0.3)
        
        # Remove eixos vazios
        for i in range(len(features_to_plot), len(axes)):
            fig.delaxes(axes[i])
        
        plt.suptitle('Distribuição das Audio Features', fontsize=16, y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {save_path}")
        
        plt.show()
    
    def plot_correlation_matrix(self, df: pd.DataFrame, save_path: Optional[str] = None):
        """
        Plota matriz de correlação entre features
        
        Args:
            df: DataFrame com as músicas
            save_path: Caminho para salvar o gráfico (opcional)
        """
        features_to_plot = [f for f in AUDIO_FEATURES if f in df.columns]
        
        if len(features_to_plot) < 2:
            logger.warning("Poucas features para matriz de correlação")
            return
        
        corr_matrix = df[features_to_plot].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, fmt='.2f',
                   cbar_kws={"shrink": 0.8})
        plt.title('Matriz de Correlação entre Audio Features', fontsize=16)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Matriz de correlação salva em: {save_path}")
        
        plt.show()
    
    def create_interactive_radar_chart(self, profile: PlaylistProfile):
        """
        Cria gráfico de radar interativo para o perfil da playlist
        
        Args:
            profile: Perfil da playlist
        """
        features = list(profile.features_mean.keys())
        values = list(profile.features_mean.values())
        
        # Fecha o gráfico conectando o último ponto ao primeiro
        features.append(features[0])
        values.append(values[0])
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=features,
            fill='toself',
            line=dict(color='rgb(30, 215, 96)'),
            fillcolor='rgba(30, 215, 96, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title=f"Perfil de Audio Features: {profile.name}",
            showlegend=False
        )
        
        fig.show()
    
    def generate_report(self, playlist_name: str) -> Optional[Dict[str, Any]]:
        """
        Gera um relatório completo da análise
        
        Args:
            playlist_name: Nome da playlist
            
        Returns:
            Dict: Relatório com todas as análises
        """
        # Obtém dados
        df = extract_playlist_data(playlist_name)
        if df is None:
            return None
        
        # Cria perfil
        profile = self.analyze_playlist(playlist_name)
        if profile is None:
            return None
        
        # Prepara relatório
        report = {
            'playlist_name': playlist_name,
            'summary': {
                'total_tracks': profile.track_count,
                'unique_artists': profile.unique_artists,
                'avg_duration_minutes': round(profile.avg_duration, 2),
                'avg_popularity': round(profile.avg_popularity, 2),
                'audio_mood': profile.audio_mood
            },
            'top_artists': profile.top_artists,
            'feature_statistics': {
                'mean': profile.features_mean,
                'std': profile.features_std
            },
            'data_sample': df[['name', 'artist', 'popularity']].head().to_dict('records')
        }
        
        return report

def analyze_playlist(playlist_name: str) -> Optional[PlaylistProfile]:
    """
    Função principal para análise de playlist
    
    Args:
        playlist_name: Nome da playlist
        
    Returns:
        PlaylistProfile: Perfil da playlist
    """
    analyzer = PlaylistAnalyzer()
    return analyzer.analyze_playlist(playlist_name)

def generate_analysis_report(playlist_name: str, save_plots: bool = False):
    """
    Gera e exibe um relatório completo de análise
    
    Args:
        playlist_name: Nome da playlist
        save_plots: Se True, salva os gráficos
    """
    analyzer = PlaylistAnalyzer()
    
    # Obtém dados
    df = extract_playlist_data(playlist_name)
    if df is None:
        print(f"❌ Não foi possível analisar a playlist '{playlist_name}'")
        return
    
    # Cria perfil
    profile = analyzer.analyze_playlist(playlist_name)
    if profile is None:
        return
    
    # Exibe relatório
    print("\n" + "="*60)
    print(f"📊 RELATÓRIO DA PLAYLIST: {playlist_name}")
    print("="*60)
    
    print(f"\n📈 RESUMO:")
    print(f"  • Total de músicas: {profile.track_count}")
    print(f"  • Artistas únicos: {profile.unique_artists}")
    print(f"  • Duração média: {profile.avg_duration:.2f} minutos")
    print(f"  • Popularidade média: {profile.avg_popularity:.1f}/100")
    print(f"  • Mood predominante: {profile.audio_mood}")
    
    print(f"\n🎤 TOP 5 ARTISTAS:")
    for artist, count in profile.top_artists.items():
        print(f"  • {artist}: {count} música(s)")
    
    print(f"\n🎵 AUDIO FEATURES (média):")
    for feature, value in profile.features_mean.items():
        print(f"  • {feature}: {value:.3f}")
    
    # Gera visualizações
    if save_plots:
        analyzer.plot_feature_distribution(df, f"{playlist_name}_distribution.png")
        analyzer.plot_correlation_matrix(df, f"{playlist_name}_correlation.png")
    else:
        analyzer.plot_feature_distribution(df)
        analyzer.plot_correlation_matrix(df)
    
    # Gráfico interativo
    analyzer.create_interactive_radar_chart(profile)
    
    return profile

if __name__ == "__main__":
    # Teste da análise
    analyzer = PlaylistAnalyzer()
    
    # Lista playlists disponíveis
    from .data_extractor import DataExtractor
    extractor = DataExtractor()
    playlists = extractor.get_user_playlists()
    
    if playlists:
        test_playlist = list(playlists.keys())[0]
        print(f"🔍 Testando análise na playlist: '{test_playlist}'")
        
        # Gera relatório completo
        generate_analysis_report(test_playlist)
    else:
        print("❌ Nenhuma playlist encontrada")