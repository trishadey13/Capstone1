"""Recipe model tests."""

# run these tests like:
#
#    python -m unittest test_recipe_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Recipe, User, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///capstonetest"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class RecipeModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        # self.uid = 94566
        # u = User.signup("testing", "testing@test.com", "password", None)
        # u.id = self.uid
        # db.session.commit()

        # self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""
        
        m = Recipe(
            id=123456
        )

        db.session.add(m)
        db.session.commit()

    def test_recipe_likes(self):
        m1 = Recipe(
            id=567643,
        )

        u = User.signup("yetanothertest", "t@email.com", "password", None)
        uid = 888
        u.id = uid
        db.session.add_all([m1, u])
        db.session.commit()

        u.likes.append(m1)

        db.session.commit()

        l = Like.query.filter(Like.user_id == uid).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].recipe_id, m1.id)


