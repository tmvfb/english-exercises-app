import json
import os
import random

import gensim.downloader
import lemminflect
import spacy
import spacy.cli
from dotenv import load_dotenv
from sentence_splitter import SentenceSplitter

load_dotenv()
dev = os.getenv("DEBUG", False)

if not dev:  # speed up dev server deploy time
    spacy.cli.download("en_core_web_sm")

nlp = spacy.load("en_core_web_sm")
model = ""
model = gensim.downloader.load("glove-wiki-gigaword-100")


NUM_SYNONYMS = 5  # [3, 10] - defines quality of synonyms for multichoice
NUM_OPTIONS = 3  # number of options for multichoice exercises, <= SYN_COUNT
inflection_dict = {  # options for inflecting pos
    "VERB": ["VBG", "VBN", "VBZ"],
    "ADJ": ["JJR", "JJS", "RB"],
}


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

    if e_type == "all_choices":
        e_type = random.choice(["type_in", "multiple_choice", "word_order", "blanks"])
        kwargs["exercise_type"] = e_type

    if e_type == "type_in":
        correct_answer, begin, end = type_in_exercise(sentences, pos, length)
    elif e_type == "multiple_choice":
        correct_answer, begin, end, options = multiple_choice_exercise(
            sentences, pos, length
        )
        kwargs["options"] = options
    elif e_type == "word_order":
        skip_length = kwargs.get("skip_length", 3)
        correct_answer, begin, end, options = word_order_exercise(
            sentences, pos, length, skip_length
        )
        kwargs["options"] = options
    elif e_type == "blanks":
        skip_length = kwargs.get("skip_length", 3)
        correct_answer, begin, end, options = blanks_exercise(
            sentences, pos, length, skip_length
        )
        kwargs["options"] = options

    kwargs["correct_answer"] = correct_answer
    kwargs["sentence"] = [begin, end]
    # kwargs should have correct answer and task sentence
    return kwargs


def type_in_exercise(
    sentences: list,
    pos: list,
    length: int,
    skip_length: int = 1,
    multiple_skips: bool = False,
) -> tuple:
    """
    Base function for other exercises.
    Skip length is the count of skipped words for user to fill.
    """

    if len(sentences) < length:
        raise Exception("Provided text is too short.")

    # picking up a sentence long enough
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

    # selecting skipped words
    if "ALL" not in pos:
        selected_tokens = [
            (token.text, token.i) for token in doc if token.pos_ in pos and token.i > 0
        ]
        if skip_length > 1:  # don't select tokens at the very end of the sentence
            selected_tokens = list(
                filter(lambda x: x[1] <= len(tokens) - skip_length, selected_tokens)
            )
    elif len(tokens) > 2 * skip_length:  # restrict to get slice correctly
        selected_tokens = [
            (token.text, token.i) for token in doc if not token.is_punct
        ][
            1:-skip_length
        ]  # by default remove 1st and last to prevent undesired behaviour
    else:  # too short sentence for current skip length
        return type_in_exercise(sentences, pos, length, skip_length, multiple_skips)

    if selected_tokens and not multiple_skips:
        selected_token = random.choice(selected_tokens)
        # selected_token[0] is the token, selected_token[1] is its index
        begin = "".join(tokens[: selected_token[1]])
        end = "".join(tokens[selected_token[1] + skip_length :])
        correct_answer = selected_token[0]

        # correct answer should be string
        if skip_length > 1:
            correct_answer = "".join(
                [
                    token
                    for token in tokens[
                        selected_token[1] : selected_token[1] + skip_length
                    ]
                ]
            ).strip()

        print(begin, end)
        print(correct_answer)
        return (correct_answer, begin, end)

    elif selected_tokens and multiple_skips and len(selected_tokens) >= skip_length:
        selected_tokens = random.sample(selected_tokens, skip_length)
        selected_tokens.sort(key=lambda x: x[1])
        correct_answer = []
        for idx in range(len(selected_tokens)):
            position = selected_tokens[idx][1]
            tokens.insert(position, ". . .")
            correct_answer.append(tokens.pop(position + 1).strip())

        return (correct_answer, tokens)

    else:  # in case sentence doesn't contain desired pos or number of pos
        return type_in_exercise(sentences, pos, length, skip_length, multiple_skips)


