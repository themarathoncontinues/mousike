import json

# temporary data read
ratings = []
with open('data/sample_data/random_ratings.txt') as f:
    for rating in f:
        ratings.append(json.loads(rating))



def consensus_rating(ratings):
    print(ratings)


if __name__ == '__main__':
    consensus_rating(ratings)