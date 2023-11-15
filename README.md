After downloading the repository you should run it through Docker, I added dockerfile. you will use the project through Docker
after the following commands (Through either terminal or command-line):
1. pip install Flask-BasicAuth 
2. docker build -t project .
3. docker run project

download postmen:
you should download postmen agent in order to be able to write POST requests


after running it, you should authenticate, in GET requests (all_users function only) you can simply write name and
password once (username: David, password: Hadad) after opening and you will count as logged in, in POST requests I used postmen.
To authenticate with postmen you should press the tab "Authorization" then in type select "basic authenticate" 
then write username and password as specified.
in order to make POST requests in postmen you should go to headers and press on bulk edit, then write "Content-Type:application/json" then press on
key-value edit. thats means we send and receive content in json format.

In order to use endpoint you need to add the ending "some_endpoint" to the url, for example if you want to delete user you can use
http://127.0.0.1:5000/delete_user.

--Delete endpoint: /delete_user --
the key in my database is the email, so in order to delete user you need to specify his email in json format, like
{"email":"david@gmail.com"}, you sould write it in postmen in body->raw (and thats goes for every other function as well)

--Add user: /add_user --
in order to add we need json with three parts, username email and password.

--Edit user: /edit_user -- 
in order to edit we need to have the user old email so we can find him and at least one from: new_email, new_username, new_password,
so the json will look like {*mandatory* "old_email":"d@gmail.com", *optional*: "new_email":"some email" and username password optional here as well}

--Find duplicates: /find_duplicates -- 
to find duplicates we can use either mail username or password or any combination, when used with email this will only give us one user
because email is a key, the json will look like adding user, only in this case the fields will be optional
