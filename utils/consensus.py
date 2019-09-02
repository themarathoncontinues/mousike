import json
import numpy as np
from json_util import (
    get_nested,
    set_nested
)

from data.sample_ratings import generate_random_ratings

# temporary data read


def rating_weight(length):
    ratings = generate_random_ratings(length)
    for rating in ratings:
        rep = get_nested(rating, 'data.accountStanding.reputation')
        g_rep = get_nested(rating, 'data.accountStanding.genreReputation')

        relative_weight = (rep+g_rep)/2

        set_nested(rating, 'data.relativeWeight', relative_weight)

    return ratings


def calculate_rating(new_ratings):
    overall_rating = [get_nested(x, 'data.overallRating') for x in new_ratings]
    weights = [get_nested(x, 'data.relativeWeight') for x in new_ratings]

    weighted_consensus = round(np.average(overall_rating, weights=weights), 2)

    return weighted_consensus


if __name__ == '__main__':
    length = 1000
    weights = rating_weight(length)
    calculate_rating(weights)