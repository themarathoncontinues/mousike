import json
import random

from collections import OrderedDict


def generate_random_ratings(length):
    for x in range(length):
        yield {
            "data": {
                "reputation": random.uniform(0, 10),
                "genreReputation": random.uniform(0, 10)
                },
                "ratingCriteria": {
                    "complexity": random.uniform(0, 10),
                    "consistency": random.uniform(0, 10),
                    "content": random.uniform(0, 10),
                    "continuity": random.uniform(0, 10),
                    "lyrics": random.uniform(0, 10),
                    "production": random.uniform(0, 10),
                    "style": random.uniform(0, 10),
                    "substance": random.uniform(0, 10),
                    "tenacity": random.uniform(0, 10)
                },
                "reviewComment": "",
                "source": {
                    "albumName": "GINGER",
                    "artistName": "BROCKHAMPTON",
                    "releaseDate": "2019-08-23",
                    "label": "RCA Records"
                },
                "metadata": {
                    "rating": {
                        "amount": x+1,
                        "initial": "2019-08-23"
                    }
                },
            "key": {
                "accountCreatedAt": "2019-08-21",
                "userName": "leon",
                "uuid": x+1
            }
        }
