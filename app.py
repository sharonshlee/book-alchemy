"""
Install the flask, sqlalchemy, flask_sqlalchemy, and jinja2 libraries into your environment.
"""
import os
from datetime import datetime
import requests
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, render_template, request
from data_models import db, Author, Book

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
    """
    Fetch book cover image url
    from external Google Books API
    """
    url = f'https://www.googleapis.com/books/v1/volumes?q={book_title}'
    book_info_dict = requests.get(url, timeout=5).json()
    book_cover_image_url = book_info_dict['items'][0]['volumeInfo']['imageLinks']['thumbnail'] \
        if 'imageLinks' in book_info_dict['items'][0]['volumeInfo'] else ''
    return book_cover_image_url


def get_sorted_books(sort):
    """
    Return sorted books by sort keyword
    """
    if sort == 'title_desc':
        return Book.query.order_by(Book.title.desc()).all()
    if sort == 'author_asc':
        return Book.query.join(Author).order_by(Author.name.asc()).all()
    if sort == 'author_desc':
        return Book.query.join(Author).order_by(Author.name.desc()).all()

    return Book.query.order_by(Book.title.asc()).all()


def search_book_by_title(search_keyword):
    """
    Search a book by title given search keyword
    """
    return Book.query.filter(Book.title.like(f'%{search_keyword}%')).all()


@app.route('/')
def index():
    """
    Home page and sort route
    """
    sort = request.args.get('sort')
    books = get_sorted_books(sort)
    return render_template('home.html', books=books)


@app.route('/search_book', methods=['POST'])
def search_book():
    """
    Render all the books that meet the search criteria,
    or display a message that says there were no books that match the search criteria.
    """
    search_keyword = request.form.get('search')
    books = search_book_by_title(search_keyword)
    error_message = ''

    if not books:
        error_message = f'There were no books that match {search_keyword}.'

    return render_template('home.html', error_message=error_message, books=books)


def get_new_author_info():
    """
    Get new author info from user input
    """
    name = request.form.get('name')
    birth_date_str = request.form.get('birthdate')
    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
    death_date_str = request.form.get('date_of_death')

    date_of_death = None
    if death_date_str:
        date_of_death = datetime.strptime(death_date_str, '%Y-%m-%d').date()

    return name, birth_date, date_of_death


def instantiate_new_author():
    """
    Instantiate a new author object
    with info from user input
    """
    name, birth_date, date_of_death = get_new_author_info()

    return Author(
        name=name,
        birth_date=birth_date,
        date_of_death=date_of_death,
    )


@app.route('/authors', methods=['GET', 'POST'])
def add_author():
    """
    Add a new authors route
    """
    if request.method == 'POST':
        try:
            new_author = instantiate_new_author()
            db.session.add(new_author)
            db.session.commit()
            message = 'Author has successfully added to the database.'
        except SQLAlchemyError:
            db.session.rollback()
            message = 'Failed to add author to the database.'
        return render_template('add_author.html', message=message)

    return render_template('add_author.html')


def instantiate_new_book():
    """
    Instantiate a new book object
    with info from user input
    """
    book_title = request.form.get('title')
    return Book(
        isbn=request.form.get('isbn'),
        title=book_title,
        publication_year=request.form.get('publication_year'),
        cover_image_url=fetch_book_cover_image_url(book_title),
        author_id=request.form.get('author')
    )


@app.route('/books', methods=['GET', 'POST'])
def add_book():
    """
    Add a new book route
    """
    if request.method == 'POST':
        try:
            new_book = instantiate_new_book()
            db.session.add(new_book)
            db.session.commit()
            message = 'Book has successfully added to the database.'
        except SQLAlchemyError:
            db.session.rollback()
            message = 'Failed to add book to the database.'
        return render_template('add_book.html', message=message)

    authors = db.session.query(Author).order_by(Author.name.asc()).all()
    return render_template('add_book.html', authors=authors)


def delete_author(book_id):
    """
    Delete the author who does not have any books in the database
    """
    book_to_delete = Book.query.filter(Book.id == book_id).one()
    author_count = Book.query.filter(Book.author_id == book_to_delete.author_id).count()
    if author_count == 1:
        Author.query.filter(Author.id == book_to_delete.author_id).delete()


@app.route('/book/<int:book_id>/delete')
def delete_book(book_id):
    """
    Delete a specific book by book_id route
    """
    try:
        delete_author(book_id)
        Book.query.filter(Book.id == book_id).delete()
        db.session.commit()
        message = f'Book {book_id} has been deleted from the database.'
    except SQLAlchemyError:
        db.session.rollback()
        message = f'Failed to delete book {book_id}.'

    books = Book.query.order_by(Book.title.asc()).all()
    return render_template('home.html', books=books, message=message)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
