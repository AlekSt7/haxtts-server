import logging
import os
from typing import Final, Optional

import torch
from pydantic import Field

from pydantic_settings import BaseSettings

logger = logging.getLogger('uvicorn')
speakers_directory_name: Final = 'speakers'
root_dir = os.path.dirname(os.path.abspath(__file__))
speakers_directory: Final = os.path.join(root_dir, speakers_directory_name)
voice_extension: Final = '.wav'
version = '1.0.0'

def scan_files_for_names(directory, extensions) -> list[str]:
    if not os.path.exists(directory):
        raise RuntimeError(f"Directory '{directory}' not found.")

    matching_files: list[str] = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_name_without_extension = os.path.splitext(file)[0]
                matching_files.append(file_name_without_extension)
    return matching_files

class Settings(BaseSettings):
    logger.info(f'Current version: {version}')
    logger.info(f'Getting service configuration...')

    auto_detect_language: bool = False
    current_model: str = "AstraMindAI/xttsv2"
    current_model_gpt: str = "AstraMindAI/xtts2-gpt"
    max_text_parts_count: int = 8

    xtts_speakers: Optional[list[str]] = Field(None)

    class Config:
        env_file = ".env"

settings = Settings()

def settings_checker():
    if not os.path.exists(speakers_directory):
        os.mkdir(f"./{speakers_directory}/")

    settings.xtts_speakers = scan_files_for_names(speakers_directory, voice_extension)

    logger.info(f'Found voices: {settings.xtts_speakers}')
    logger.info(f'Current xtts model is: {settings.current_model}')

settings_checker()
