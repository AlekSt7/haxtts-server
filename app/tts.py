import io
import time
import logging
import asyncio
from auralis import TTS, TTSRequest, TTSOutput
from auralis.common.definitions.requests import SupportedLanguages

from app.config import models_directory, speakers_directory, settings
from app.language_mapper import map_mary_tts_to_xtts_language_codes
from app.text_splitter import get_text_parts

logger = logging.getLogger('uvicorn')

logger.info("Trying to load xtts model...")
current_model = settings.current_model
tts = TTS().from_pretrained("test/core_xttsv2", gpt_model='test/gpt')

async def generate_speech(text_parts: list[str], speaker: str, language: str) -> io.BytesIO:

    logger.info(f'Inference xtts model, language is {language}')

    # Create audio buffer
    in_memory_audio_buffer = io.BytesIO()

    # Create multiple requests
    requests = [
        TTSRequest(
            text=i,
            speaker_files=[f"{speakers_directory}{speaker}.wav"],
            language = language
        ) for i in text_parts
    ]

    # Process in parallel
    coroutines = [tts.generate_speech_async(req) for req in requests]
    outputs = await asyncio.gather(*coroutines, return_exceptions=True)

    # Handle results
    valid_outputs = [
        out for out in outputs
        if not isinstance(out, Exception)
    ]

    # Combine results
    combined = TTSOutput.combine_outputs(valid_outputs)
    in_memory_audio_buffer.write(combined.to_bytes())
    in_memory_audio_buffer.seek(0)

    return in_memory_audio_buffer

async def get_audio_in_bytes(text: str, speaker: str, language: str) -> io.BytesIO:

    # Check for the presence of speaker file
    if speaker not in settings.xtts_speakers:
        raise RuntimeError(f'Invalid speaker: speaker {speaker} not found in speakers directory')

    logger.info(f'Start text processing: {text}')

    start_time = time.time()

    # Prepare data for tts
    auralis_language = 'auto' if settings.auto_detect_language else map_mary_tts_to_xtts_language_codes(language)
    text_parts = get_text_parts(text, settings.max_text_parts_count)

    logger.info(f'Text parts: {text_parts}, size: {len(text_parts)}')

    # Run tts
    result = await generate_speech(text_parts=text_parts, speaker=speaker, language=auralis_language)

    elapsed_time = time.time() - start_time
    logger.info(f'Time spent on the process: {elapsed_time}')

    return result
