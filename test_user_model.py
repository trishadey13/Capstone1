"""User model tests."""

# run these tests like:
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Recipe, Like

os.environ['DATABASE_URL'] = "postgresql:///capstonetest"

from app import app

# Create our tables

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for recipes."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no liked recipes
        self.assertEqual(len(u.likes), 0)

    def test_user_likes(self):
        r1 = Recipe(
            id=507644,
        )
        r2 = Recipe(
            id=507645,
        )

        u = User.signup("test", "td@email.com", "password", None)
        uid = 111
        u.id = uid
        db.session.add_all([r1,r2,u])
        db.session.commit()

        u.likes.append(r1)
        db.session.commit()

        l = Like.query.filter(Like.user_id == uid).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].recipe_id, r1.id)

        u.likes.append(r2)
        db.session.commit()
        l2 = Like.query.filter(Like.user_id == uid).all()
        self.assertEqual(len(l2), 2)
        self.assertEqual(l2[1].recipe_id, r2.id)
