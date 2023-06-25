import random
import re
import os
import json
from sentence_splitter import SentenceSplitter
# import gensim.downloader
import spacy
# import spacy.cli
# spacy.cli.download("en_core_web_sm")


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


def remove_data(filepath: str, username: str, **kwargs):
    path, _ = os.path.split(filepath)
    path = path + "/" + username + ".json"
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def prepare_exercises(filepath: str, **kwargs) -> dict:
    sentences = load_data(filepath, str(kwargs.get("user")))
    correct_answer, begin, end = type_in_exercise(sentences, kwargs.get("pos"))

    kwargs["correct_answer"] = correct_answer
    kwargs["sentence"] = [begin, end]
    # kwargs should have correct answer and task sentence
    return kwargs


def type_in_exercise(sentences: list, pos: list) -> tuple:

    while True:
        rng_sentence = random.randint(0, len(sentences)-1)
        sentence = sentences[rng_sentence].split(" ")
        if len(sentence) > 3:  # take context into consideration
            break

    if "ALL" not in pos:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(sentences[rng_sentence])
        tokens = [token.text_with_ws for token in doc]
        tokens_with_pos = [(token.text, token.i) for token in doc if token.pos_ in pos]

        try:
            selected_token = random.choice(tokens_with_pos)
        # in case sentence doesn't contain desired pos
        except IndexError:
            return type_in_exercise(sentences, pos)

        # selected_token[0] is the token, selected_token[1] is index
        begin = "".join(tokens[:selected_token[1]])
        end = "".join(tokens[selected_token[1]+1:])
        correct_answer = selected_token[0]

    else:
        rng = random.randint(1, len(sentence)-2)  # exclude 1st and last
        correct_answer = sentence[rng]
        correct_answer = re.sub(r"[^A-Za-z]", "", correct_answer)

        begin = " ".join(sentence[:rng])
        end = " ".join(sentence[rng+1:])

    print(begin, end)
    return (correct_answer, begin, end)


if __name__ == "__main__":
    filepath = "/home/tmvfb/english-exercises-app/media/Little_Red_Cap__Jacob_and_Wilhelm_Grimm.txt"  # noqa: E501
    kwargs = {
        "username": "me",
        "pos": "NOUN"
    }
    prepare_exercises(filepath, **kwargs)
    # remove_data(filepath, **kwargs)
