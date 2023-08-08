import os
import random

import gensim.downloader
import spacy
import spacy.cli
from dotenv import load_dotenv

from .spacy_token_processing import (
    inflect_token,
    remove_token,
    replace_element_in_token_list,
    select_skippable_tokens,
)

model = gensim.downloader.load("glove-wiki-gigaword-100")

load_dotenv()
dev = bool(os.getenv("DEBUG"))
if not dev:  # speed up dev server deploy time
    spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")


NUM_SYNONYMS = 5  # [3, 10] - defines quality of synonyms for multichoice
NUM_OPTIONS = 3  # number of options for multichoice exercises, <= NUM_SYNONYMS
DIVIDER = ".#.#."  # used for identifying skipped text inside django template


def replace_word_with_synonyms(word: str) -> list:
    word_lower = word.lower()
    try:
        synonyms = model.most_similar(word_lower)
        # sometimes gensim suggests punctuation marks as similar words
        synonyms = [synonym[0] for synonym in synonyms if synonym[0] not in ',.;:!?"']
    except KeyError:
        return

    if word != word_lower:
        synonyms = [synonym.capitalize() for synonym in synonyms]
    return synonyms


def pick_long_sentence(sentences: list, length: int) -> str:
    while True:
        rng_sentence = random.randint(0, len(sentences) - length)
        if length == 1:
            sentence = sentences[rng_sentence]
        else:
            sentence = " ".join(sentences[rng_sentence : rng_sentence + length])
        if len(sentence.split(" ")) > 3:  # take context into consideration
            break

    return sentence


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

    sentence = pick_long_sentence(sentences, length)
    doc = nlp(sentence)
    all_tokens, selected_tokens = select_skippable_tokens(doc, skip_length, pos)

    if not selected_tokens:  # sentence is too short
        return type_in_exercise(sentences, pos, length, skip_length, multiple_skips)

    elif not multiple_skips:
        skipped_token = random.choice(selected_tokens)
        # skipped_token[0] is the token, skipped_token[1] is its index
        begin = "".join(all_tokens[: skipped_token[1]])
        end = "".join(all_tokens[skipped_token[1] + skip_length :])
        correct_answer = skipped_token[0]

        if skip_length > 1:
            correct_answer = "".join(
                [
                    token
                    for token in all_tokens[
                        skipped_token[1] : skipped_token[1] + skip_length
                    ]
                ]
            ).strip()

    # blanks exercises only
    elif len(selected_tokens) >= skip_length:
        selected_tokens = random.sample(selected_tokens, skip_length)
        selected_tokens.sort(key=lambda x: x[1])
        correct_answer = []
        for idx in range(len(selected_tokens)):
            position = selected_tokens[idx][1]
            all_tokens.insert(position, DIVIDER)  # mark skips to find them in template
            correct_answer.append(all_tokens.pop(position + 1).strip())

        correct_answer = ", ".join(correct_answer)
        begin = "".join(all_tokens)
        end = ""  # this string is preserved for interface compatibility

    # in case sentence doesn't contain desired pos or number of pos
    else:
        return type_in_exercise(sentences, pos, length, skip_length, multiple_skips)

    return (correct_answer, begin, end)


def multiple_choice_exercise(sentences: list, pos: list, length: int) -> tuple:
    correct_answer, begin, end = type_in_exercise(sentences, pos, length)

    synonyms = replace_word_with_synonyms(correct_answer)
    if not synonyms:
        return multiple_choice_exercise(sentences, pos, length)

    # adding some customization
    token = nlp(correct_answer.lower())[0]
    inflected_token = inflect_token(token)
    if inflected_token and inflected_token not in synonyms:
        synonyms.insert(0, inflected_token)

    if len(synonyms) > NUM_SYNONYMS:
        subsample = synonyms[:NUM_SYNONYMS]
        # don't repeat options on same word
        options = random.sample(subsample, NUM_OPTIONS)
        # options should contain tuples to correctly work with django forms
        options = list(zip(options, options))
    else:
        options = [
            (synonyms[i], synonyms[i]) for i in range(min(len(synonyms), NUM_OPTIONS))
        ]

    # for capitalized words
    if correct_answer == correct_answer.capitalize():
        options = [
            (options[i][0].capitalize(), options[i][0].capitalize())
            for i in range(len(options))
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
    removed = remove_token(answer)
    if removed:
        options.append(removed)  # current options len = 0-1

    # create the same string with one inflected verb/adjective
    inflected = inflect_token(answer, multiple_tokens=True)
    options.extend(inflected)  # current options len = 0-skip_length+1

    # replace a word with synonym
    split = [token for token in answer]
    i = random.choice(range(len(split)))
    syn_rank = random.choice(range(NUM_SYNONYMS))

    word = split[i].text
    synonyms = replace_word_with_synonyms(word)
    synonym = synonyms[syn_rank]
    replaced = replace_element_in_token_list(split, synonym, i)
    options.append(replaced)  # len = 0-skip_length+2

    # shuffle word order
    # adding 2 sentences with incorrect order in any case
    count = 0
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
        inflected_token = inflect_token(token)
        if inflected_token:
            options.append(inflected_token)

        syn_rank = random.choice(range(NUM_SYNONYMS))
        synonyms = replace_word_with_synonyms(token.text)
        if synonyms:
            option = synonyms[syn_rank]
            options.append(option)

    options = random.sample(options, max(len(options) - 1, 0))
    options.extend(split_correct_answer)
    random.shuffle(options)
    options = set(options)
    options = ", ".join(options)

    return (correct_answer, begin, end, options)
