import os
import random
import typing as tp
import string

__all__ = ['shuffle_together', 'random_binary', 'random_word']

from satella.coding.typing import T


def random_word(length: int, choice: T = string.ascii_lowercase,
                join_fun: tp.Callable[[T, ...], T] = lambda *args: ''.join(args)):
    """
    Build and return a random word of provided length.

    The word will be built by calling join_fun with length of arguments picked
    at random from choice.

    :param length: length of the word
    :param choice: a range of characters to use. By default is string.ascii_lowercase
    :param join_fun: an argument to be called with randomly picked characters as *args.
        Defaults to ''.join(args), so your T must be a string. If you're passing a
        different type, remember to alter this function because the default one expects strings!
    :return: a random word
    """
    return join_fun(*(random.choice(choice) for _ in range(length)))


def random_binary(length: int) -> bytes:
    """
    Return a random bytes string of given length.

    An attempt will be made to utilize /dev/random, if exists

    :param length: length of string to generate
    """
    if os.path.exists('/dev/random'):
        with open('/dev/random', 'rb') as f_in:
            return f_in.read(length)
    else:
        return bytes([random.randint(0, 255) for _ in range(length)])


def shuffle_together(*args: tp.Sequence) -> tp.List[tp.List]:
    """
    args, being sequences of equal length, will be permuted in such a way
    that their indices will still correspond to each other.

    So given:

    >>> a = [1, 2, 3]
    >>> b = ['a', 'b', 'c']
    >>> c = shuffle_together(a, b)

    Might equal

    >>> c == [[3, 1, 2], ['c', 'a', 'b']]

    """
    try:
        indices = list(range(len(args[0])))
    except IndexError:
        return []  # empty array

    random.shuffle(indices)
    return [[arg[i] for i in indices] for arg in args]
