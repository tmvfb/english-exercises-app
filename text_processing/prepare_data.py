#!/usr/bin/env python3

import json
import os
import random

from sentence_splitter import SentenceSplitter

from .exercises import (
    blanks_exercise,
    multiple_choice_exercise,
    type_in_exercise,
    word_order_exercise,
)


def load_data(filepath: str, username: str) -> list:
    """
    Parsed data is stored in a json file under "path" filepath.
    It is assigned a {username}.json name for uniqueness.
    Every user has 2 associated files: original and jsonified.
    """

    path, _ = os.path.split(filepath)
    path = path + "/" + username + ".json"

    try:
        with open(path, "r") as file:
            sentences = json.load(file)
    except FileNotFoundError:
        with open(filepath, "r") as file:
            text = file.read()

        splitter = SentenceSplitter(language="en")
        sentences = splitter.split(text)
        with open(path, "w") as f:
            f.write(json.dumps(sentences))

    return sentences


def remove_data(filepath: str, username: str, **kwargs):
    path, _ = os.path.split(filepath)
    path = path + "/" + username + ".json"
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def prepare_exercises(filepath: str, **kwargs) -> dict:
    """
    Dispatcher function to call corresponding exercise generator.
    """

    sentences = load_data(filepath, str(kwargs.get("user")))
    e_type = kwargs.get("exercise_type")
    pos = kwargs.get("pos")
    length = kwargs.get("length")
    skip_length = kwargs.get("skip_length", 3)

    if e_type == "all_choices":
        e_type = random.choice(["type_in", "multiple_choice", "word_order", "blanks"])
        kwargs["exercise_type"] = e_type

    if e_type == "type_in":
        correct_answer, begin, end = type_in_exercise(sentences, pos, length)
        options = None
    elif e_type == "multiple_choice":
        correct_answer, begin, end, options = multiple_choice_exercise(
            sentences, pos, length
        )
    elif e_type == "word_order":
        correct_answer, begin, end, options = word_order_exercise(
            sentences, pos, length, skip_length
        )
    elif e_type == "blanks":
        correct_answer, begin, end, options = blanks_exercise(
            sentences, pos, length, skip_length
        )

    kwargs["correct_answer"] = correct_answer
    kwargs["options"] = options
    kwargs["begin"] = begin
    kwargs["end"] = end
    # kwargs should have correct answer and task sentence (begin + end)
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
