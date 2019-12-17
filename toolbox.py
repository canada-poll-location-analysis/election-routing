import datetime
import os


def try_to_int(value):
    try:
        return int(value)
    except ValueError:
        return value


def try_to_numeric(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def make_directory(fn):
    test_directory(fn)


def test_directory(path):
    """ Tests a file path and ensures the path exists.  If it does not exist, I will create the path
    :param path: String of a path
    """
    p = os.path.dirname(os.path.abspath(path))
    if not os.path.exists(p):
        os.makedirs(p)


def time_for_files(time=datetime.datetime.now()):
    """
    Gets a time string for file names that I like.
    """
    time = time.strftime("%Y%m%d_%H%M%S")
    return time
