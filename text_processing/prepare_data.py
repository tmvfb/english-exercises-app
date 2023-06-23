class Exercise:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1


def prepare_exercises(filepath, **kwargs):
    # return f'{count = }\n{pos = }\n{ex_type = }\n{length = }'
    # exercise = Exercise()
    # return exercise.count
    # data = {
    #     "sentence": ["My favorite fruit", "apple."],
    #     "correct_answer": "is",
    #     "exercise_type": "type_in"
    # }
    kwargs["correct_answer"] = "SAS"
    kwargs["sentence"] = ["lol", "lel"]
    return kwargs
