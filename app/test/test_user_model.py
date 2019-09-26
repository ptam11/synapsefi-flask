import os
from unittest import TestCase

from app.models.User import User

# os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# db.create_all()


# class UserModelTestCase(TestCase):
#     """Test views for messages."""

#     def setUp(self):
#         """Create test client, add sample data."""

#         User.query.delete()
#         Message.query.delete()
#         Follows.query.delete()

#         self.client = app.test_client()

#     def test_user_model(self):
#         """Does basic model work?"""

#         u = User(
#             email="test@test.com",
#             username="testuser",
#             password="HASHED_PASSWORD"
#         )

#         db.session.add(u)
#         db.session.commit()

#         # User should have no messages & no followers
#         self.assertEqual(len(u.messages), 0)
#         self.assertEqual(len(u.followers), 0)