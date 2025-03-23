import gc
import logging
import json

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse
from urllib.parse import parse_qs
from functools import lru_cache

from starlette.responses import StreamingResponse

from app.config import Settings, settings
from app.tts import get_audio_in_bytes

logger = logging.getLogger('uvicorn')
router = APIRouter()


@lru_cache()
def get_settings():
    return settings


@router.get('/')
async def index():
    return {'status': 'work'}


@router.get('/voices', response_class=HTMLResponse)
async def process(settings: Settings = Depends(get_settings)):
    return '\n'.join(settings.xtts_speakers)


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
        logger.error(exception)
        return HTMLResponse(status_code=400)


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
        logger.error(exception)
        return HTMLResponse(status_code=400)


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


