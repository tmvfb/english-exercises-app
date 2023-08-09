"""
This module works predominantly with spaCy objects. In order to reuse functions
from this module, spaCy should be imported explicitly.
"""

import random

import lemminflect
from spacy.tokens.doc import Doc
from spacy.tokens.token import Token

INFLECTION_DICT = {  # options for inflecting pos
    "VERB": ["VBG", "VBN", "VBZ"],
    "ADJ": ["JJR", "JJS", "RB"],
}


def select_skippable_tokens(doc: Doc, skip_length: int, pos: list) -> tuple:
    """
    Receives a spacy Doc object and finds which tokens can be skipped for
    exercises in accordance with the given pos and skip length.
    Returns all tokens in text format and skippable tokens in (text, position) format.
    """

    all_tokens = [token.text_with_ws for token in doc]
    if "ALL" not in pos:
        selected_tokens = [
            (token.text, token.i) for token in doc if token.pos_ in pos and token.i > 0
        ]
        if skip_length > 1:
            # don't select tokens at the very end of the sentence
            # functions are designed to skip a few words AFTER the selected token
            selected_tokens = list(
                filter(lambda x: x[1] <= len(all_tokens) - skip_length, selected_tokens)
            )
    elif len(all_tokens) > 2 * skip_length:  # restrict to get slice correctly
        selected_tokens = [
            (token.text, token.i) for token in doc if not token.is_punct
        ][
            1:-skip_length
        ]  # by default remove 1st and last to prevent undesired behaviour
    else:  # too short sentence for current skip length
        selected_tokens = None
    return all_tokens, selected_tokens


def inflect_token(doc: Token or Doc, multiple_tokens: bool = False) -> str or list:
    """
    Function inflecting spacy Token or Doc in accordance with INFLECTION_DICT.
    Returns string if a Token object is passed, returns list, if Doc is passed.
    """

    options = []
    if multiple_tokens:
        split = [token for token in doc]

    for pos, inflection_options in INFLECTION_DICT.items():
        if multiple_tokens:
            pos_idx = [i for i in range(len(split)) if split[i].pos_ == pos]
            if pos_idx:
                inflection_option = random.choice(inflection_options)
                i = random.choice(pos_idx)
                option = split[i]._.inflect(inflection_option)
                replaced = replace_element_in_token_list(split, option, i)
                options.append(replaced)

        elif doc.pos_ == pos:
            inflection_option = random.choice(inflection_options)
            inflected_token = doc._.inflect(inflection_option)
            return inflected_token

    return options


def remove_token(doc: Doc) -> str:
    """
    Remove a token in spacy Doc object if a token is auxiliary verb or determinant.
    """

    split = [token for token in doc]
    aux_idx = [i for i in range(len(split)) if split[i].pos_ in ["AUX", "DET"]]
    if aux_idx:
        split_copy = split[:]
        split_copy.pop(random.choice(aux_idx))
        joined = " ".join([token.text for token in split_copy]).strip()
        return joined


def add_token(doc: Doc) -> str:
    """
    Add an article before noun.
    """

    split = [token for token in doc]
    noun_idx = [i for i in range(len(split)) if split[i].pos_ == "NOUN"]
    if noun_idx:
        split_copy = split[:]
        i = random.choice(noun_idx)
        options = ["a", "an", "the"]
        split_copy.insert(i, random.choice(options))
        joined = " ".join(
            [
                token.text if not isinstance(token, str) else token
                for token in split_copy
            ]
        ).strip()
        return joined


def replace_element_in_token_list(token_list: list, element: str, position: int) -> str:
    """
    Auxiliary function to replace an element in a list of tokens (or strings)
    and return a joined string with replaced element.
    """

    token_list = token_list[:]
    token_list.insert(position, element)
    split = token_list[: position + 1] + token_list[position + 2 :]
    joined = " ".join(
        [token.text if not isinstance(token, str) else token for token in split]
    ).strip()
    return joined
