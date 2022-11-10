# ./shared/hash.py
import random
import string


def get_random_hash():
    random_hash = "".join(random.sample(string.ascii_letters + string.digits, 15))
    return random_hash
