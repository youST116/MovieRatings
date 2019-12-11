from sqlalchemy import func
from model import User, Rating, Movie
import datetime
from model import connect_to_db, db
from routes import app

def load_users():
    print "Users"
    User.query.delete()
    with open("seed_data/u.user") as user_file:
        for row in user_file:
            row = row.rstrip()
            user_id, email, password, age, zipcode = row.split("|")

            user = User(user_id=user_id,
                        age=age,
                        zipcode=zipcode)

            db.session.add(user)
    db.session.commit()

def load_movies():
    print "Movies"
    Movie.query.delete()
    with open("seed_data/u.item")as movie_file:
        for row in movie_file:
            row = row.rstrip().split("|")
            movie_id, title, released_at, misc, imdb_url = row[0:5]
            movie_id = int(movie_id)
            title = title[:-7]
            if released_at:
                released_at = datetime.datetime.strptime(released_at, "%d-%b-%Y")
                movie = Movie(movie_id=movie_id, title=title, released_at=released_at, imdb_url=imdb_url)
            else:
                movie = Movie(movie_id=movie_id, title=title, imdb_url=imdb_url)
            db.session.add(movie)
    db.session.commit()

def load_ratings():
    print "Ratings"
    Rating.query.delete()
    with open("seed_data/u.data") as rating_file:
        i=0
        for row in rating_file:
            row = row.rstrip().split()
            user_id = int(row[0])
            movie_id = int(row[1])
            score = int(row[2])
            rating = Rating(user_id=user_id, movie_id=movie_id, score=score)
            db.session.add(rating)
            if i%1000==0:
                db.session.commit()
    db.session.commit()

def set_val_user_id():
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
