#!/usr/bin/env python3

import json
import os
import random
from pathlib import Path
from typing import List

import requests
from dotenv import load_dotenv
from sentence_splitter import SentenceSplitter

from .exercises import (
    blanks_exercise,
    multiple_choice_exercise,
    type_in_exercise,
    word_order_exercise,
)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv()
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech"

# key names should be compatible with MemoryForm from exercises module
EXERCISES = {
    "type_in": type_in_exercise,
    "multiple_choice": multiple_choice_exercise,
    "word_order": word_order_exercise,
    "blanks": blanks_exercise,
}


def get_filepath(filepath: str, username: str, extension: str = ".json"):
    path, _ = os.path.split(filepath)
    path = path + "/" + username + extension
    return path


def load_data(text_path: str, username: str) -> List[str]:
    """
    Parsed data is stored in a json file under "json_path" filepath.
    It is assigned a {username}.json name for uniqueness.
    Every user has up to 3 associated files: original text, jsonified text, audio.

    Function loads associated user json or creates new json from an uploaded txt.
    Case when no file is uploaded is handled by django backend.
    """

    json_path = get_filepath(text_path, username)

    try:
        with open(json_path, "r") as file:
            sentences = json.load(file)
    except FileNotFoundError:
        with open(text_path, "r") as file:  # read initial text file
            text = file.read()

        splitter = SentenceSplitter(language="en")
        sentences = splitter.split(text)
        with open(json_path, "w") as f:
            f.write(json.dumps(sentences))

    return sentences


def remove_data(text_path: str, username: str):
    """
    Removes json file associated with text file.
    Text file deletion is handled by Django.
    """

    json_path = get_filepath(text_path, username)
    if os.path.exists(json_path):
        os.remove(json_path)


def load_audio(text_path: str, username: str, text_for_audio: str):
    audio_path = get_filepath(text_path, username, extension=".wav")
    if os.path.exists(audio_path):
        os.remove(audio_path)

    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": text_for_audio})
    with open(audio_path, mode="bx") as f:
        f.write(response.content)


def prepare_exercises(filepath: str, **kwargs) -> dict:
    """
    Dispatcher function to call corresponding exercise generator.
    """

    sentences = load_data(filepath, str(kwargs.get("user")))
    e_type = kwargs.get("exercise_type")
    pos = kwargs.get("pos")
    length = kwargs.get("length")
    skip_length = kwargs.get("skip_length", 1)
    if len(sentences) < length:
        raise Exception("Provided text is too short.")

    if e_type == "all_choices":
        e_type = random.choice(list(EXERCISES.keys()))
        kwargs["exercise_type"] = e_type

    correct_answer, begin, end, options = EXERCISES[e_type](
        sentences, pos, length, skip_length
    )

    kwargs["correct_answer"] = correct_answer
    kwargs["begin"] = begin
    kwargs["end"] = end
    kwargs["options"] = options

    return kwargs


if __name__ == "__main__":
    # example script to test module functionality
    filepath = "/home/tmvfb/english-exercises-app/media/Little_Red_Cap__Jacob_and_Wilhelm_Grimm.txt"  # noqa: E501
    kwargs = {
        "pos": "ALL",
        "length": 1,
        "skip_length": 3,
        "exercise_type": "blanks",
    }
    prepare_exercises(filepath, **kwargs)
