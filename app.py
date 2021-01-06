import os
import requests
import random
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from forms import SearchForm

# from forms import UserAddForm, UserEditForm, LoginForm, MessageForm
from models import db, connect_db, Recipe

CURR_USER_KEY = "curr_user"
SPOON_API = "https://api.spoonacular.com"
API_KEY = "3630282f6c42420fa7099731b3f21509"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgres:///capstone'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def homepage():
    """Show homepage:"""
    OFFSET = random.randint(0, 900)
    HEALTH_OFFSET = random.randint(0, 500)

    random_recipes = requests.get(f'{SPOON_API}/recipes/complexSearch?number=5&offset={OFFSET}&apiKey={API_KEY}').json()['results']
    popular_recipes = requests.get(f'{SPOON_API}/recipes/complexSearch?number=5&offset={OFFSET}&sort=popularity&apiKey={API_KEY}').json()['results']
    healthy_recipes = requests.get(f'{SPOON_API}/recipes/complexSearch?number=5&offset={HEALTH_OFFSET}&sort=healthiness&apiKey={API_KEY}').json()['results']
    
    all_recipe_ids = ""
    for (rand, pop, health) in zip(random_recipes, popular_recipes, healthy_recipes):
        r_id = rand['id']
        p_id = pop['id']
        h_id = health['id']
        all_recipe_ids += f'{r_id},{p_id},{h_id},'
    
    all_results = requests.get(f'{SPOON_API}/recipes/informationBulk?ids={all_recipe_ids}&apiKey={API_KEY}').json()

    return render_template('home.html', rand_results=all_results[:5], pop_results=all_results[5:10], health_results=all_results[10:])

@app.route('/search-results', methods=['GET', 'POST'])
def get_search_results():

    formdata = request.form['q']
    req_data = requests.get(f'{SPOON_API}/recipes/complexSearch?query={formdata}&apiKey={API_KEY}').json()['results']
    
    all_recipe_ids = ""
    for result in req_data:
        r_id = result['id']
        all_recipe_ids += f'{r_id},'

    all_results = requests.get(f"{SPOON_API}/recipes/informationBulk?ids={all_recipe_ids}&apiKey={API_KEY}").json()
    
    return render_template('search.html', all_results=all_results)
    

# @app.before_request
# def add_user_to_g():
#     """If we're logged in, add curr user to Flask global."""

#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#     else:
#         g.user = None

# def do_login(user):
#     """Log in user."""

#     session[CURR_USER_KEY] = user.id


# def do_logout():
#     """Logout user."""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]


# @app.route('/signup', methods=["GET", "POST"])
# def signup():
#     """Handle user signup.

#     Create new user and add to DB. Redirect to home page.

#     If form not valid, present form.

#     If the there already is a user with that username: flash message
#     and re-present form.
#     """
#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]
#     form = UserAddForm()

#     if form.validate_on_submit():
#         try:
#             user = User.signup(
#                 username=form.username.data,
#                 password=form.password.data,
#                 email=form.email.data,
#                 image_url=form.image_url.data or User.image_url.default.arg,
#             )
#             db.session.commit()

#         except IntegrityError as e:
#             flash("Username already taken", 'danger')
#             return render_template('users/signup.html', form=form)

#         do_login(user)

#         return redirect("/")

#     else:
#         return render_template('users/signup.html', form=form)

# @app.route('/login', methods=["GET", "POST"])
# def login():
#     """Handle user login."""

#     form = LoginForm()

#     if form.validate_on_submit():
#         user = User.authenticate(form.username.data,
#                                  form.password.data)

#         if user:
#             do_login(user)
#             flash(f"Hello, {user.username}!", "success")
#             return redirect("/")

#         flash("Invalid credentials.", 'danger')

#     return render_template('users/login.html', form=form)

# @app.route('/logout')
# def logout():
#     """Handle logout of user."""

#     do_logout()

#     flash("You have successfully logged out.", 'success')
#     return redirect("/login")

# @app.route('/search')
# def list_search_recipes():

#     """Can take a 'search' param in querystring to search by that"""

#     search = request.args.get('search')

#     if not search:
#         recipes = Recipe.query.all()
#     else:
#         recipes = Recipe.query.filter(Recipe.name.like(f"%{search}%")).all()

#     return render_template('users/index.html', recipes=recipes)

