import random, string

def get_random_hash():
    hash = ''.join(random.sample(string.ascii_letters + string.digits, 15))
    return hash