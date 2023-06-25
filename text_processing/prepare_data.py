import json
import os
import random
# import gensim.downloader
import spacy
import spacy.cli
from sentence_splitter import SentenceSplitter

if not os.getenv("DEBUG", "False"):  # don't download on dev server
    spacy.cli.download("en_core_web_sm")

nlp = spacy.load("en_core_web_sm")


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
    sentences = load_data(filepath, str(kwargs.get("user")))

    correct_answer, begin, end = type_in_exercise(
        sentences, kwargs.get("pos"), kwargs.get("length")
    )

    kwargs["correct_answer"] = correct_answer
    kwargs["sentence"] = [begin, end]
    # kwargs should have correct answer and task sentence
    return kwargs


def type_in_exercise(sentences: list, pos: list, length: int) -> tuple:
    if len(sentences) < length:
        raise Exception("Provided text is too short.")

    while True:
        rng_sentence = random.randint(0, len(sentences) - length)
        if length == 1:
            sentence = sentences[rng_sentence]
        else:
            sentence = " ".join(sentences[rng_sentence: rng_sentence + length])
        if len(sentence.split(" ")) > 3:  # take context into consideration
            break

    doc = nlp(sentence)
    tokens = [token.text_with_ws for token in doc]

    if "ALL" not in pos:
        selected_tokens = [
            (token.text, token.i) for token in doc if token.pos_ in pos
        ]
        if selected_tokens:
            selected_token = random.choice(selected_tokens)
        # in case sentence doesn't contain desired pos
        else:
            return type_in_exercise(sentences, pos, length)

    else:
        rng = random.randint(1, len(tokens) - 2)  # exclude 1st and last
        selected_token = (tokens[rng], rng)

    # selected_token[0] is the token, selected_token[1] is index
    begin = "".join(tokens[: selected_token[1]])
    end = "".join(tokens[selected_token[1] + 1:])
    correct_answer = selected_token[0]

    print(begin, end)
    return (correct_answer, begin, end)


if __name__ == "__main__":
    filepath = "/home/tmvfb/english-exercises-app/media/Little_Red_Cap__Jacob_and_Wilhelm_Grimm.txt"  # noqa: E501
    kwargs = {"username": "me", "pos": "NOUN", "length": 1}
    prepare_exercises(filepath, **kwargs)
    # remove_data(filepath, **kwargs)
