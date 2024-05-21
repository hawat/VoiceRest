from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import tempfile
from TTS.api import TTS
import re
from num2words import num2words
from functools import lru_cache
import configparser
from TTS.utils.manage import ModelManager
import os


# Initialize the config parser



app = FastAPI(
    title="voice generator",
    description="This API serves voide in wav files",
    version="1.0.1",
)


class Config(BaseModel):
    languages: dict[str, str]


@lru_cache()
def get_settings():
    cnf = configparser.ConfigParser()
    cnf.read('config.ini')
    langs = dict()
    if 'LANGUAGES' in cnf:
        for llag in cnf['LANGUAGES']:
            if llag.startswith('lang_'):
                langs[llag[5:]] = cnf['LANGUAGES'][llag]
    print(langs)
    ll={'languages':langs}
    return Config(**ll)


def replace_numbers_with_words(text, lang="pl"):
    """Replaces integer and real numbers in a string with their word equivalents."""

    def convert_number(match,lang="pl"):
        number_str = match.group(0)
        if "." in number_str:  # Check for decimal point
            whole_part, decimal_part = number_str.split(".")
            whole_word = num2words(int(whole_part),lang=lang)
            decimal_word = num2words(int(decimal_part), lang=lang)
            return f"{whole_word} koma {decimal_word}"
        else:
            return num2words(int(number_str,),lang="pl")

    pattern = r"-?\d+(\.\d+)?"  # Match integers or decimals, with optional negative sign
    return re.sub(pattern, convert_number, text)


def handle_models():
    model_manager = ModelManager()
    available_models = model_manager.list_models()

    def install_model(model_name):
        print(f"Downloading model '{model_name}'...")
        model_manager.download_model(model_name)
        print("Model downloaded successfully!")

    def check_and_install_model(model_name):
        model_path = model_name  # Model name is the path
        config_path = os.path.join(model_path, "config.json")
        if model_name in available_models:
            print(f"Model '{model_name}' is installed!")
        else:
            install_model(model_name)

    for langs in get_settings().languages.keys():
        print(f"langs: {langs} and {get_settings().languages[langs]}")
        check_and_install_model(get_settings().languages[langs])


# Placeholder function for text-to-speech conversion
def generate_wav_from_text(text: str, temp_file: str,lang="pl"):
    print("generate_wav_from_text")
    """Replace this with your actual text-to-speech conversion logic"""
    # Example: You might use libraries like pyttsx3, gTTS, etc.
    tts = TTS(model_name=get_settings().languages[lang],
              gpu=False)  # Set gpu to True if you have a GPU

    # Synthesize speech
    tx = replace_numbers_with_words(text,lang)
    print(tx)
    tts.tts_to_file(text=tx, file_path=temp_file)

# Input model for request validation (optional, for stricter input control)
class TextToSpeechInput(BaseModel):
    text: str
    filename: Optional[str] = "audio.wav"  # Default filename
    '''lang: Optional[str] = get_settings().languages[list(get_settings().languages.keys())[0]]'''
    lang: Optional[str] = get_settings().languages[next(iter(get_settings().languages))]

@app.post("/voice/")
async def text_to_wav(input_data: TextToSpeechInput):
    print("post")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_filepath = temp_file.name
        print(temp_filepath)
        print(temp_file)
        generate_wav_from_text(input_data.text, temp_filepath)
    headers = {"Content-Disposition": f"attachment; filename={input_data.filename}"}
    return FileResponse(temp_filepath, media_type="audio/wav", headers=headers)

@app.get("/voice/")
async def text_to_wav(input_data: TextToSpeechInput):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_filepath = temp_file.name
        generate_wav_from_text(input_data.text, temp_filepath)
    headers = {"Content-Disposition": f"attachment; filename={input_data.filename}"}
    return FileResponse(temp_filepath, media_type="audio/wav", headers=headers)

@app.get("/get_langs")
def get_data_custom():
    return JSONResponse(content=get_settings().languages, status_code=200)

@app.on_event("startup")
async def startup_event():
    conf = get_settings()
    print("______________")
    print(conf)
    print("______________")
    handle_models()
    print("______________")