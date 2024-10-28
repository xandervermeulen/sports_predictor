import re


def format_event(event):
    return re.sub(r'(?<=[0-9])(ATP|WTA)', r' \1', event)

