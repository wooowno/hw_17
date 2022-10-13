from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace("movies")
director_ns = api.namespace("directors")
genre_ns = api.namespace("genres")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        movies_filter = []

        if "director_id" in request.args:
            director_id = request.args.get("director_id")
            movies_filter.append(Movie.director_id == director_id)

        if "genre_id" in request.args:
            genre_id = request.args.get("genre_id")
            movies_filter.append(Movie.genre_id == genre_id)

        movies = db.session.query(Movie).filter(*movies_filter)

        return movies_schema.dump(movies), 200

    def post(self):
        req_json = request.json
        movie = Movie(**req_json)

        movie.director = db.session.query(Director).get(movie.director_id)
        movie.genre = db.session.query(Genre).get(movie.genre_id)

        db.session.add(movie)
        db.session.commit()

        return "", 201


@movie_ns.route("/<int:movie_id>")
class MovieView(Resource):
    def get(self, movie_id):
        try:
            movie = db.session.query(Movie).get(movie_id)
            return movie_schema.dump(movie), 200

        except Exception as e:
            return str(e), 404

    def put(self, movie_id):
        req_json = request.json
        try:
            movie = db.session.query(Movie).get(movie_id)

            movie.title = req_json.get("title")
            movie.description = req_json.get("description")
            movie.trailer = req_json.get("trailer")
            movie.year = req_json.get("year")
            movie.rating = req_json.get("rating")
            movie.genre_id = req_json.get("genre_id")
            movie.director_id = req_json.get("director_id")

            movie.director = db.session.query(Director).get(movie.director_id)
            movie.genre = db.session.query(Genre).get(movie.genre_id)

            db.session.add(movie)
            db.session.commit()

            return "", 204
        except Exception as e:
            return str(e), 404

    def patch(self, movie_id):
        req_json = request.json
        try:
            movie = db.session.query(Movie).get(movie_id)

            if "title" in req_json:
                movie.title = req_json.get("title")

            if "description" in req_json:
                movie.description = req_json.get("description")

            if "trailer" in req_json:
                movie.trailer = req_json.get("trailer")

            if "year" in req_json:
                movie.year = req_json.get("year")

            if "rating" in req_json:
                movie.rating = req_json.get("rating")

            if "genre_id" in req_json:
                movie.genre_id = req_json.get("genre_id")
                movie.genre = db.session.query(Genre).get(movie.genre_id)

            if "director_id" in req_json:
                movie.director_id = req_json.get("director_id")
                movie.director = db.session.query(Director).get(movie.director_id)

            db.session.add(movie)
            db.session.commit()

            return "", 204
        except Exception as e:
            return str(e), 404

    def delete(self, movie_id):
        try:
            movie = db.session.query(Movie).get(movie_id)

            db.session.delete(movie)
            db.session.commit()

            return "", 204

        except Exception as e:
            return str(e), 404


@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors), 200

    def post(self):
        req_json = request.json
        director = Director(**req_json)

        db.session.add(director)
        db.session.commit()

        return "", 201


@director_ns.route("/<int:director_id>")
class DirectorView(Resource):
    def get(self, director_id):
        try:
            director = db.session.query(Director).get(director_id)
            return director_schema.dump(director), 200

        except Exception as e:
            return str(e), 404

    def put(self, director_id):
        req_json = request.json
        try:
            director = db.session.query(Director).get(director_id)

            director.name = req_json.get("name")

            db.session.add(director)
            db.session.commit()

            return "", 204

        except Exception as e:
            return str(e), 404

    def patch(self, director_id):
        req_json = request.json
        try:
            director = db.session.query(Director).get(director_id)

            if "name" in req_json:
                director.name = req_json.get("name")

            db.session.add(director)
            db.session.commit()

            return "", 204

        except Exception as e:
            return str(e), 404

    def delete(self, director_id):
        try:
            director = db.session.query(Director).get(director_id)

            db.session.delete(director)
            db.session.commit()

            return "", 204

        except Exception as e:
            return str(e), 404


@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres), 200

    def post(self):
        req_json = request.json
        genre = Genre(**req_json)

        db.session.add(genre)
        db.session.commit()

        return "", 201


@genre_ns.route("/<int:genre_id>")
class GenreView(Resource):
    def get(self, genre_id):
        try:
            genre = db.session.query(Genre).get(genre_id)
            return genre_schema.dump(genre), 200

        except Exception as e:
            return str(e), 404

    def put(self, genre_id):
        req_json = request.json
        try:
            genre = db.session.query(Genre).get(genre_id)

            genre.name = req_json.get("name")

            db.session.add(genre)
            db.session.commit()

            return "", 204

        except Exception as e:
            return str(e), 404

    def patch(self, genre_id):
        req_json = request.json
        try:
            genre = db.session.query(Genre).get(genre_id)

            if "name" in req_json:
                genre.name = req_json.get("name")

            db.session.add(genre)
            db.session.commit()

            return "", 204

        except Exception as e:
            return str(e), 404

    def delete(self, genre_id):
        try:
            genre = db.session.query(Genre).get(genre_id)

            db.session.delete(genre)
            db.session.commit()

            return "", 204

        except Exception as e:
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
