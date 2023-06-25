import random
import re
import os
import json
from sentence_splitter import SentenceSplitter
# import gensim.downloader
# import spacy
# import spacy.cli
# spacy.cli.download("en_core_web_sm")
# nlp = spacy.load("en_core_web_sm")


def load_data(filepath: str, username: str) -> list:
    # parsed data is stored in a json file under "path" filepath
    # it is assigned a {username}.json name for uniqueness
    # every user has 2 associated files: original and jsonified
    path, _ = os.path.split(filepath)
    path = path + "/" + username + ".json"

    try:
        with open(path, "r") as file:
            sentences = json.load(file)

    except FileNotFoundError:
        with open(filepath, "r") as file:
            text = file.read()

        splitter = SentenceSplitter(language='en')
        sentences = splitter.split(text)
        with open(path, "w") as f:
            f.write(json.dumps(sentences))

    return sentences


def remove_data(filepath: str, username: str):
    path, _ = os.path.split(filepath)
    path = path + "/" + username + ".json"
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def prepare_exercises(filepath: str, **kwargs) -> dict:
    sentences = load_data(filepath, str(kwargs.get("user")))
    correct_answer, begin, end = type_in_exercise(sentences)

    kwargs["correct_answer"] = correct_answer
    kwargs["sentence"] = [begin, end]
    # kwargs should have correct answer and task sentence
    return kwargs


def type_in_exercise(sentences: list) -> tuple:

    while True:
        rng_sentence = random.randint(0, len(sentences)-1)
        sentence = sentences[rng_sentence].split(" ")
        if len(sentence) > 3:  # take context into consideration
            break

    rng = random.randint(1, len(sentence)-2)  # exclude 1st and last
    correct_answer = sentence[rng]
    correct_answer = re.sub(r"[^A-Za-z]", "", correct_answer)
    print(rng, correct_answer)

    begin = " ".join(sentence[:rng])
    end = " ".join(sentence[rng+1:])
    print(begin, end)
    return (correct_answer, begin, end)


if __name__ == "__main__":
    filepath = "/home/tmvfb/english-exercises-app/media/Little_Red_Cap__Jacob_and_Wilhelm_Grimm.txt",  # noqa: E501
    username = "me"
    prepare_exercises(filepath, username)
    remove_data(filepath, username)
