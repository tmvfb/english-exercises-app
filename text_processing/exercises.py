import os
import random

import gensim.downloader
import lemminflect
import spacy
import spacy.cli
from dotenv import load_dotenv

load_dotenv()
dev = bool(os.getenv("DEBUG"))

if not dev:  # speed up dev server deploy time
    spacy.cli.download("en_core_web_sm")

nlp = spacy.load("en_core_web_sm")
model = gensim.downloader.load("glove-wiki-gigaword-100")
# model = ""


NUM_SYNONYMS = 5  # [3, 10] - defines quality of synonyms for multichoice
NUM_OPTIONS = 3  # number of options for multichoice exercises, <= SYN_COUNT
DIVIDER = ".#.#."  # used for identifying skipped text inside template
inflection_dict = {  # options for inflecting pos
    "VERB": ["VBG", "VBN", "VBZ"],
    "ADJ": ["JJR", "JJS", "RB"],
}


def type_in_exercise(
    sentences: list,
    pos: list,
    length: int,
    skip_length: int = 1,
    multiple_skips: bool = False,
) -> tuple:
    """
    Base function for  all other exercises.
    Selects the skips in sentences in accordance with passed user params.
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

    # only for blanks exercise
    elif len(selected_tokens) >= skip_length and multiple_skips:
        selected_tokens = random.sample(selected_tokens, skip_length)
        selected_tokens.sort(key=lambda x: x[1])
        correct_answer = []
        for idx in range(len(selected_tokens)):
            position = selected_tokens[idx][1]
            tokens.insert(position, DIVIDER)  # mark the skips to find them in template
            correct_answer.append(tokens.pop(position + 1).strip())

        correct_answer = ", ".join(correct_answer)
        begin = "".join(tokens)
        end = ""  # this string is preserved for interface compatibility

    else:  # in case sentence doesn't contain desired pos or number of pos
        return type_in_exercise(sentences, pos, length, skip_length, multiple_skips)

    return (correct_answer, begin, end)


def multiple_choice_exercise(sentences: list, pos: list, length: int) -> tuple:
    correct_answer, begin, end = type_in_exercise(sentences, pos, length)

    try:
        synonyms = model.most_similar(correct_answer.lower())
    except KeyError:
        return multiple_choice_exercise(sentences, pos, length)
    # sometimes gensim suggests punctuation marks as similar words
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
        try:
            synonym = model.most_similar(word)[syn_rank][0]
            if word != split_copy[i].text:  # capitalized words
                synonym = synonym.capitalize()
            split_copy.insert(i, synonym)
        except KeyError:
            pass

        split_copy = split_copy[: i + 1] + split_copy[i + 2 :]
        joined = " ".join(
            [
                token.text if not isinstance(token, str) else token
                for token in split_copy
            ]
        ).strip()
        options.append(joined)  # len = 0-2

    # shuffle word order
    count = 0  # adding 2 sentences with incorrect order in any case
    while count < NUM_OPTIONS - 1:
        random.shuffle(split)
        joined = " ".join([token.text for token in split]).strip()
        if joined not in options:
            options.append(joined)  # len = 2-4, i.e. [NUM_OPTIONS-1, NUM_OPTIONS+1]
            count += 1

    options = random.sample(options, NUM_OPTIONS)
    options.append(correct_answer)
    options = set(options)  # sometimes shuffle gives identical results
    options = list(zip(options, options))  # format to work with django forms
    return (correct_answer, begin, end, options)


def blanks_exercise(sentences: list, pos: list, length: int, skip_length: int) -> tuple:
    # getting a sequence of sentences with correct length
    # performing all necessary length checks
    correct_answer, begin, end = type_in_exercise(
        sentences, pos, length, skip_length, multiple_skips=True
    )
    split_correct_answer = correct_answer.split(", ")
    doc = nlp(" ".join(split_correct_answer))
    tokens = [token for token in doc]
    options = []

    for token in tokens:
        if token.pos_ == "DET":
            options.extend(["a", "an", "the"])
        for pos in inflection_dict.keys():
            if token.pos_ == pos:
                inflection_option = random.choice(inflection_dict[pos])
                options.append(token._.inflect(inflection_option))
        syn_rank = random.choice(range(NUM_SYNONYMS))
        try:
            option = model.most_similar(token.text)[syn_rank][0]
            options.append(option)
        except KeyError:
            pass

    options = random.sample(options, max(len(options) - 1, 0))
    options.extend(split_correct_answer)
    random.shuffle(options)
    options = set(options)
    options = ", ".join(options)

    return (correct_answer, begin, end, options)