def multiple_choice_exercise(sentences: list, pos: list, length: int) -> tuple:
    correct_answer, begin, end = type_in_exercise(sentences, pos, length)

    synonyms = model.most_similar(correct_answer.lower())
    # sometimes gensim suggest punctuation marks as similar words
    synonyms = [synonym[0] for synonym in synonyms if synonym[0] not in ',.;:!?"']

    # adding some customization
    token = nlp(correct_answer.lower())[0]
    pos_tag = token.pos_
    option = None

    for pos, inflection_options in inflection_dict.items():
        if pos_tag == pos:
            inflection_option = random.choice(inflection_options)
            option = token._.inflect(inflection_option)
    if option and option not in synonyms:
        synonyms.insert(0, option)

    if len(synonyms) > NUM_SYNONYMS:
        subsample = synonyms[:NUM_SYNONYMS]
        # don't repeat options on same word
        options = random.sample(subsample, NUM_OPTIONS)
        # options should contain tuples to correctly work with django forms
        options = list(zip(options, options))
    else:
        options = [(synonyms[i], synonyms[i]) for i in range(NUM_OPTIONS)]

    # for capitalized words
    if correct_answer == correct_answer.capitalize():
        options = [
            (options[i][0].capitalize(), options[i][0].capitalize())
            for i in range(NUM_OPTIONS)
        ]

    options.append((correct_answer, correct_answer))
    random.shuffle(options)

    return (correct_answer, begin, end, options)


def word_order_exercise(
    sentences: list, pos: list, length: int, skip_length: int
) -> tuple:
    correct_answer, begin, end = type_in_exercise(sentences, pos, length, skip_length)
    answer = nlp(correct_answer)
    split = [token for token in answer]

    # get rid of exercises with punctuation marks - they are bad
    # just in case checking length (skip length is >= 3 - form params)
    if any([x.is_punct for x in split]) or len(split) < 3:
        return word_order_exercise(sentences, pos, length, skip_length)

    options = []

    # create the same string with one removed article/aux verb
    aux_ind = [i for i in range(len(split)) if split[i].pos_ in ["AUX", "DET"]]
    if aux_ind:
        split_copy = split[:]
        split_copy.pop(random.choice(aux_ind))
        joined = " ".join([token.text for token in split_copy]).strip()
        options.append(joined)  # current options len = 0-1

    # create the same string with one inflected verb/adjective
    for pos, inflection_options in inflection_dict.items():
        aux_ind = [i for i in range(len(split)) if split[i].pos_ == pos]
        if aux_ind:
            split_copy = split[:]
            inflection_option = random.choice(inflection_options)
            i = random.choice(aux_ind)
            option = split_copy[i]._.inflect(inflection_option)
            split_copy.insert(i, option)
            split_copy = split_copy[: i + 1] + split_copy[i + 2 :]
            joined = " ".join(
                [
                    token.text if not isinstance(token, str) else token
                    for token in split_copy
                ]
            ).strip()
            options.append(joined)  # len = 0-2

        # replace a word with synonym
        split_copy = split[:]
        i = random.choice(range(len(split_copy)))
        word = split_copy[i].text.lower()
        syn_rank = random.choice(range(NUM_SYNONYMS))
        synonym = model.most_similar(word)[syn_rank][0]
        if word != split_copy[i].text:  # capitalized words
            synonym = synonym.capitalize()
        split_copy.insert(i, synonym)
        split_copy = split_copy[: i + 1] + split_copy[i + 2 :]
        joined = " ".join(
            [
                token.text if not isinstance(token, str) else token
                for token in split_copy
            ]
        ).strip()
        options.append(joined)  # len = 1-3

    # shuffle word order
    count = 0  # adding 2 sentences with incorrect order in any case
    while count < NUM_OPTIONS - 1:
        random.shuffle(split)
        joined = " ".join([token.text for token in split]).strip()
        if joined not in options:
            options.append(joined)  # len = 3-5, i.e. [NUM_OPTIONS, NUM_OPTIONS+2]
            count += 1
        print(options)

    options = random.sample(options, NUM_OPTIONS)
    options.append(correct_answer)
    options = set(options)  # sometimes shuffle gives identical results
    options = list(zip(options, options))  # format to work with django forms
    print(options)
    return (correct_answer, begin, end, options)


def blanks_exercise(sentences: list, pos: list, length: int, skip_length: int) -> tuple:
    # getting a sequence of sentences with correct length
    # performing all necessary length checks
    correct_answer, sentence = type_in_exercise(
        sentences, pos, length, skip_length, multiple_skips=True
    )
    correct_answer = ", ".join(correct_answer)
    begin = "".join(sentence)
    end = ""
    options = correct_answer
    return (correct_answer, begin, end, options)


if __name__ == "__main__":
    filepath = "/home/tmvfb/english-exercises-app/media/Little_Red_Cap__Jacob_and_Wilhelm_Grimm.txt"  # noqa: E501
    kwargs = {
        "username": "me",
        "pos": "NOUN",
        "length": 1,
        "exercise_type": "blanks_exercise",
        "skip_length": 3,
    }
    prepare_exercises(filepath, **kwargs)
    # remove_data(filepath, **kwargs)
