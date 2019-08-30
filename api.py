import os

from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from pathlib import Path
from pymongo import MongoClient, ASCENDING, DESCENDING


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()
mongo_uri=os.environ.get('MONGO_URI')
db_name=os.environ.get('DB_NAME')
api_user = os.environ.get('AUTH_USER')
api_pass = os.environ.get('AUTH_PASS')


@auth.get_password
def get_password(username):
    # temporary
    if username == api_user:
        return api_pass
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)



track_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'producer': fields.String,
    'mousike_date_released': fields.DateTime(dt_format='rfc822'),
    'mousike_last_updated': fields.DateTime(dt_format='rfc822'),
}

album_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'tracks': fields.List(fields.Nested(track_fields)),
    'mousike_date_released': fields.DateTime(dt_format='rfc822'),
    'mousike_last_updated': fields.DateTime(dt_format='rfc822'),
}

artist_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'stage_name': fields.String,
    'is_active': fields.Boolean, # dead or alive essentially
    'music': fields.List(fields.Nested(album_fields)),
    'mousike_date_created' : fields.DateTime(dt_format='rfc822'),
    'mousike_last_updated': fields.DateTime(dt_format='rfc822'),
}


class ArtistListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('first_name', type=str, required=False,
                                   help='No first name title provided',
                                   location=['json', 'form'])
        self.reqparse.add_argument('last_name', type=str, required=False,
                                   help="No last name provided",
                                   location=['json', 'form'])
        self.reqparse.add_argument('stage_name', type=str, required=True,
                                   help="No stage_name provided",
                                   location=['json', 'form'])
        self.reqparse.add_argument('is_active', type=bool, required=False,
                                   help="No active indication",
                                   location=['json', 'form'])
        super(ArtistListAPI, self).__init__()

    def get(self):

        cx = MongoClient(mongo_uri)
        data = [x for x in cx[db_name]['artists'].find().sort('id', -1)]
        for x in data: del x['_id']
        cx = cx.close()

        return {'artists': [marshal(artist, artist_fields) for artist in data]}

    @auth.login_required
    def post(self):

        body = self.reqparse.parse_args()

        cx = MongoClient(mongo_uri)
        col = cx[db_name]['artists']

        if len([x for x in col.find()]) == 0:
            new_id = 1
        else:
            latest_id = [x for x in col.find().sort([('id', -1)]).limit(1)][0]
            new_id = latest_id['id'] + 1

        # here is where we can have some review algos of a new Artist
        if col.find_one({'stage_name': body['stage_name']}) is not None:
            return {'message': 'Request is being reviewed...'}, 202

        artist = {
            'id': new_id,
            'first_name': body['first_name'],
            'last_name': body['last_name'],
            'stage_name': body['stage_name'],
            'is_active': body['is_active'],
            'mousike_date_created': datetime.now(),
            'mousike_last_updated': datetime.now(),
            'music': [],
        }

        result = col.insert_one(artist)
        cx = cx.close()

        return {'artist': marshal(artist, artist_fields), 'result': result.acknowledged}, 201


# class ArtistAPI(Resource):

#     def __init__(self):
#         self.reqparse = reqparse.RequestParser()
#         self.reqparse.add_argument('name', type=str, location='json')
#         self.reqparse.add_argument('name', type=str, location='json')
#         self.reqparse.add_argument('name', type=str, location='json')
#         self.reqparse.add_argument('description', type=str, location='json')
#         self.reqparse.add_argument('review', type=dict, location='json')
#         super(ArtistAPI, self).__init__()

#     def get(self, id):

#         cx = mongo.connect_db()
#         col = cx[db_name]['artists']

#         artist = col.find_one({'id': id})
#         cx = cx.close()
#         del artist['_id']

#         if len(artist) == 0:
#             abort(404)

#         return {'artist': marshal(artist, artist_fields)}

#     @auth.login_required
#     def put(self, id):

#         cx = mongo.connect_db()
#         col = cx[db_name]['artists']

#         artist = col.find_one({'id': id})

#         if len(artist) == 0:
#             abort(404)

#         updates = self.reqparse.parse_args()

#         final_updates = {}

#         for k, v in updates.items():
#             if v is not None:
#                 if k == 'review':
#                     pass
#                 else:
#                     final_updates[k] = v

#         if 'review' in updates.keys() and isinstance(updates['review'], dict):
#             if set(updates['review'].keys()) == set(review_fields.keys()):
#                 review = updates['review']

#                 if len(final_updates) == 0:
#                     col.update_one(
#                         {'_id': artist['_id']},
#                         {'$push': {'reviews': review}},
#                         upsert=False,
#                     )
#                 else:
#                     col.update_one(
#                         {'_id': artist['_id']},
#                         {'$set': final_updates, '$push': {'reviews': review}},
#                         upsert=False,
#                     )

#             else:
#                 abort(404)
#         else:
#             col.update_one({'_id': artist['_id']}, {'$set': updates})

#         cx = cx.close()

#         return {'artist': marshal(artist, artist_fields)}

#     @auth.login_required
#     def delete(self, id):

#         cx = mongo.connect_db()
#         col = cx[db_name]['artists']

#         artist = col.find_one({'id': id})

#         if len(artist) == 0:
#             abort(404)

#         col.delete_one({'_id': artist['_id']})

#         return {'result': True}


api.add_resource(ArtistListAPI, '/mousike/api/v1.0/artists', endpoint='artists')
# api.add_resource(ArtistAPI, '/mousike/api/v1.0/artists/<int:id>', endpoint='artist')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
