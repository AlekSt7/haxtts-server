import logging
import os
from typing import Final

import torch

from pydantic import BaseSettings

logger = logging.getLogger('uvicorn')
models_directory: Final = './models/'
speakers_directory: Final = './speakers/'
audios_directory: Final = './audios/'
voice_extension: Final = '.wav'
version = '1.0.0'

def scan_files_for_names(directory, extensions):
    if not os.path.exists(directory):
        raise RuntimeError(f"Directory '{directory}' not found.")

    matching_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                # Получаем имя файла без расширения
                file_name_without_extension = os.path.splitext(file)[0]
                matching_files.append(file_name_without_extension)
    return matching_files


def get_subdirectories(directory):
    if not os.path.exists(directory):
        raise RuntimeError(f"Directory '{directory}' not found.")

    all_entries = os.listdir(directory)
    subdirectories = [entry for entry in all_entries if os.path.isdir(os.path.join(directory, entry))]
    return subdirectories

class Settings(BaseSettings):
    logger.info(f'Current version: {version}')
    logger.info(f'Getting service configuration...')

    default_language: Final = 'ru'
    use_deep_speed: bool = False
    use_cpu: bool = False
    current_model = "Roxy_Migurdia_coqui_XTTS"

    xtts_models = []
    xtts_speakers = []

    class Config:
        env_file = ".env"

settings = Settings()

def settings_checker():
    if not os.path.exists(models_directory):
        os.mkdir(models_directory)

    if not torch.cuda.is_available() and not settings.use_cpu:
        logger.warning("Use of cuda is enabled in the configuration, but cuda is not available on this device. Using the cpu instead")
        settings.use_cpu = True

    if not os.path.exists(speakers_directory):
        os.mkdir(speakers_directory)

    settings.xtts_models = get_subdirectories(models_directory)
    settings.xtts_speakers = scan_files_for_names(speakers_directory, voice_extension)

    logger.info(f'Found xtts models: {settings.xtts_models}')
    logger.info(f'Found voices: {settings.xtts_speakers}')
    logger.info(f'Current xtts model is: {settings.current_model}')

    if settings.current_model not in settings.xtts_models:
        raise RuntimeError("Xtts model to use not found in models directory")

    if not os.path.exists(audios_directory):
        os.mkdir(audios_directory)

settings_checker()
