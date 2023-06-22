class Exercise:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1


def prepare_exercises(count, pos, ex_type, length):
    # return f'{count = }\n{pos = }\n{ex_type = }\n{length = }'
    exercise = Exercise()
    return exercise.count
