import json
import os
from dotenv import load_dotenv
import random
import gensim.downloader
import spacy
import lemminflect
import spacy.cli
from sentence_splitter import SentenceSplitter

load_dotenv()
dev = os.getenv("DEBUG", False)

if not dev:  # speed up dev server deploy time
    spacy.cli.download("en_core_web_sm")

nlp = spacy.load("en_core_web_sm")
model = gensim.downloader.load("glove-wiki-gigaword-100")


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
    e_type = kwargs.get("exercise_type")
    pos = kwargs.get("pos")
    length = kwargs.get("length")

    if e_type == "all_choices":
        e_type = random.choice(["type_in", "multiple_choice"])
        kwargs["exercise_type"] = e_type

    if e_type == "type_in":
        correct_answer, begin, end = type_in_exercise(sentences, pos, length)
    elif e_type == "multiple_choice":
        correct_answer, begin, end, options = multiple_choice_exercise(
            sentences, pos, length
        )
        kwargs["options"] = options

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
            sentence = " ".join(sentences[rng_sentence : rng_sentence + length])
        if len(sentence.split(" ")) > 3:  # take context into consideration
            break

    doc = nlp(sentence)
    tokens = [token.text_with_ws for token in doc]

    if "ALL" not in pos:
        selected_tokens = [(token.text, token.i) for token in doc if token.pos_ in pos]
    else:
        selected_tokens = [
            (token.text, token.i) for token in doc if not token.is_punct
        ][1:-1]  # remove 1st and last to prevent undesired behaviour

    if selected_tokens:
        selected_token = random.choice(selected_tokens)
    # in case sentence doesn't contain desired pos
    else:
        return type_in_exercise(sentences, pos, length)

    # selected_token[0] is the token, selected_token[1] is index
    begin = "".join(tokens[: selected_token[1]])
    end = "".join(tokens[selected_token[1] + 1 :])
    correct_answer = selected_token[0]

    print(begin, end)
    return (correct_answer, begin, end)


def multiple_choice_exercise(sentences: list, pos: list, length: int) -> tuple:
    correct_answer, begin, end = type_in_exercise(sentences, pos, length)

    synonyms = model.most_similar(correct_answer.lower().strip())

    # adding some customization
    token = nlp(correct_answer.lower())[0]
    pos_tag = token.pos_
    if pos_tag == "VERB":
        inflect_option = random.choice(["VBG", "VBN", "VBZ"])
        option = token._.inflect(inflect_option)
    elif pos_tag == "ADJ":
        inflect_option = random.choice(["JJR", "JJS", "RB"])
        option = token._.inflect(inflect_option)
    else:
        option = None

    synonyms = [synonym[0] for synonym in synonyms if synonym[0] not in ',.;:!?"']
    if option and option not in synonyms:
        synonyms.insert(0, option)

    if len(synonyms) > 5:
        # options should contain tuples to correctly work with django forms
        subsample = synonyms[:5]  # don't repeat options on same word
        options = random.sample(subsample, 3)
        options = list(zip(options, options))
    else:
        options = [(synonyms[i], synonyms[i]) for i in range(3)]

    # for capitalized words
    if correct_answer == correct_answer.capitalize():
        options = [
            (options[i][0].capitalize(), options[i][0].capitalize()) for i in range(3)
        ]

    options.append((correct_answer, correct_answer))
    random.shuffle(options)

    return (correct_answer, begin, end, options)


if __name__ == "__main__":
    filepath = "/home/tmvfb/english-exercises-app/media/Little_Red_Cap__Jacob_and_Wilhelm_Grimm.txt"  # noqa: E501
    kwargs = {"username": "me", "pos": "NOUN", "length": 1, "exercise_type": "type_in"}
    prepare_exercises(filepath, **kwargs)
    # remove_data(filepath, **kwargs)
