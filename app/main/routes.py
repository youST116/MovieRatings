from app.main import bp
from flask import render_template
from flask import Flask, jsonify, redirect, request, flash, session
from app.main.model import User, Movie, Rating, connect_to_db, db
import sqlite3

app = Flask(__name__)
app.secret_key = "ABC"

@bp.route('/')
def index():
    return render_template("Home.html")

@bp.route('/users', methods=['GET','POST'])
def user_list():
    users = User.query.all()
    return render_template("Users.html", users=users)

@bp.route("/users/<user_id>")
def show_user_page(user_id):
    user = User.query.get(user_id)
    ratings_list = db.session.query(Rating.score, Movie.title, Movie.imdb_url).join(Movie).filter(Rating.user_id==user_id).all()

    return render_template("User_page.html", user=user, ratings_list=ratings_list)

@bp.route("/movies")
def movie_list():
    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)

@bp.route("/movies/<movie_id>")
def show_movie_page(movie_id):
    movie = Movie.query.get(movie_id)
    user_id = session.get("user_id")
    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()
    else:
        user_rating = None

    conn = sqlite3.connect('ratings.db')
    c = conn.cursor()
    c.execute("SELECT score FROM ratings")
    rating_scores = c.fetchall()
    avg_rating = float(sum(rating_scores) / len(rating_scores))
    prediction = None

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)

    return render_template(
        "movie_page.html",
        movie=movie,
        user_rating=user_rating,
        average=avg_rating,
        prediction=prediction
        )


@bp.route("/movies/<movie_id>", methods=["POST"])
def rate_movie_page(movie_id):
    new_score = request.form.get("movie-rating")
    movie = Movie.query.get(movie_id)
    user_id=session["user_id"]

    rating = Rating.query.filter((Rating.user_id==user_id) & (Rating.movie_id==movie_id)).first()

    if not rating:
        rating = Rating(score=new_score, user_id=user_id, movie_id=movie_id)

    else:
        rating.score = new_score

    db.session.add(rating)
    db.session.commit()

    return redirect("/movies/%s" % movie_id)

@bp.route("/login")
def show_login():
    return render_template("login_form.html")

@bp.route("/login", methods=["POST"])
def login_process():
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Email does not exist. Please try again or register.")
        return redirect("/login")
    elif user and (user.password == password):
        flash("Login Successful.")
        session['user_id'] = user.user_id
        return redirect("/users/" + str(user.user_id))
    else:
        flash("Incorrect Password... Please try again.")
        return redirect("/login")

@bp.route("/logout")
def show_logout():
    flash("Logged out. Thanks for visiting Ratings!")
    del session['user_id']
    return redirect("/")

@bp.route("/registration")
def show_registration():
    return render_template("registration_form.html")

@bp.route("/registration", methods=["POST"])
def registration_process():
    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    if age:
        age = int(age)
    else:
        age=None
    zipcode = request.form.get("zipcode")

    user = User.query.filter_by(email=email).first()

    if user:
        flash("You're already in our system? Please login to your account instead.")
        return redirect("/login")
    else:
        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.user_id
        flash("Registration Successful. Thank You! Look through our Ratings! In the End, PLEASE Rate some of these Movies too!!")
        return redirect("/")

if __name__ == "__main__":
    connect_to_db(app)
    app.run()
