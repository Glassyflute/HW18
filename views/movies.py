# здесь контроллеры/хендлеры/представления для обработки запросов (flask ручки). сюда импортируются сервисы из пакета service
from flask import request
from flask_restx import Resource, Namespace
from models import Movie, MovieSchema
from setup_db import db

movie_ns = Namespace('movies')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        all_movies_query = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id:
            all_movies_query = all_movies_query.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id:
            all_movies_query = all_movies_query.filter(Movie.genre_id == genre_id)

        year_selected = request.args.get("year")
        if year_selected:
            all_movies_query = all_movies_query.filter(Movie.year == year_selected)

        final_query = all_movies_query.all()

        return movies_schema.dump(final_query), 200

    def post(self):
        new_data = request.json

        movie_ = movie_schema.load(new_data)
        new_movie = Movie(**movie_)
        with db.session.begin():
            db.session.add(new_movie)

        return "", 201
# ставим при проверке закрывающий слэш в Postman

# movie_new = {
#         "trailer": "https://youtu.be/VISiqVeKTq8",
#         "year": 2022,
#         "title": "Гарри Поттер в Средиземье",
#         "rating": 7.1,
#         "genre_id": 3,
#         "description": "История попадания в Средиземье того самого Гарри Поттера - спаситель должен примерить на себя роль Лучшего Друга ГГ саги, Сэма, и взглянуть на собственные приключения с новой стороны.",
#         "director_id": 4
#     }

# movie_2 = {
#         "trailer": "https://youtu.be/VISiqVeKTq8",
#         "year": 2023,
#         "title": "Гарри Поттер в Средиземье -часть 2",
#         "rating": 3.5,
#         "genre_id": 3,
#         "description": "История попадания в Средиземье того самого Гарри Поттера - часть 2.",
#         "director_id": 4
#     }


@movie_ns.route("/<mid>")
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)

        if not movie:
            return "", 404

        return movie_schema.dump(movie), 200

    def put(self, mid):
        movie_selected = db.session.query(Movie).filter(Movie.id == mid)
        movie_first = movie_selected.first()

        if movie_first is None:
            return "", 404

        new_data = request.json
        movie_selected.update(new_data)
        db.session.commit()

        return "", 204

    def delete(self, mid):
        movie_selected = db.session.query(Movie).filter(Movie.id == mid)
        movie_first = movie_selected.first()

        if movie_first is None:
            return "", 404

        rows_deleted = movie_selected.delete()
        # если произошло удаление более 1 строки, то указываем на наличие проблемы.
        if rows_deleted != 1:
            return "", 400

        db.session.commit()
        return "", 204

