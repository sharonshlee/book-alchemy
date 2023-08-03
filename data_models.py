
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    def __repr__(self) -> str:
        return f"Author(id={self.id}, name={self.name}, birth_date={self.birth_date}, date_of_death={self.date_of_death})"

    def __str__(self) -> str:
        return f"""Author info:
                    id: {self.id},
                    name: {self.name},
                    birth_date: {self.birth_date},
                    date_of_birth: {self.date_of_death}
                """


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String)
    title = db.Column(db.String)
    publication_year = db.Column(db.Integer)
    cover_image_url = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    # Create a relationship between Book and Author
    author = db.relationship('Author', backref='books')

    def __repr__(self) -> str:
        return f"Book(id={self.id}, " \
               f"isbn={self.isbn}, " \
               f"title={self.title}, " \
               f"publication_year={self.publication_year}, " \
               f"author_id={self.author_id})"

    def __str__(self) -> str:
        return f"""Book info:
                    id: {self.id},
                    isbn: {self.isbn},
                    title: {self.title},
                    publication_year: {self.publication_year},
                    author_id={self.author_id}
                """
