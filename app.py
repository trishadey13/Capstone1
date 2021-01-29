import os
import requests
import random
from flask import Flask, render_template, request, flash, redirect, abort, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from forms import SearchForm, UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, Recipe, Like

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

##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")

##############################################################################
# Homepage

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

        all_ids = [r_id,p_id,h_id]
        for x in all_ids:
            if (db.session.query(Recipe.id).filter_by(id=x).scalar() is None):
                recipe = Recipe(id=x)
                db.session.add(recipe)
        db.session.commit()

        all_recipe_ids += f'{r_id},{p_id},{h_id},'
    
    all_results = requests.get(f'{SPOON_API}/recipes/informationBulk?ids={all_recipe_ids}&apiKey={API_KEY}').json()
    
    likes = []
    for like in g.user.likes:
        likes.append(like.id)
    
    return render_template('home.html', rand_results=all_results[:5], pop_results=all_results[5:10], health_results=all_results[10:], likes=likes)

##############################################################################
# Searching

@app.route('/search-results', methods=['GET', 'POST'])
def get_search_results():

    formdata = request.form['q']
    req_data = requests.get(f'{SPOON_API}/recipes/autocomplete?query={formdata}&apiKey={API_KEY}').json()
    
    all_recipe_ids = ""
    for result in req_data:
        r_id = result['id']
        if (db.session.query(Recipe.id).filter_by(id=r_id).scalar() is None):
                recipe = Recipe(id=r_id)
                db.session.add(recipe)
        all_recipe_ids += f'{r_id},'

    db.session.commit()

    if not all_recipe_ids:
        no_results = "No results found!"
        return render_template('search.html', no_results=no_results)

    all_results = requests.get(f"{SPOON_API}/recipes/informationBulk?ids={all_recipe_ids}&apiKey={API_KEY}").json()

    likes = []
    for like in g.user.likes:
        likes.append(like.id)

    return render_template('search.html', all_results=all_results, likes=likes)
    
@app.route('/search-results-filter', methods=['POST'])
def get_search_results_with_filters():
    cuisine = '&'
    meal_type='&'
    ingredients = '&'

    if 'cuisine' in request.form:
        cuisine = f"&cuisine={request.form['cuisine']}"
    
    if 'type' in request.form:
        meal_type = f"&type={request.form['type']}"

    if 'ingredients' in request.form:
        ingredients = f"&includeIngredients={request.form['ingredients']}"

    filtered_recipes = requests.get(f'{SPOON_API}/recipes/complexSearch?apiKey={API_KEY}{cuisine}{type}{ingredients}').json()['results']

    all_recipe_ids = ""
    for result in filtered_recipes:
        r_id = result['id']
        if (db.session.query(Recipe.id).filter_by(id=r_id).scalar() is None):
                recipe = Recipe(id=r_id)
                db.session.add(recipe)
        all_recipe_ids += f'{r_id},'
    
    db.session.commit()

    if not all_recipe_ids:
        no_results = "No results found!"
        return render_template('search.html', no_results=no_results)

    all_results = requests.get(f"{SPOON_API}/recipes/informationBulk?ids={all_recipe_ids}&apiKey={API_KEY}").json()
    
    return render_template('search.html', all_results=all_results)

##############################################################################
# User profile/edit/delete

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    liked_ids = ""
    
    for recipe in g.user.likes:
        liked_ids += f'{recipe.id},'

    liked_recipes = requests.get(f"{SPOON_API}/recipes/informationBulk?ids={liked_ids}&apiKey={API_KEY}").json()
    
    return render_template('users/detail.html', user=user, liked_recipes=liked_recipes)

@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or "/static/images/default-pic.png"

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

##############################################################################
# User recipe like

@app.route('/like', methods=['POST'])
def like_recipe():

    recipe_id = request.get_json()['body']['recipeId']
    liked = request.get_json()['body']['liked']
    liked_recipe = Recipe.query.filter(Recipe.id==recipe_id).first()
    user_likes = g.user.likes

    # if unliked
    if not liked:
        g.user.likes = [like for like in user_likes if like != liked_recipe]      
    else: 
        g.user.likes.append(liked_recipe)

    db.session.commit()

    return redirect("/")

##############################################################################
# Error page

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404

##############################################################################
# Turn off all caching in Flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req