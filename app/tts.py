import time
import hashlib
import os
import logging
import torch

import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

from app.config import audios_directory, models_directory, speakers_directory, settings

logger = logging.getLogger('uvicorn')

# Init TTS
config = XttsConfig()

current_model = settings.current_model

logger.info("Trying to load xtts model...")
config.load_json(models_directory + current_model + "/config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir=models_directory + current_model,
                      vocab_path=models_directory + current_model + "/vocab.json", use_deepspeed=settings.use_deep_speed)

if settings.use_cpu:
    model.cpu()
else:
    model.cuda()

def generate_speach(text: str, speaker: str, file_path: str, language: str) -> bool:

    logger.info("Computing speaker latents...")
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=speakers_directory + speaker + ".wav")

    logger.info("Inference xtts model...")
    out = model.inference(
        text,
        language,
        gpt_cond_latent,
        speaker_embedding,
        speed=1
    )
    torchaudio.save(file_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)

    return True


def get_audio_file(text: str, speaker: str, language: str, file_extension: str = 'wav') -> str:
    text_hash = hashlib.sha512(bytes(text, 'UTF-8')).hexdigest()
    file_path = audios_directory + speaker + '-' + text_hash + '.' + file_extension

    if not os.path.exists(audios_directory):
        os.mkdir(audios_directory)

    if os.path.exists(file_path):
        return file_path

    if speaker not in settings.xtts_speakers:
        raise RuntimeError(f'Invalid speaker: speaker {speaker} not found in speakers directory')

    logger.info(f'Start text processing: {text}')

    start_time = time.time()

    generate_speach(text=text, speaker=speaker, file_path=file_path, language=language)

    elapsed_time = time.time() - start_time
    logger.info(f'Time spent on the process: {elapsed_time}')

    return file_path
