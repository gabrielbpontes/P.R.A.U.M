from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="spotify-recommender",
    version="0.1.0",
    author="Gabriel Batista Pontes",
    author_email="gabriel91pontes@gmail.com",
    description="Recomendador inteligente que cria playlists adaptadas ao perfil e ao comportamento musical do usuário.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gabrielbpontes/P.R.A.U.M",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "spotify-recommender=spotify_recommender.cli:main",
        ],
    },
)