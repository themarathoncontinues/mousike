import json

from data.sample_ratings import generate_random_ratings

# temporary data read


def consensus_rating(length):
    ratings = generate_random_ratings(length)
    print(ratings[0])


if __name__ == '__main__':
    length = 1000
    consensus_rating(length)