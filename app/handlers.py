import gc
import logging
import json
import os.path

from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, PlainTextResponse
from urllib.parse import parse_qs
from functools import lru_cache

from starlette.responses import StreamingResponse, FileResponse, JSONResponse

from app.config import Settings, settings
from app.const import voice_extension, speakers_directory, static_dir
from app.files import save_file_to_speakers_directory, delete_file_from_speakers_directory, scan_files_for_names
from app.tts import get_audio_in_bytes

logger = logging.getLogger('uvicorn')
router = APIRouter()


def handle_tts_error(exception: RuntimeError):
    logger.error(exception)
    if settings.voice_tts_errors:
        return FileResponse("./error.wav", media_type="audio/wav", filename="audio.wav")
    else:
        return HTMLResponse(status_code=400)


@lru_cache()
def get_settings():
    return settings


# main

@router.get('/')
async def index():
    return {'status': 'work'}


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return FileResponse(os.path.join(static_dir, "index.html"))


# tts

@router.get('/process')
async def process(request: Request):
    request_args = dict(request.query_params)

    print(request_args)

    speaker = request_args['VOICE']
    text = request_args['INPUT_TEXT']
    language = request_args['LOCALE'][0]

    try:
        audio_file = await get_audio_in_bytes(text=text, speaker=speaker, language=language)
        return StreamingResponse(content=audio_file, media_type='audio/wav')
    except RuntimeError as exception:
        return handle_tts_error(exception)


# noinspection PyRedundantParentheses
@router.post('/process')
async def process(request: Request):
    body = await request.body()
    body_decoded = body.decode("utf-8")
    body_args = parse_qs(body_decoded)

    print(body_args)

    speaker = body_args['VOICE'][0]
    text = body_args['INPUT_TEXT'][0]
    language = body_args['LOCALE'][0]

    try:
        audio_file = await get_audio_in_bytes(text=text, speaker=speaker, language=language)
        return StreamingResponse(content=audio_file, media_type='audio/wav')
    except RuntimeError as exception:
        return handle_tts_error(exception)


@router.get('/settings')
async def show_settings(settings: Settings = Depends(get_settings)):
    settings_dict = settings.dict()
    return PlainTextResponse(json.dumps(settings_dict, indent=2))


@router.get('/clear_cache')
async def clear_cache():
    try:
        gc.collect()
        return PlainTextResponse(status_code=200, content='Success')
    except Exception as e:
        logger.error(e)
        return PlainTextResponse(status_code=400, content='Error')


# voices

@router.get('/voices', response_class=HTMLResponse)
async def process():
    return '\n'.join(settings.xtts_speakers)


@router.get('/available-voices', response_class=JSONResponse)
async def process():
    return JSONResponse(settings.xtts_speakers)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(voice_extension):
        response = HTMLResponse(status_code=400)
        response.body = f"Only {voice_extension} files are allowed"
        return response
    await save_file_to_speakers_directory(file)
    settings.xtts_speakers = scan_files_for_names(speakers_directory, voice_extension)
    return {"filename": file.filename}


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    try:
        delete_file_from_speakers_directory(filename)
    except FileNotFoundError:
        response = HTMLResponse(status_code=404)
        response.body = f"File {filename} not found"
        return response
    settings.xtts_speakers = scan_files_for_names(speakers_directory, voice_extension)
    return {"detail": "File deleted successfully"}


@router.get(path="/files/{filename}")
async def post_media_file(filename: str):
    return FileResponse(f"{speakers_directory}/{filename}{voice_extension}", media_type="audio/mpeg")
