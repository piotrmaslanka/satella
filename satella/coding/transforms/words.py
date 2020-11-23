import typing as tp


def words_to_int(words: tp.List[str]) -> tp.Dict[str, int]:
    """
    Assign each word an integer, starting from 0, and return the resulting mapping

    :param words: a list of words
    :return: a dictionary keyed by words and values are the assigned integers
    """
    dictionary = {}
    i = 0
    for word in set(words):
        dictionary[word] = i
        i += 1
    return dictionary
