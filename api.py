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


@auth.get_password
def get_password(username):
    # temporary
    if username == os.environ.get('AUTH_USER'):
        return os.environ.get('AUTH_PASS')
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)


review_fields = {
    'user': fields.String,
    'rating': fields.Integer,
    'comment': fields.String
}

artist_fields = {
    'name': fields.String,
    'description': fields.String,
    'image_path': fields.String,
    'uri': fields.Url('artist'),
    'id' : fields.String,
    'reviews': fields.List(fields.Nested(review_fields))
}



class ArtistListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True,
                                   help='No artist title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, required=True,
                                   help="No description provided",
                                   location='json')
        self.reqparse.add_argument('image_path', type=str, required=True,
                                   help="No image provided",
                                   location='json')
        super(ArtistListAPI, self).__init__()

    def get(self):

        cx = mongo.connect_db()
        data = [x for x in cx[db_name]['artists'].find().sort('id', -1)]
        for x in data: del x['_id']
        cx = cx.close()

        return {'artists': [marshal(artist, artist_fields) for artist in data]}

    @auth.login_required
    def post(self):
        body = self.reqparse.parse_args()

        cx = mongo.connect_db()
        col = cx[db_name]['artists']

        # this is not the best approach
        if len([x for x in col.find()]) == 0:
            new_id = 1
        else:
            latest_id = [x for x in col.find().sort([('id', -1)]).limit(1)][0]
            new_id = latest_id['id'] + 1

        artist = {
            'id': new_id,
            'name': body['name'],
            'description': body['description'],
            'image_path': body['image_path'],
            'reviews': []
        }

        result = col.insert_one(artist)
        cx = cx.close()

        return {'artist': marshal(artist, artist_fields), 'result': result.acknowledged}, 201


class ArtistAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('review', type=dict, location='json')
        super(ArtistAPI, self).__init__()

    def get(self, id):

        cx = mongo.connect_db()
        col = cx[db_name]['artists']

        artist = col.find_one({'id': id})
        cx = cx.close()
        del artist['_id']

        if len(artist) == 0:
            abort(404)

        return {'artist': marshal(artist, artist_fields)}

    @auth.login_required
    def put(self, id):

        cx = mongo.connect_db()
        col = cx[db_name]['artists']

        artist = col.find_one({'id': id})

        if len(artist) == 0:
            abort(404)

        updates = self.reqparse.parse_args()

        final_updates = {}

        for k, v in updates.items():
            if v is not None:
                if k == 'review':
                    pass
                else:
                    final_updates[k] = v

        if 'review' in updates.keys() and isinstance(updates['review'], dict):
            if set(updates['review'].keys()) == set(review_fields.keys()):
                review = updates['review']

                if len(final_updates) == 0:
                    col.update_one(
                        {'_id': artist['_id']},
                        {'$push': {'reviews': review}},
                        upsert=False,
                    )
                else:
                    col.update_one(
                        {'_id': artist['_id']},
                        {'$set': final_updates, '$push': {'reviews': review}},
                        upsert=False,
                    )

            else:
                abort(404)
        else:
            col.update_one({'_id': artist['_id']}, {'$set': updates})

        cx = cx.close()

        return {'artist': marshal(artist, artist_fields)}

    @auth.login_required
    def delete(self, id):

        cx = mongo.connect_db()
        col = cx[db_name]['artists']

        artist = col.find_one({'id': id})

        if len(artist) == 0:
            abort(404)

        col.delete_one({'_id': artist['_id']})

        return {'result': True}


api.add_resource(ArtistListAPI, '/mousike/api/v1.0/artists', endpoint='artists')
api.add_resource(ArtistAPI, '/mousike/api/v1.0/artists/<int:id>', endpoint='artist')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
