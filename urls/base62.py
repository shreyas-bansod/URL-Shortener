CHARACTERS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode(number):
    if number == 0:
        return CHARACTERS[0]

    result = []

    while number > 0:
        remainder = number % 62
        result.append(CHARACTERS[remainder])
        number = number // 62

    return "".join(reversed(result))