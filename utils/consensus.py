import json

from data.sample_ratings import generate_random_ratings


def test_random_ratings():
    length = 1000

    ratings = generate_random_ratings(length)
    with open('data/sample_data/random_ratings.json', 'w') as fout:
        for rating in ratings:
            json.dump(rating, fout)
            print(json.dumps(rating, indent=4))

    print('Finished')



if __name__ == '__main__':
    test_random_ratings()