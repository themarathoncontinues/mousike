import json
import random


def generate_random_ratings(length):
    ratings = []
    for x in range(length):
        rating =  {
            "data": {
                "accountStanding": {
                    "reputation": random.uniform(0, 10),
                    "genreReputation": random.uniform(0, 10)
                },
                "overallRating": random.uniform(0, 10),
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
                }
            },
            "key": {
                "accountCreatedAt": "2019-08-21",
                "userName": "leon",
                "uuid": x+1
            }
        }

        ratings.append(rating)

    return ratings


def create_random_ratings():
    length = 1000

    ratings = generate_random_ratings(length)
    with open('data/sample_data/random_ratings.json', 'w') as fout:
        for rating in ratings:
            json.dump(rating, fout)
            print(json.dumps(rating, indent=4))

    print('-----Random Ratings Created-----')



if __name__ == '__main__':
    create_random_ratings()