# @app.route('/users/<int:user_id>')
# def users_show(user_id):
#     """Show user profile."""

#     user = User.query.get_or_404(user_id)
#     # snagging messages in order from the database;
#     # user.messages won't be in order by default
#     messages = (Message
#                 .query
#                 .filter(Message.user_id == user_id)
#                 .order_by(Message.timestamp.desc())
#                 .limit(100)
#                 .all())
#     likes = [message.id for message in user.likes]
#     return render_template('users/show.html', user=user, messages=messages, likes=likes)

# @app.route('/users/<int:user_id>/following')
# def show_following(user_id):
#     """Show list of people this user is following."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
#     return render_template('users/following.html', user=user)


# @app.route('/users/<int:user_id>/followers')
# def users_followers(user_id):
#     """Show list of followers of this user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
#     return render_template('users/followers.html', user=user)

# @app.route('/users/follow/<int:follow_id>', methods=['POST'])
# def add_follow(follow_id):
#     """Add a follow for the currently-logged-in user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     followed_user = User.query.get_or_404(follow_id)
#     g.user.following.append(followed_user)
#     db.session.commit()

#     return redirect(f"/users/{g.user.id}/following")

# @app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
# def stop_following(follow_id):
#     """Have currently-logged-in-user stop following this user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     followed_user = User.query.get(follow_id)
#     g.user.following.remove(followed_user)
#     db.session.commit()

#     return redirect(f"/users/{g.user.id}/following")

# @app.route('/users/<int:user_id>/likes', methods=["GET"])
# def show_likes(user_id):
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
#     return render_template('users/likes.html', user=user, likes=user.likes)

# @app.route('/messages/<int:message_id>/like', methods=['POST'])
# def add_like(message_id):
#     """Toggle a liked message for the currently-logged-in user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     liked_message = Message.query.get_or_404(message_id)
#     if liked_message.user_id == g.user.id:
#         return abort(403)

#     user_likes = g.user.likes

#     if liked_message in user_likes:
#         g.user.likes = [like for like in user_likes if like != liked_message]
#     else:
#         g.user.likes.append(liked_message)

#     db.session.commit()

#     return redirect("/")

# @app.route('/users/profile', methods=["GET", "POST"])
# def edit_profile():
#     """Update profile for current user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = g.user
#     form = UserEditForm(obj=user)

#     if form.validate_on_submit():
#         if User.authenticate(user.username, form.password.data):
#             user.username = form.username.data
#             user.email = form.email.data
#             user.image_url = form.image_url.data or "/static/images/default-pic.png"
#             user.header_image_url = form.header_image_url.data or "/static/images/warbler-hero.jpg"
#             user.bio = form.bio.data

#             db.session.commit()
#             return redirect(f"/users/{user.id}")

#         flash("Wrong password, please try again.", 'danger')

#     return render_template('users/edit.html', form=form, user_id=user.id)

# @app.route('/users/delete', methods=["POST"])
# def delete_user():
#     """Delete user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     do_logout()

#     db.session.delete(g.user)
#     db.session.commit()

#     return redirect("/signup")

# @app.route('/messages/new', methods=["GET", "POST"])
# def messages_add():
#     """Add a message:

#     Show form if GET. If valid, update message and redirect to user page.
#     """

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     form = MessageForm()

#     if form.validate_on_submit():
#         msg = Message(text=form.text.data)
#         g.user.messages.append(msg)
#         db.session.commit()

#         return redirect(f"/users/{g.user.id}")

#     return render_template('messages/new.html', form=form)

# @app.route('/messages/<int:message_id>', methods=["GET"])
# def messages_show(message_id):
#     """Show a message."""

#     msg = Message.query.get_or_404(message_id)
#     return render_template('messages/show.html', message=msg)

# @app.route('/messages/<int:message_id>/delete', methods=["POST"])
# def messages_destroy(message_id):
#     """Delete a message."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     msg = Message.query.get_or_404(message_id)
#     if msg.user_id != g.user.id:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     db.session.delete(msg)
#     db.session.commit()

#     return redirect(f"/users/{g.user.id}")


# @app.errorhandler(404)
# def page_not_found(e):
#     """404 NOT FOUND page."""

#     return render_template('404.html'), 404


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

# @app.after_request
# def add_header(req):
#     """Add non-caching headers on every request."""

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers['Cache-Control'] = 'public, max-age=0'
#     return req
