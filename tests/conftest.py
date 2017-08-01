# Relative import flasksqla_apicrud
import sys;sys.path.append('..')

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flasksqla_apicrud import APIManager



@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    app.testing = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return SQLAlchemy(app)
    

@pytest.fixture
def api(app, db, Film):
    api = APIManager(app, db.session)
    api.register(
        Film
    )
    return api


@pytest.fixture
def Film(db):
    class Film(db.Model):
        __tablename__  = 'films'
        id = Column(Integer, primary_key = True)
        name = Column(String(60), nullable=False)
    db.create_all()
    film = Film(name='Star Wars')
    db.session.add(film)
    db.session.commit()
    return Film
