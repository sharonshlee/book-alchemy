"""
Install the flask, sqlalchemy, flask_sqlalchemy, and jinja2 libraries into your environment.
"""
import requests
import os
from datetime import datetime

from flask_cors import CORS

from data_models import db, Author, Book

from flask import Flask, render_template, request, jsonify, url_for, redirect

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/library.sqlite')

# Initialize the db instance by passing the app to it
db.init_app(app)

# Link the Author and Book models with the db instance
with app.app_context():
    db.create_all()


def fetch_book_cover_image_url(book_title):
    url = f'https://www.googleapis.com/books/v1/volumes?q={book_title}'
    book_info_dict = requests.get(url).json()
    book_cover_image_url = book_info_dict['items'][0]['volumeInfo']['imageLinks']['thumbnail'] \
        if 'imageLinks' in book_info_dict['items'][0]['volumeInfo'] else ''
    return book_cover_image_url


def get_sorted_books(sort):
    if not sort or sort == 'title_asc':
        return Book.query.order_by(Book.title.asc()).all()
    if sort == 'title_desc':
        return Book.query.order_by(Book.title.desc()).all()
    if sort == 'author_asc':
        return Book.query.join(Author).order_by(Author.name.asc()).all()
    if sort == 'author_desc':
        return Book.query.join(Author).order_by(Author.name.desc()).all()


@app.route('/')
def index():
    sort = request.args.get('sort')
    books = get_sorted_books(sort)

    return render_template('home.html', books=books)


@app.route('/authors', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        birth_date_str = request.form.get('birthdate')

        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()

        death_date_str = request.form.get('date_of_death')

        date_of_death = None
        if death_date_str:
            date_of_death = datetime.strptime(death_date_str, '%Y-%m-%d').date()

        author = Author(
            name=request.form.get('name'),
            birth_date=birth_date,
            date_of_death=date_of_death,
        )
        db.session.add(author)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_author.html')


@app.route('/books', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book_title = request.form.get('title')
        new_book = Book(
            isbn=request.form.get('isbn'),
            title=book_title,
            publication_year=request.form.get('publication_year'),
            cover_image_url=fetch_book_cover_image_url(book_title),
            author_id=request.form.get('author')
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('index'))

    authors = db.session.query(Author).order_by(Author.name.asc()).all()
    return render_template('add_book.html', authors=authors)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
