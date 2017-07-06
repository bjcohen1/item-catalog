import os
from flask import Flask, render_template, request, redirect, url_for
from flask import flash, jsonify
from werkzeug.utils import secure_filename
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, ListItem, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials
import httplib2
import json
from flask import make_response
import requests

Upload_Folder = '/var/www/item_catalog/item_catalog/static/img'
Allowed_Extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['Upload_Folder'] = Upload_Folder

CLIENT_ID = json.loads(
    open('/var/www/item_catalog/item_catalog/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

engine = create_engine('postgresql://catalog:a!5MrD!b@52.3.235.134/catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Making an API endpoint
@app.route('/categories/JSON')
def viewCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/categories/<int:category_id>/items/JSON')
def viewItemsJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(ListItem).filter_by(category_id=category_id).all()
    return jsonify(CategoryItems=[i.serialize for i in items])


@app.route('/categories/<int:category_id>/items/<int:item_id>/JSON')
def viewItemJSON(category_id, item_id):
    item = session.query(ListItem).filter_by(
        category_id=category_id, id=item_id)
    return jsonify(ItemDetails=[i.serialize for i in item])


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Route to facilitate the gmail login
@app.route('/gconnect', methods=['GET', 'POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/item_catalog/item_catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        respose = make_response(json.dumps
                                ('Failed to upgrade the authorization code.'),
                                401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's"), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if a user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # See if user exists, if doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ("style = width: 300px;" +
    "height: 300px;" +
    "border-radius: 150px;" +
    "-webkit-border-radius: 1500px;" +
    "-moz-border-radius: 150px;>")
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Helper method to create a new user
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Retrieve user info from the database
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Helper function to get access to userID
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Helper function to determine user upload is appropriate file format
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Allowed_Extensions


# Login decorator to check if a user is logged in when accessing a page
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            flash("You don't have permission to view that...")
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# DISCONNECT -Revoke a current user's token and reset their login_session
@app.route("/gdisconnect")
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HHTP GET request to revoke current token.
    # Access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    else:
        # For some reason the given token was invalid.
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Display the categories for the visitor to choose from--
# differs if logged in or not
@app.route('/')
@app.route('/categories/')
def listCategories():
    categories = session.query(Category).all()
    if 'username' in login_session:
        return render_template('homepage.html', categories=categories)
    else:
        return render_template('homepage_public.html', categories=categories)


# Create a new category (user is registered as owner of the category)
@app.route('/categories/newcategory', methods=['GET', 'POST'])
@login_required
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash("Category has been created!")
        return redirect(url_for('listCategories'))
    else:
        return render_template('newCategory.html')


# Method to delete a category, but only if the user owns the category
@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    if deletedCategory.user_id != login_session['user_id']:
        return """<function myFunction()
        {alert('You are not authorized to delete this category.
            Please create your own category in order to delete.');}
            </script></body onload='myFunction()''>"""

    deletedCategory = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        session.delete(deletedCategory)
        session.commit()
        flash("Category has been successfully deleted")
        return redirect(url_for('listCategories'))
    else:
        return render_template('deleteCategory.html', category=deletedCategory)


# Displays the categories in a given category
# (public and private pages depending on login status)
@app.route('/categories/<int:category_id>/items', methods=['GET', 'POST'])
def viewItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    items = session.query(ListItem).filter_by(category_id=category_id).all()

    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('viewItems_public.html',
                               category=category,
                               items=items,
                               creator=creator)
    else:
        return render_template('viewItems.html',
                               category=category,
                               items=items,
                               creator=creator)


# Create a new item, make sure picture is valid format and safe
@app.route('/categories/<int:category_id>/items/new', methods=['GET', 'POST'])
@login_required
def newItem(category_id):
    if category.user_id != login_session['user_id']:
        flash("You are not the owner of this category!")
        return redirect('/categories')

    category = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['Upload_Folder'], filename))

        newItem = ListItem(name=request.form['name'],
                           description=request.form['description'],
                           category_id=category_id,
                           user_id=login_session['user_id'],
                           picture_url=filename)
        session.add(newItem)
        session.commit()
        flash("New item has been created!")
        return redirect(url_for('viewItems', category_id=newItem.category_id))

    else:
        return render_template('newItem.html', category_id=category_id)


# Edit item, page only renders for owner of the category
@app.route('/categories/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):

    editedItem = session.query(ListItem).filter_by(
        category_id=category_id, id=item_id).one()

    if editedItem.user_id != login_session['user_id']:
        flash("You are not the owner of this category!")
        return redirect('/categories')

    if request.method == 'POST':
        file = request.files['file']
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['Upload_Folder'], filename))
            editedItem.picture_url = filename

        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Item successfully edited")
        return redirect(url_for('viewItems', category_id=category_id))
    else:
        return render_template('editItem.html', editedItem=editedItem)


# User can delete items that he/she created
@app.route('/categories/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_id, item_id):

    deleteItem = session.query(ListItem).filter_by(
        category_id=category_id, id=item_id).one()

    if deleteItem.user_id != login_session['user_id']:
        flash("You are not the owner of this category!")
        return redirect('/categories')

    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash("Item has been deleted")
        return redirect(url_for('viewItems',
                        category_id=deleteItem.category_id))

    else:
        return render_template('deleteItem.html',
                               category_id=category_id, item_id=item_id,
                               deleteItem=deleteItem)

if __name__ == '__main__':
    app.secret_key = '3aRz!dLq9Cx4F'
    app.debug = True
    app.run(host='0.0.0.0', port=2200)
