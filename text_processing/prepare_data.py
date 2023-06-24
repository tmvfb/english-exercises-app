import random
import re
from sentence_splitter import SentenceSplitter


def prepare_exercises(filepath: str, **kwargs) -> dict:
    with open(filepath, "r") as file:
        text = file.read()

    splitter = SentenceSplitter(language='en')
    sentences = splitter.split(text)

    correct_answer, begin, end = type_in_exercise(sentences)

    kwargs["correct_answer"] = correct_answer
    kwargs["sentence"] = [begin, end]
    return kwargs  # should have correct answer and task sentence


def type_in_exercise(sentences: list) -> tuple:

    while True:
        rng_sentence = random.randint(1, len(sentences)-2)
        sentence = sentences[rng_sentence].split(" ")
        if len(sentence) > 3:  # take context into consideration
            break

    print(sentence)

    rng = random.randint(1, len(sentence)-2)
    correct_answer = sentence[rng]
    correct_answer = re.sub(r"[^A-Za-z]", "", correct_answer)
    print(rng, correct_answer)

    begin = " ".join(sentence[:rng])
    end = " ".join(sentence[rng+1:])
    print(begin, end)
    return (correct_answer, begin, end)


if __name__ == "__main__":
    prepare_exercises(
        "/home/tmvfb/english-exercises-app/media/Little_Red_Cap__Jacob_and_Wilhelm_Grimm.txt"  # noqa: E501
    )
