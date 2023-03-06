from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_API_KEY = "417e34b632c0901f294263c9e52cf6dc"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db.init_app(app)

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)

with app.app_context():
    db.create_all()
    # new_movie = Movies(
    #     title="Phone Booth",
    #     year=2002,
    #     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #     rating=7.3,
    #     ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )
    # db.session.add(new_movie)
    # db.session.commit()

class MyForm(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    review = StringField('Review')
    submit = SubmitField('Done')

class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

@app.route("/")
def home():
    all_movies = Movies.query.order_by(Movies.rating).all()[::-1]
    for i in range(len(all_movies)):
        all_movies[i].ranking = i+1
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    db.session.delete(Movies.query.get(id))
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        data = response.json()['results']
        return render_template("select.html", options=data)
    return render_template("add.html", form=form)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    my_form = MyForm()
    movie = Movies.query.get(id)
    if my_form.validate_on_submit():
        movie.rating = float(my_form.rating.data)
        movie.review = my_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=my_form, movie=movie)

@app.route("/find/<int:id>", methods=["GET", "POST"])
def find(id):
    movie_api_url = f'https://api.themoviedb.org/3/movie/{id}'
    response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY})
    data = response.json()
    print(data)
    new_movie = Movies(
        title=data["title"],
        year=data["release_date"].split("-")[0],
        img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}",
        description=data["overview"]
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
