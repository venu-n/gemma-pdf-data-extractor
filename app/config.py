from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    input_dir: Path = Path('input')
    output_dir: Path = Path('output')
    samples_dir: Path = Path('samples')
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:e4b"

    huggingface_api_key: str = ""
    huggingface_model: str = ""
    huggingface_provider: str = ""

    vision_provider: str = "ollama"
    vision_timeout: int = 360
    render_dpi: int = 150
    detector_padding: int = 10
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = Settings()
