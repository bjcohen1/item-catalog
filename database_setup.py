import psycopg2
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(80), nullable = False)
    picture = Column(String(250))

class Category(Base):
    __tablename__ = 'categories'
    name = Column (String(80), nullable = False)
    id = Column (Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name' : self.name,
            'id' : self.id
        }

class ListItem(Base):
    __tablename__ = 'list_items'
    name = Column (String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    picture_url = Column(String(350))
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }

engine = create_engine('postgresql://catalog:a!5MrD!b@52.3.235.134/catalog.db')

Base.metadata.create_all(engine)