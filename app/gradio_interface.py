import shutil

import gradio as gr
import os
from app.config import speakers_directory, settings, scan_files_for_names, voice_extension


def delete_file(filename):
    file_path = os.path.join(speakers_directory, filename + voice_extension)

    if os.path.exists(file_path):
        os.remove(file_path)
        gr.Info(f"File '{filename}' successfully removed.")
    else:
        gr.Info(f"Error: file '{filename}' not found.")


def save_file(file: str):
    if not file.endswith(voice_extension):
        gr.Info(f"Error: Please upload a file with extension {voice_extension}")
        return
    destination = os.path.join(speakers_directory, os.path.basename(file))
    shutil.move(file, destination)

    gr.Info(f"File '{file}' successfully uploaded to '{speakers_directory}'")


def update_file_list():
    settings.xtts_speakers = scan_files_for_names(speakers_directory, voice_extension)
    return settings.xtts_speakers


with gr.Blocks() as demo:

    # Speakers list
    text_box = gr.Textbox(label=f"Available speakers", value = settings.xtts_speakers, scale=5, interactive=False)

    # Speakers removing
    delete_filename = gr.Dropdown(label="Choose file to remove", choices=settings.xtts_speakers, interactive=True)

    # Speakers upload
    gr.Interface(
        fn=lambda filename: (save_file(filename), update_file_list()),
        inputs=gr.File(label=f"Example: female_speaker{voice_extension}"),
        outputs=[text_box, delete_filename],
        delete_cache=(86400, 86400),
        title="Uploading speaker file",
        description=f"Upload a {voice_extension} file and it will be saved to the '{speakers_directory}' folder. "
                    "The file name must not contain spaces."
    )

    delete_button = gr.Button("Remove file")
    delete_button.click(
        fn=lambda filename: (delete_file(filename), update_file_list()),
        inputs=delete_filename,
        outputs=[text_box, delete_filename]
    )


demo.launch()