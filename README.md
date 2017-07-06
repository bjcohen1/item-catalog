README for Item Catalog Developed for Full Stack Web Developer Nanodegree

Latest Version: 7/6/2017

The purpose of this program is to set up an Item Catalog hosted on an AWS LightSail web server--the program can maintain lists of items organized by category.
It also provides a permissions framework that only allows the creators of a specific item to edit or delete that item.

Files included with this program:
database_setup.py--contains the database setup that will support the backend of the item catalog using SQLAlchemy
including tables for categories, items, as well as Users
__init__.py--contains the python code necessary to link to the PSQL database and perform CRUD operations on the database
templates--contains all of the html templates necessary to render the item catalog using the Flask framework. The database_setup.py 
file contains decorator methods to allow the data from the database to be archieved in JSON format.

The files also include a JSON file containing the client secret necessary for user logins with Google.

The IP address of this project can be found at 52.3.235.134

The AWS LightSail server was configured by installing Apache2, Flask and PostgreSQL.
To configure the app the app's .conf file was set to specify the IP address of the
project, the WSGI script location for serving the app using Flask and customizations
for apache2 error logs as well as aliases for file paths.

The WSGI file to serve the Flask app was also configured to indicate where the
app files are located.

The server firewall was reconfigured to only allow ssh on port 2200 and only using RSA
key authentication. 

This catalog supports a number of manipulations of the database at the following urls:

/login : Brings the user to the initail login allowing for log in or account creation through gmail

/ or /categories: Renders all of the categories of items currently in the database which contains links
	to view the items in those categories

The file also contains dedicated links to view items, create new items, edit exisitng items
	and delete existing items.  The user is advised to use the hyperlinks on the pages
	to access these pages because accessing them directly requires knowledge of category
	and item id numbers

The pages for editing/deleting items are protected to ensure that only the owner of those
items edits/deletes.  Further, a user may only create a new category after logging in
with his or her account.

When creating a new item a user will be requested to include a name, description, and picture
of the item for the catalog.  The picture can be in the following file types:
txt, pdf, png, jpg, jpeg, gif.

Once logged in a user will see a link to logout, but can also do so by accessing 
the IP/gdisconnect.

