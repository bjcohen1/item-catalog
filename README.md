README for Item Catalog Developed for Full Stack Web Developer Nanodegree

Latest Version: 6/23/2017

The purpose of this program is to set up an Item Catalog--the program can maintain lists of items organized by category.
It also provides a permissions framework that only allows the creators of a specific item to edit or delete that item.

Files included with this program:
database_setup.py--contains the database setup that will support the backend of the item catalog using SQLAlchemy
including tables for categories, items, as well as Users
project_w_user.py--contains the python code necessary to perform CRUD operations on the database
templates--contains all of the html templates necessary to render the item catalog using the Flask framework

The files also include a JSON file containing the client secret necessary for user logins.

To run this program you will need to download Virtual Box and Vagrant to support the databases
needed to use this program.  Using git you can clone all of the necessary files for this program from Udacity via 
http://github.com/udacity/fullstack-nanodegree-vm fullstack

Once the above softwares are downloaded, start the virtual machine by typing vagrant up and log in to the 
virtual machine by typing vagrant ssh.
Type cd /vagrant and cd to 'catalog_2' to access the correct folder.

To first set up the database run the database_setup.py file followed by running project_w_users.py.  At this point the
item catalog will be running at localhost:5000.  The database_setup.py file contains decorator methods to allow the data
from the database to be achieved in JSON format.

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
the url localhost:5000/gdisconnect

