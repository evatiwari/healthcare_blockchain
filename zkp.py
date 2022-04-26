# imports here
from imghdr import what
import random

# On client side


def zkp(x):
    rounds = 2000
    generator = 2
    prime_number = 11
    all_rounds_verified = True
    y = (generator**x) % prime_number
    for i in range(0, rounds):
        random_int = random.randrange(0, prime_number - 1, 1)
        random_generated_constant = (generator ** random_int) % prime_number
        answer_with_x = (random_int + x) % (prime_number-1)
        answer_with_random_int = (random_int) % (prime_number-1)
        verify = verify_with_zkp(
            answer_with_x, answer_with_random_int, y, random_generated_constant, prime_number, generator)
        all_rounds_verified = verify & all_rounds_verified
    return verify


# Just this function is on the server side, and it has no knowledge of out 'x' value.

def verify_with_zkp(answer_with_x, answer_with_random_int, y, random_generated_constant, prime_number, generator):
    what_to_ask = random.randint(0, 1)
    if(what_to_ask == 1):
        compute_with_answered = (generator ** answer_with_x) % prime_number
    else:
        compute_with_answered = (
            generator ** answer_with_random_int) % prime_number
    compute_with_y_to_verify = (
        random_generated_constant * (y ** what_to_ask)) % prime_number
    if compute_with_answered == compute_with_y_to_verify:
        return True
    return False
