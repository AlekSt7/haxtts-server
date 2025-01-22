def map_mary_tts_to_xtts_language_codes(xtts_language_code: str) -> str:
    mary_tts_to_xtts = {
        'de': 'de',
        'en_GB': 'en',
        'en_US': 'en',
        'fr': 'fr',
        'it': 'it',
        'lb': '',
        'ru': 'ru',
        'sv': '',
        'te': '',
        'tr': 'tr'
    }
    language_code: str
    try:
         language_code = mary_tts_to_xtts[xtts_language_code]
    except KeyError as e:
        raise ValueError(f'Undefined unit: {e.args[0]}')
    check_xtts_language_code_support(language_code)
    return language_code

def check_xtts_language_code_support(xtts_language_code):
    if not xtts_language_code:
        raise RuntimeError("Language not supported by xtts")