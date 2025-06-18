import logging
import os
from typing import Optional

from pydantic import Field

from pydantic_settings import BaseSettings

from app.const import speakers_directory, voice_extension
from app.files import scan_files_for_names

logger = logging.getLogger('uvicorn')
root_dir = os.path.dirname(os.path.abspath(__file__))
version = '1.0.0'


class Settings(BaseSettings):
    logger.info(f'Current version: {version}')
    logger.info(f'Getting service configuration...')

    auto_detect_language: bool = False
    remove_dots_at_the_end: bool = True
    voice_tts_errors: bool = True
    base_model: str = "AstraMindAI/xttsv2"
    gpt_model: str = "AstraMindAI/xtts2-gpt"
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
    logger.info(f'Current xtts model is: {settings.base_model}')


settings_checker()
