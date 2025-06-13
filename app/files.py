import os

import aiofiles
from fastapi import UploadFile

from app.const import speakers_directory, voice_extension


def delete_file_from_speakers_directory(filename: str):
    file_path = os.path.join(speakers_directory, filename + voice_extension)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: file '{filename}' not found.")
    os.remove(file_path)


async def save_file_to_speakers_directory(in_file: UploadFile):
    file_path = os.path.join(speakers_directory, in_file.filename)
    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk


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
