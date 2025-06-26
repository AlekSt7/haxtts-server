import os
from typing import Final

static_dir: Final[str] = os.path.join(os.path.dirname(__file__), 'webapp')
speakers_directory: Final[str] = './speakers'
voice_extension: Final[str] = '.wav'
port: Final[int] = 9898
