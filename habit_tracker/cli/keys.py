BACK = "b"
QUIT = "q"
ENTER = "enter"
NEXT_PAGE = "n"
PREV_PAGE = "p"
ADD = "a"


def is_digit_key(key: str) -> bool:
    return len(key) == 1 and key.isdigit()


def digit_value(key: str) -> int:
    return int(key)
