"""
Install the flask, sqlalchemy, flask_sqlalchemy, and jinja2 libraries into your environment.
"""
from datetime import datetime
import os
from data_models import db, Author, Book

from flask import Flask, render_template, request, jsonify

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/library.sqlite')

# Initialize the db instance by passing the app to it
db.init_app(app)

# Link the Author and Book models with the db instance
with app.app_context():
    db.create_all()


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
            date_of_death=date_of_death
        )
        db.session.add(author)
        db.session.commit()
        return jsonify({'message': 'Author added successfully!'}), 201

    return render_template('add_author.html')


@app.route('/books', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        new_book = Book(
            isbn=request.form.get('isbn'),
            title=request.form.get('title'),
            publication_year=request.form.get('publication_year'),
            author_id=request.form.get('author')
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully!'}), 201

    authors = db.session.query(Author).order_by(Author.name.asc()).all()
    return render_template('add_book.html', authors=authors)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
