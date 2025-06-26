![Supports amd64 Architecture][amd64-badge]
![Supports by nvidia gpu][nvidia-badge]
[![MIT License][license-shield]][license-url]

# HAxTTS Server

[![en](https://img.shields.io/badge/lang-en-red.svg)](./README.md)

## Содержание
- [О проекте](#about)
- [Рекомендации к запуску](#start-recommendation)
- [Установка сервера](#server-install)
- [Конфигурация сервера](#server-configure)
- [Настройка в Home Assistant](#ha-configure)
- [Настройка в Rhasspy](#rhasspy-configure)
- [Вывод звука на Bluetooth колонку](#bluetooth-speaker)
- [Кастомные модели](#finetune)
- [API](#api)
- [Разработка](#development)

<a id="about"></a>
## О проекте

![Logo]
Hax-TTS это Mary TTS совместимый сервер для синтеза речи с поддержкой моделей XTTSv2. 
Этот проект нацелен на то, чтобы обеспечить в ваш Home Assistant качественным синтезом речи.</br>
Сервер работает на основе моделей [XTTSv2] от [Coqui] (поддержка прекращена, рабочий [форк] от idiap). 
В качестве бэкенда для инференса моделей используется очень крутой проект - [Auralis].</br>
Сервер поддерживает параллельные вычисления для ускорения синтеза речи на больших объемах текста. 
Так же поддерживаются предобученные пользовательские модели (пока что только ссылками на Hugging Face).</br>

Сами модели являются мультиязычными, поэтому выбор языка в интеграции Mary TTS влияет только на акцент при произношении речи.
Так же модели поддерживают клонирование любых голосов (как мужских, так и женских).</br>
Для выбора голоса необходимо установить в значение параметра `voice`, в конфигурации Mary TTS название wav файла с примером записанного голоса, см. [Настройка в Home Assistant](#ha-configure).
Так же имеется возможность добавлять или удалять собственные wav файлы с примерами голосов. Панель управления голосами доступна по http://server-address:9898/dashboard. Поддерживаются только .wav файлы.</br>

Ниже приведена таблица с поддерживаемыми языками:

|           Язык           | Код языка |
|:------------------------:|:---------:|
|         Немецкий         |   `de`    |
| Английский (Британский)* |   `en_GB`    |
|    Английский (США)*     |   `en_US`    |
|       Французский        |   `fr`    |
|       Итальянский        |   `it`    |
|         Русский          |   `ru`    |
|         Турецкий         |   `tr`    |
*В рамках этого проекта `en_GB` и `en_US` ничем не отличаются, это сделано для поддержки интеграции с API Mary TTS.

На данный момент сервер имеет совместимость только с API Mary TTS (если я смогу найти время в своей жизни 
на доработку, возможно когда-то я смогу добавить поддержку [Wyoming Protocol]).<br>

<a id="start-recommendation"></a>
## Рекомендации к запуску

Docker контейнеру нужно около 6gb RAM для работы, так же <b>обязательно</b> нужен графический адаптер с VRAM не меньше 4gb
(лично я тестировал на RTX3060).
На CPU сервер не запустится.</br>
Для быстрого старта смотри [установка сервера](#server-install) и [настройка в Home Assistant](#ha-configure)

Проверка работоспособности через CURL:
```commandline
curl -d "VOICE=your_voice_name&LOCALE=ru&INPUT_TEXT=Это тест речи!" -X POST http://localhost:9898/process --output test.wav
```

### Производительльность
В большинстве случаев скорость на Nvidia RTX 3060 составляет, в среднем, 2 секунды для текста ~100 символов.<br>
[Заявленная скорость от движка Auralis]

<a id="server-install"></a>
## Установка сервера

### Установка через Docker:
Выполните команду:
```commandline
docker run -p 9898:9898 --gpus all --name hax-tts-service -d alekst7/haxtts-service:latest
```
С дополнительными параметрами:
```commandline
docker run -p 9898:9898 --gpus all --name hax-tts-service -e BASE_MODEL="AstraMindAI/xttsv2" -e GPT_MODEL="AstraMindAI/xtts2-gpt" -e MAX_TEXT_PARTS_COUNT=4 -d alekst7/haxtts-service:latest
```

### Установка через Docker Compose:
Создайте файл `docker-compose.yml` и перенесите в него содержимое:
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
Выполните команду:
```commandline
docker compose up
```


<a id="server-configure"></a>
## Конфигурация сервера
Все параметры конфигурации сервера передаются как параметры окружения docker контейнеру при запуске.

Автоматическое определение языка `AUTO_DETECT_LANGUAGE`:
```yaml
AUTO_DETECT_LANGUAGE: False 
```
По умолчанию: `False`<br>
Будет ли язык определяться автоматически. Если эта функция включена, то указанный язык в `GET` и `POST` запросах на эндпоинт `/process` будет игнорироваться, а система попытается определить язык самостоятельно.<br>
Эта функция хороша в случае, если в тексте присутствуют разные языки, и вам нужно сохранить индивидуальное произношение для каждого языка. Эта функция может не очень хорошо работать, поэтому по умолчанию она отключена.</br>
<br>

Удаление точки в конце текста `REMOVE_DOTS_AT_THE_END`:
```yaml
REMOVE_DOTS_AT_THE_END: ru
```
По умолчанию: `True`<br>
Параметр, который указывает, стоит ли удалять точки в конце текста. Я заметил, что в большинстве моделей XTTSv2 могут быть слышны артефакты (возгласы, мычания, восклицания) в конце речи, если текст оканчивается на точку.</br>
Хорошим решением было ввести функцию, которая просто удаляет точку в конце текста, идущего в речевой синтезатор.
Стоит обратить внимание, параметр удаляет точку <b>не</b> в конце предложений, а <b>только в конце текста</b>, который пойдёт в 
синтезатор речи.</br>
<br>

Озвучка ошибок `VOICE_TTS_ERRORS`:
```yaml
VOICE_TTS_ERRORS: True 
```
По умолчанию: `True`<br>
Если параметр имеет значение `True`, то при возникновении ошибки во время синтеза речи, сервер отправит HTTP ответ с кодом 200. В котором будет содержаться аудиофайл с озвученном текстом о том, что произошла ошибка.</br>
При значении `False`, сервер во время ошибки вернёт HTTP ответ с кодом 400.</br>
<br>

Базовая XTTSv2 модель `BASE_MODEL`:
```yaml
BASE_MODEL: "AstraMindAI/xttsv2"
```
По умолчанию: `AstraMindAI/xttsv2`</br>
Базовая модель XTTSv2. В качестве значения должна передаваться ссылка на модель с Hugging Face в формате `Автор/модель`. 
Модель автоматически скачается при запуске.</br>
Параметр обязателен к использованию вместе с параметром `GPT_MODEL`.</br>
Ссылка на официальную базовую модель XTTS от Auralis: https://huggingface.co/AstraMindAI/xttsv2</br>
<br>

GPT-компонент XTTSv2 `GPT_MODEL`:
```yaml
GPT_MODEL: "AstraMindAI/xtts2-gpt"
```
По умолчанию: `AstraMindAI/xtts2-gpt`</br>
GPT-компонент модели XTTSv2. В качестве значения должна передаваться ссылка на модель с Hugging Face в формате `Автор/модель`. 
Модель автоматически скачается при запуске.</br>
Ссылка на официальную базовую GPT-модель XTTS от Auralis: https://huggingface.co/AstraMindAI/xtts2-gpt</br>
<br>

Параллелизм `MAX_TEXT_PARTS_COUNT`:
```yaml
MAX_TEXT_PARTS_COUNT: 32
```
По умолчанию: `32`</br>
Уменьшение этого значения, позволит сэкономить видеопамять, увеличение позволит сократить время синтеза на больших текстах</b>.
По умолчанию задано оптимальное значение, подобранное опытным путём.<br>
Для быстродействия сервер умеет параллельно синтезировать речь в нескольких потоках.
Это обеспечивается путём разбиения большого текста на отдельные части.</br>
Параметр `MAX_TEXT_PARTS_COUNT` ограничивает максимальное количество частей текста.
Если в параметре будет указано число 8, то текст, например, состоящий из 15 предложений, разобьётся на 8 частей, где 7 частей будут иметь по 2 предложения, 
а последняя часть одно предложение. Соответственно текст будет синтезирован в восьми потоках. По итогу будет 8 аудио, которые
совместятся в одно выходное аудио.
</br>

Разбитие на предложения `SPLIT_BY_SENTENCES`:
```yaml
SPLIT_BY_SENTENCES: False
```
По умолчанию: `False`</br>
Определяет будет ли делиться текст по цельным предложениям, или просто по разделителям во время параллельного синтеза речи.
Разделителями текста являются следующие символы: `;:,.!?`.</br>
Если функция отключена `False`, текст будет делиться по разделителям, это гарантирует ещё больший прирост производительности,
чем при разделении на цельные предложения, но так же есть шанс, что иногда TTS-модель может ставить неверную интонацию, где есть запятые
или другие знаки препинания, это не очень критично. В целом, советую отключать разделение по предложениям.
</br>

Частота дискретизации `SAMPLE_RATE`:
```yaml
SAMPLE_RATE: 16000
```
По умолчанию: `16000`</br>
Задаёт частоту дискретизации параметра `load_sample_rate` в движке Auralis. 
Кажется, это должно влиять на качество выходного звука, но разницы между 16000 и 48000 я не заметил.
Зато вывод при 16000 работает быстрее в среднем на 0.5-1 секунду.</br>
Пусть этот параметр будет просто на всякий случай.
</br>

<a id="ha-configure"></a>
## Настройка в Home Assistant
В файле `configuration.yaml` добавьте запись:
```yaml
tts:
  - platform: marytts
    host: localhost # IP-адрес сервера
    port: 9898
    codec: WAVE_FILE
    voice: xenia # Имя голоса который хотите использовать.
    language: ru # Модель мультиязычная, влияет только на акцент произношения.
```

<a id="rhasspy-configure"></a>
## Настройка в Rhasspy Assistant
1) В настройках, в разделе Text to Speech. Выберете модуль MarryTTS.
2) Примените настройки  Rhasspy Assistant (он перезагрузится).
3) Укажите адрес вашего сервера с путём `/process`.
4) Нажмите на кнопку Refresh.
5) В списке доступных голосов, выберите голос который вам нужен.
6) Примените настройки  Rhasspy Assistant (он перезагрузится).

![RhasspyConfig]

<a id="bluetooth-speaker"></a>
## Вывод звука на Bluetooth колонку

1) Если Home Assistant как основная ОС (HAOS), то читаем эту документацию [TTS Bluetooth Speaker for Home Assistant]
2) Если Home Assistant стоит на Debian, то делаем следующее:

Отредактируем client.conf

```commandline
nano /etc/pulse/client.conf
```

Добавим следующее:

```commandline
default-server = unix:/usr/share/hassio/audio/external/pulse.sock
autospawn = no
```

![ClientConf]

Перезапускаем pulseaudio.

```commandline
pulseaudio -k && pulseaudio --start
```

Ставим аддон [Mopidy 2.1.1] и ставим только эту версию. Mopidy 2.2.0 не ставить - она сломанная. Подробнее про поломанную версию Mopidy 2.2.0 читать [здесь].

Добавляем в configuration.yaml
```yaml
media_player:
  - platform: mpd
    name: "MPD Mopidy"
    host: localhost
    port: 6600
```

Перезагружаем Home Assistant полностью, чтобы перезагрузился сам Debian.

![RebootHa]

Подключаем bluetooth колонку к Debian, kb,j через GUI, либо через консоль используя команду bluetoothctl

Включим bluetooth:

```commandline
power on
```

Запуск сканирования девайсов:

```commandline
scan on
```

Как увидели свой девайс, спариваемся с устройством:

```commandline
pair [mac адрес девайса]
```

Подключаемся к устройству:

```commandline
connect [mac адрес девайса]
```

Добавляем устройство в доверенные:

```commandline
trust [mac адрес девайса]
```

Далее, как добавлен bluetooth девайс то в двух аддонов Rhasspy Assistant и Mopidy нужно указать источник вывода звука bluetooth девайса:

1) В Rhasspy Assistant указываем так:

![RhasspyAssistantConfig]

2) В Mopidy указываем так:

![MopidyConfig]


Проверяем работоспособность:

![TtsSay]

Код: 

```yaml
service: tts.marytts_say
data:
  entity_id: media_player.mpd_mopidy
  message: >-
    Спустя 15 лет жизнь некогда бороздившего космические просторы Жана-Люка
    Пикара
```

<a id="finetune"></a>
## Кастомные модели

Сервер поддерживает finetune-модели. Для того чтобы дообучить свою модель, можно использовать 
[этот инструмент], или какие-то другие инструменты, доступные для этих целей.<br>
После того, как была получена работающая XTTSv2 модель, её необходимо сконвертировать в формат Auralis.
Для этого используйте [этот скрипт] (он так же продублирован в моём проекте):
```commandline
python checkpoint_converter.py path/to/checkpoint.pth --output_dir path/to/output
```
Скрипт создаст две папки, одну с контрольной точкой ядра XTTSv2 и одну с компонентом gpt2. 
Затем эти модели можно загрузить на Hugging Face и использовать.</br>
Локальный запуск моделей пока не поддерживается.

<a id="api"></a>
## API

###  Совместимые с Mary TTS 

- `GET` `/clear_cache` - Вызывает GC внутри приложения.
- `GET` `/settings` - Возвращает текущие настройки сервера.
- `GET` `/voices` - Возвращает строкой список доступных голосов (названия .wav файлов).
- `GET` `/process?VOICE=[Выбраный голос]&INPUT_TEXT=[Текст для обработки]` - Возвращает аудио файл синтезированной речи.
- `POST` `/process` в теле запроса `VOICE=[Выбраный голос]`, `INPUT_TEXT=[Текст для обработки]` - Возвращает аудио файл синтезированной речи.

###  Управление голосами

- `GET` `/available-voices` - Возвращает json объектом список доступных голосов (названия .wav файлов).
- `POST` `/upload` - Загружает .wav файл с примером голоса на сервер.
- `DELETE` `/files/{filename}` - Удаляет .wav файл с примером голоса на сервере.
- `GET` `/files/{filename}` - Отдаёт .wav файл с примером голоса с сервера для дальнейшего проигрывания.

<a id="development"></a>
## Разработка

Для разработки и тестирования из под Windows необходимо использовать WSL.</br>
Подойдёт дистрибутив Debian, т.к. на Ubuntu может возникать ошибка установки пакетов `EbookLib`, `ffmpeg`, `langid`, `docopt` и `jaconv`.
Установка пакета auralis может занимать очень много времени, больше часа, так что, будьте готовы, это нормально. 
Вся мишура связана с пакетом Triton, используемым в Auralis. Он не может запускаться из под Windows.</br>
Код написан с использованием Python 3.10

[amd64-badge]: https://img.shields.io/badge/amd64-yes-green
[nvidia-badge]: https://img.shields.io/badge/nvidia-yes-green
[license-shield]: https://img.shields.io/badge/license-MIT-green

[license-url]: ./LICENSE

[Coqui]: https://github.com/coqui-ai/TTS
[форк]: https://github.com/idiap/coqui-ai-TTS
[Auralis]: https://github.com/astramind-ai/Auralis
[XTTSv2]: https://huggingface.co/coqui/XTTS-v2
[Wyoming Protocol]: https://www.home-assistant.io/integrations/wyoming/

[RhasspyConfig]: /docs/RhasspyConfig.png

[TTS Bluetooth Speaker for Home Assistant]: https://github.com/pkozul/ha-tts-bluetooth-speaker

[ClientConf]: /docs/ClientConf.png

[Mopidy 2.1.1]: https://github.com/Llntrvr/Hassio-Addons
[здесь]: https://github.com/Poeschl/Hassio-Addons/issues/334
[Заявленная скорость от движка Auralis]: https://github.com/astramind-ai/Auralis#:~:text=Convert%20the%20entire%20first%20Harry%20Potter%20book%20to%20speech%20in%2010%20minutes%20(realtime%20factor%20of%20%E2%89%88%200.02x!%20)
[этот инструмент]: https://github.com/daswer123/xtts-finetune-webui
[этот скрипт]: https://github.com/astramind-ai/Auralis/blob/main/src/auralis/models/xttsv2/utils/checkpoint_converter.py

[RebootHa]: /docs/RebootHa.png

[RhasspyAssistantConfig]: /docs/RhasspyAssistantConfig.png
[MopidyConfig]: /docs/MopidyConfig.png
[TtsSay]: /docs/TtsSay.png
[Logo]: /docs/HaxTTSLogo.png