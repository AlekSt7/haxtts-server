![Supports amd64 Architecture][amd64-badge]
![Supports by nvidia gpu][nvidia-badge]
[![MIT License][license-shield]][license-url]

# HAxTTS Server

[![en](https://img.shields.io/badge/lang-ru-red.svg)](./README.ru.md)

## Contents
- [About the project](#about)
- [Startup recommendations](#start-recommendation)
- [Server installation](#server-install)
- [Server configuration](#server-configure)
- [Configuration in Home Assistant](#ha-configure)
- [Configuration in Rhasspy](#rhasspy-configure)
- [Output sound to a Bluetooth speaker](#bluetooth-speaker)
- [Finetune models](#finetune)
- [API](#api)
- [Development](#development)

<a id="about"></a>
## About the project

![Logo]
Hax-TTS is a Mary TTS compatible server for speech synthesis with XTTSv2 models support.
This project aims to provide your Home Assistant with high-quality speech synthesis.</br>
The server is based on [XTTSv2] models from [Coqui] (support discontinued, working [fork] from idiap).
The very cool project [Auralis] is used as a backend for model inference.</br>
The server supports parallel computing to speed up speech synthesis on large amounts of text.
Pre-trained custom models are also supported (currently only links to Hugging Face).</br>

The models themselves are multilingual, so the choice of language in the Mary TTS integration only affects the accent when pronouncing speech.
The models also support cloning any voices (both male and female).</br>
To select a voice, you need to set the `voice` parameter in the Mary TTS configuration to the name of the wav file with the recorded voice sample, see [Configuration in Home Assistant](#ha-configure).
It is also possible to add or remove your own wav files with voice samples. The voice control panel is available at http://server-address:9898/dashboard. Only .wav files are supported.</br>

Below is a table with supported languages:

| Language | Language code |
|:------------------------:|:---------:|
| German | `de` |
| English (British)* | `en_GB` |
| English (USA)* | `en_US` |
| French | `fr` |
| Italian | `it` |
| Russian | `ru` |
| Turkish | `tr` |
*Within this project, `en_GB` and `en_US` are no different, this is done to support integration with the Mary TTS API.

At the moment, the server is only compatible with the Mary TTS API (if I can find time in my life
to refine it, maybe someday I can add support for [Wyoming Protocol]).<br>

<a id="start-recommendation"></a>
## Startup recommendations

The Docker container needs about 6gb of RAM to work, and a graphics adapter with VRAM of at least 4gb is <b>required</b> 
(I personally tested on RTX3060).
The server will not run on the CPU.</br>
For a quick start, see [server installation](#server-install) and [configuration in Home Assistant](#ha-configure)

Check operability via CURL:
```commandline
curl -d "VOICE=your_voice_name&LOCALE=ru&INPUT_TEXT=Это тест речи!" -X POST http://localhost:9898/process --output test.wav
```

### Performance
In most cases, the speed on Nvidia RTX 3060 is, on average, 2 seconds for text ~100 characters.<br>
[Declared speed from the Auralis engine]

<a id="server-install"></a>
## Server installation

### Installation via Docker:
Execute the command:
```commandline
docker run -p 9898:9898 --gpus all --name hax-tts-service -d alekst7/haxtts-service:latest
```
With additional parameters:
```commandline
docker run -p 9898:9898 --gpus all --name hax-tts-service -e BASE_MODEL="AstraMindAI/xttsv2" -e GPT_MODEL="AstraMindAI/xtts2-gpt" -e MAX_TEXT_PARTS_COUNT=4 -d alekst7/haxtts-service:latest
```

### Installation via Docker Compose:
Create a `docker-compose.yml` file and transfer the contents to it:
```yaml
version: '1'

services:
  hax-tts-service:
    image: "alekst7/haxtts-service:latest"
    container_name: "hax-tts-service"
    ports:
      - "9898:9898"
    restart: unless-stopped
    runtime: nvidia
    deploy:
      resources:
        limits:
          memory: 6G
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
# You can use custom parameters here
#     environment:
#       CURRENT_MODEL: "AstraMindAI/xttsv2"
#       CURRENT_MODEL_GPT: "AstraMindAI/xtts2-gpt"
#       MAX_TEXT_PARTS_COUNT: 8
```
Execute the command:
```commandline
docker compose up
```

<a id="server-configure"></a>
## Server configuration
All server configuration parameters are passed as environment parameters to the docker container at startup.

Automatic language detection `AUTO_DETECT_LANGUAGE`:
```yaml
AUTO_DETECT_LANGUAGE: False
```
Default: `False`<br>
Whether the language will be detected automatically. If this function is enabled, the language specified in the `GET` and `POST` requests to the `/process` endpoint will be ignored, and the system will try to determine the language itself.<br>
This function is good if the text contains different languages, and you need to maintain individual pronunciation for each language. This function may not work very well, so it is disabled by default.</br>
<br>

Removing the dot at the end of the text `REMOVE_DOTS_AT_THE_END`:
```yaml
REMOVE_DOTS_AT_THE_END: ru
```
Default: `True`<br>
A parameter that specifies whether to remove dots at the end of the text. I noticed that in most XTTSv2 models, artifacts (exclamations, mumbling, exclamations) can be heard at the end of the speech if the text ends with a dot.</br>
A good solution was to introduce a function that simply removes the dot at the end of the text going to the speech synthesizer.
It is worth paying attention to the fact that the parameter removes the dot <b>not</b> at the end of sentences, but <b>only at the end of the text</b> that will go to the
speech synthesizer.</br>
<br>

Voice acting errors `VOICE_TTS_ERRORS`:
```yaml
VOICE_TTS_ERRORS: True
```
Default: `True`<br>
If the parameter is `True`, then if an error occurs during speech synthesis, the server will send an HTTP response with code 200. Which will contain an audio file with the voiced text about the error.</br>
If `False`, the server will return an HTTP response with code 400 during an error.</br>
<br>

Base XTTSv2 model `BASE_MODEL`:
```yaml
BASE_MODEL: "AstraMindAI/xttsv2"
```
Default: `AstraMindAI/xttsv2`</br>
Base XTTSv2 model. The value should be a link to the model from Hugging Face in the format `Author/model`.
The model will be downloaded automatically at startup.</br>
This parameter is required to be used together with the `GPT_MODEL` parameter.</br>
Link to the official base XTTS model from Auralis: https://huggingface.co/AstraMindAI/xttsv2</br>
<br>

GPT-component XTTSv2 `GPT_MODEL`:
```yaml
GPT_MODEL: "AstraMindAI/xtts2-gpt"
```
Default: `AstraMindAI/xtts2-gpt`</br>
GPT-component of the XTTSv2 model. The value should be a link to the model from Hugging Face in the format `Author/model`.
The model will be downloaded automatically at startup.</br>
Link to the official base GPT-model XTTS from Auralis: https://huggingface.co/AstraMindAI/xtts2-gpt</br>
<br>

Parallelism `MAX_TEXT_PARTS_COUNT`:
```yaml
MAX_TEXT_PARTS_COUNT: 32
```
Default: `32`</br>
Reducing this value will save video memory, increasing it will reduce the synthesis time on large texts</b>.
The default is the optimal value, selected empirically.<br>
For performance, the server can synthesize speech in parallel in several threads.
This is ensured by dividing a large text into separate parts.</br>
The `MAX_TEXT_PARTS_COUNT` parameter limits the maximum number of text parts.
If the parameter specifies the number 8, then the text, for example, consisting of 15 sentences, will be divided into 8 parts, where 7 parts will have 2 sentences each,
and the last part will have one sentence. Accordingly, the text will be synthesized in eight threads. As a result, there will be 8 audio files, which will
combine into one output audio.
</br>

Sentence splitting `SPLIT_BY_SENTENCES`:
```yaml
SPLIT_BY_SENTENCES: False
```
Default: `False`</br>
Determines whether the text will be split into complete sentences or simply by delimiters during parallel speech synthesis.
The text delimiters are the following characters: `;:,.!?`.</br>
If the function is disabled `False`, the text will be split by delimiters, which guarantees an even greater increase in performance
than when splitting into complete sentences, but there is also a chance that sometimes the TTS model may put the wrong intonation where there are commas
or other punctuation marks, this is not very critical. In general, I advise disabling sentence splitting.
</br>

Sampling rate `SAMPLE_RATE`:
```yaml
SAMPLE_RATE: 16000
```
Default: `16000`</br>
Sets the sampling rate of the `load_sample_rate` parameter in the Auralis engine.
It seems that this should affect the quality of the output sound, but I did not notice the difference between 16000 and 48000.
But the output at 16000 works faster on average by 0.5-1 seconds.</br>
Let this parameter just be in case.
</br>

<a id="ha-configure"></a>
## Configuration in Home Assistant
In the `configuration.yaml` file, add the entry:
```yaml
tts:
  - platform: marytts
    host: localhost # IP address of the server
    port: 9898
    codec: WAVE_FILE
    voice: xenia # The name of the voice you want to use.
    language: ru # The model is multilingual, it only affects the pronunciation accent.
```

<a id="rhasspy-configure"></a>
## Configuration in Rhasspy Assistant
1) In the settings, in the Text to Speech section. Select the MarryTTS module.
2) Apply the Rhasspy Assistant settings (it will reboot).
3) Specify the address of your server with the path `/process`.
4) Click on the Refresh button.
5) In the list of available voices, select the voice you need.
6) Apply the Rhasspy Assistant settings (it will reboot).

![RhasspyConfig]

<a id="bluetooth-speaker"></a>
## Output sound to a Bluetooth speaker

1) If Home Assistant is the main OS (HAOS), then read this documentation [TTS Bluetooth Speaker for Home Assistant]
2) If Home Assistant is on Debian, then do the following:

Edit client.conf

```commandline
nano /etc/pulse/client.conf
```

Add the following:

```commandline
default-server = unix:/usr/share/hassio/audio/external/pulse.sock
autospawn = no
```

![ClientConf]

Restart pulseaudio.

```commandline
pulseaudio -k && pulseaudio --start
```

Install the addon [Mopidy 2.1.1] and install only this version. Do not install Mopidy 2.2.0 - it is broken. Read more about the broken version of Mopidy 2.2.0 [here].

Add to configuration.yaml
```yaml
media_player:
  - platform: mpd
    name: "MPD Mopidy"
    host: localhost
    port: 6600
```

Reboot Home Assistant completely so that Debian itself reboots.

![RebootHa]

Connect the bluetooth speaker to Debian, either through the GUI, or through the console using the bluetoothctl command

Enable bluetooth:

```commandline
power on
```

Start scanning for devices:

```commandline
scan on
```

Once you see your device, pair with the device:

```commandline
pair [mac address of the device]
```

Connect to the device:

```commandline
connect [mac address of the device]
```

Add the device to trusted:

```commandline
trust [mac address of the device]
```

Next, once the bluetooth device is added, you need to specify the sound output source of the bluetooth device in the two addons Rhasspy Assistant and Mopidy:

1) In Rhasspy Assistant, specify it like this:

![RhasspyAssistantConfig]

2) In Mopidy, specify it like this:

![MopidyConfig]

Check operability:

![TtsSay]

Code:

```yaml
service: tts.marytts_say
data:
  entity_id: media_player.mpd_mopidy
  message: >-
    After 15 years, the life of Jean-Luc Picard, who once roamed the cosmic expanses
```

<a id="finetune"></a>
## Fintune models

The server supports finetune models. To fine-tune your model, you can use
[this tool], or some other tools available for these purposes.<br>
After a working XTTSv2 model has been obtained, it must be converted to the Auralis format.
To do this, use [this script] (it is also duplicated in my project):
```commandline
python checkpoint_converter.py path/to/checkpoint.pth --output_dir path/to/output
```
The script will create two folders, one with the XTTSv2 core checkpoint and one with the gpt2 component.
Then these models can be uploaded to Hugging Face and used.</br>
Local launch of models is not yet supported.

<a id="api"></a>
## API

### Mary TTS Compatible

- `GET` `/clear_cache` - Calls GC inside the application.
- `GET` `/settings` - Returns the current server settings.
- `GET` `/voices` - Returns a string of the list of available voices (names of .wav files).
- `GET` `/process?VOICE=[Selected voice]&INPUT_TEXT=[Text to process]` - Returns an audio file of synthesized speech.
- `POST` `/process` in the request body `VOICE=[Selected voice]`, `INPUT_TEXT=[Text to process]` - Returns an audio file of synthesized speech.

### Voice Management

- `GET` `/available-voices` - Returns a json object with a list of available voices (names of .wav files).
- `POST` `/upload` - Uploads a .wav file with a voice sample to the server.
- `DELETE` `/files/{filename}` - Deletes a .wav file with a voice sample from the server.
- `GET` `/files/{filename}` - Returns a .wav file with a voice sample from the server for further playback.

<a id="development"></a>
## Development

For development and testing under Windows, you need to use WSL.</br>
Debian distribution is suitable, because Ubuntu may have an error when installing the `EbookLib`, `ffmpeg`, `langid`, `docopt` and `jaconv` packages.
Installing the auralis package can take a very long time, more than an hour, so be prepared, this is normal.
The whole problem is related to the Triton package used in Auralis. It cannot be run under Windows.</br>
The code is written using Python 3.10

[amd64-badge]: https://img.shields.io/badge/amd64-yes-green
[nvidia-badge]: https://img.shields.io/badge/nvidia-yes-green
[license-shield]: https://img.shields.io/badge/license-MIT-green

[license-url]: ./LICENSE

[Coqui]: https://github.com/coqui-ai/TTS
[fork]: https://github.com/idiap/coqui-ai-TTS
[Auralis]: https://github.com/astramind-ai/Auralis
[XTTSv2]: https://huggingface.co/coqui/XTTS-v2
[Wyoming Protocol]: https://www.home-assistant.io/integrations/wyoming/

[RhasspyConfig]: /docs/RhasspyConfig.png

[TTS Bluetooth Speaker for Home Assistant]: https://github.com/pkozul/ha-tts-bluetooth-speaker

[ClientConf]: /docs/ClientConf.png

[Mopidy 2.1.1]: https://github.com/Llntrvr/Hassio-Addons
[here]: https://github.com/Poeschl/Hassio-Addons/issues/334
[Declared speed from the Auralis engine]: https://github.com/astramind-ai/Auralis#:~:text=Convert%20the%20entire%20first%20Harry%20Potter%20book%20to%20speech%20in%2010%20minutes%20(realtime%20factor%20of%20%E2%89%88%200.02x!%20)
[this tool]: https://github.com/daswer123/xtts-finetune-webui
[this script]: https://github.com/astramind-ai/Auralis/blob/main/src/auralis/models/xttsv2/utils/checkpoint_converter.py

[RebootHa]: /docs/RebootHa.png

[RhasspyAssistantConfig]: /docs/RhasspyAssistantConfig.png
[MopidyConfig]: /docs/MopidyConfig.png
[TtsSay]: /docs/TtsSay.png
[Logo]: /docs/HaxTTSLogo.png
