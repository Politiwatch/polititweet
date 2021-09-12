from difflib import SequenceMatcher


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def first_or_none(obj):
    try:
        return obj[0]
    except:
        return None
