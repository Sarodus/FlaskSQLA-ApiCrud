# -*- coding: utf-8 -*-
# Relative import flasksqla_apicrud
import sys;sys.path.append('.')

import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flasksqla_apicrud import APIManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'holaquetal'
db = SQLAlchemy(app)
api = APIManager(app, db.session)


class Actor(db.Model):
    __tablename__ = 'actors'

    id           = Column(Integer, primary_key = True)
    name         = Column(String(60), nullable=False)


class Director(db.Model):
    __tablename__ = 'directors'

    id           = Column(Integer, primary_key = True)
    name         = Column(String(60), nullable=False)


film_actor = Table(
    'film_actor',
    db.Model.metadata,
    Column('film_id', Integer, ForeignKey('films.id')),
    Column('actor_id', Integer, ForeignKey('actors.id'))
)

class Film(db.Model):
    __tablename__  = 'films'

    id           = Column(Integer, primary_key = True)
    name         = Column(String(60), nullable=False)
    director_id  = Column(Integer, ForeignKey(Director.id), nullable=False)
    director     = relationship(Director)
    actors       = relationship(Actor, secondary=film_actor)


# /films/
# /films/1
# /films/1/actors
# /films/1/director
api.register(
    Film,
    extra_fields = ['director', 'actors'],
    relations_fields = {
        'directors': ['name'],
    },
    joined_load_models = (Film.director, Film.actors)
)

@app.route('/')
def welcome():
    return '<body>Hello!</body>'


@click.group()
def cli():
    """Commands:"""

@cli.command()
def initdb():
    """Create tables and seed with dummy data"""
    FILMS = (
        (
            'Star Wars: Episode I - The Phantom Menace',
            'George Lucas',
            ('Liam Neeson','Ewan McGregor','Natalie Portman','Jake Lloyd','Ian McDiarmid','Anthony Daniels','Kenny Baker','Pernilla August','Frank Oz')
        ),
        (
            'Star Wars: Episode II - Attack of the Clones',
            'George Lucas',
            ('Ewan McGregor','Natalie Portman','Hayden Christensen','Ian McDiarmid','Samuel L. Jackson','Christopher Lee','Anthony Daniels','Kenny Baker','Frank Oz')
        ),
        (
            'Star Wars: Episode III - Revenge of the Sith',
            'George Lucas',
            ('Ewan McGregor','Natalie Portman','Hayden Christensen','Ian McDiarmid','Samuel L. Jackson','Christopher Lee')
        ),
        (
            'Star Wars: Episode IV - A New Hope',
            'George Lucas',
            ('Mark Hamill','Harrison Ford','Carrie Fisher','Peter Cushing','Alec Guinness')
        ),
        (
            'Star Wars: Episode V - The Empire Strikes Back',
            'Irvin Kershner',
            ('Mark Hamill','Harrison Ford','Carrie Fisher','Billy Dee Williams','Anthony Daniels','David Prowse','Kenny Baker','Peter Mayhew','Frank Oz')
        ),
        (
            'Star Wars: Episode VI - Return of the Jedi',
            'Richard Marquand',
            ('Mark Hamill','Harrison Ford','Carrie Fisher','Billy Dee Williams','Anthony Daniels','David Prowse','Kenny Baker','Peter Mayhew','Frank Oz')
        )
    )
    click.echo('Creatings tables...')
    db.create_all()
    click.echo('Tables created!')
    click.echo('Seeding data...')
    for film_name, director_name, actors in FILMS:
        film = Film(name=film_name)
        for actor_name in actors:
            actor = Actor.query.filter_by(name=actor_name).first()
            if actor is None:
                actor = Actor(name=actor_name)
            film.actors.append(actor)
        director = Director.query.filter_by(name=director_name).first()
        if director is None:
            director = Director(name=director_name)
        film.director = director
        db.session.add(film)
        db.session.commit()


@cli.command()
def runserver():
    """Run the server"""
    app.run(debug=True)


if __name__ == '__main__':
    cli()
