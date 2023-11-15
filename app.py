import sqlite3
from functools import wraps
from flask import Flask, request, jsonify, make_response

# constants and config app
USERNAME = "David"
PASSWORD = "Hadad"
app = Flask(__name__)

# Connect to the SQLite database (creates a new file if it doesn't exist)
def create_db():
    """
    Create or connect to the SQLite database.

    @return: None
    """
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT NOT NULL,
        mail TEXT PRIMARY KEY NOT NULL,
        password TEXT NOT NULL
    );
    ''')
    db.commit()
    db.close()

# Basic authentication decorator
def auth_required(func):
    """
    Decorator to require basic authentication for the specified route.

    @param: func - The inner function to be decorated.
    @return: The decorated function.
    @exception: Returns 'Access Denied' with 401 status if authentication fails.
    """
    @wraps(func)
    def decorated_func(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == USERNAME and auth.password == PASSWORD:
            # if authorized, do what the inner function should have done
            return func(*args, **kwargs)
        # not authorized case
        return make_response('Access Denied', 401, {'www-Authenticate': 'Basic Realm="Login required"'})

    return decorated_func

@app.route('/')
@auth_required
def hello_world():
    """
    Route to greet the world.

    @return: Hello World!
    """
    return "Hello World!"

@app.route('/add_user', methods=['POST'])
@auth_required
def add_user():
    """
    Route to add a new user.

    @param: None
    @return: JSON response with a message or an error if the data is incomplete.
    """
    data = request.json

    # Extract user details from the request data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Perform basic validation
    if not username or not email or not password:
        return jsonify({'error': 'Incomplete user data'}), 400

    # Connect to the SQLite database
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    # Insert the new user into the database
    cursor.execute('INSERT INTO users (username, mail, password) VALUES (?, ?, ?)', (username, email, password))
    db.commit()
    db.close()

    return jsonify({'message': 'User added successfully'}), 201

@app.route('/delete_user', methods=['POST'])
@auth_required
def delete_user():
    """
    Route to delete a user.

    @param: None
    @return: JSON response with a message or an error if the data is incomplete or the user is not found.
    """
    # get access to the database
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    data = request.json
    email = data.get('email')

    # Perform basic validation
    if not email:
        return jsonify({'error': 'Incomplete user data'}), 400

    # Check if the user with the provided email exists
    cursor.execute('SELECT * FROM users WHERE mail = ?', (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Delete the user with the provided email
    cursor.execute('DELETE FROM users WHERE mail = ?', (email,))
    db.commit()
    db.close()

    return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/all_users', methods=['GET'])
@auth_required
def all_users():
    """
    Route to get all users.

    @param: None
    @return: JSON response with a list of users.
    """
    # get access to the database
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    # Fetch all users from the database
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    # Close the database connection
    db.close()

    # Convert the users to a list of dictionaries so we can make it json
    users_list = [{'username': user[0], 'email': user[1], 'password': user[2]} for user in users]

    return jsonify(users_list)

@app.route('/edit_user', methods=['POST'])
@auth_required
def edit_user():
    """
    Route to edit a user.

    @param: None
    @return: JSON response with a message or an error if the data is incomplete or the user is not found.
    """
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    data = request.json

    # Extract details from the request data
    # email is the key, so we have to have old email
    old_email = data.get('old_email')
    new_username = data.get('new_username')
    new_email = data.get('new_email')
    new_password = data.get('new_password')

    # email is the key, so we have to have old email
    if not old_email:
        return jsonify({'error': 'Old email is mandatory'}), 400

    # Check if the user with the provided old email exists
    cursor.execute('SELECT * FROM users WHERE mail = ?', (old_email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # at least one new value - else we have nothing to update
    if not new_username and not new_email and not new_password:
        return jsonify({'error': 'Nothing to update'}), 404

    update_query, update_values = create_query_edit(new_email, new_password, new_username, old_email)

    # Execute the update query
    cursor.execute(update_query, tuple(update_values))
    db.commit()
    db.close()
    return jsonify({'message': 'User updated successfully'}), 200


def create_query_edit(new_email, new_password, new_username, old_email):
    """
        @param: new_email, new_password, new_username, old_email
        @return: sql query and all the values that we need to edit to
    """
    # if we gor here we should update something, anything that should be
    # updated will be in the sql query
    update_query = 'UPDATE users SET'
    update_values = []
    # This mechanism helps us to define the sql query based on the info we got
    if new_username:
        update_query += ' username = ?,'
        update_values.append(new_username)
    if new_email:
        update_query += ' mail = ?,'
        update_values.append(new_email)
    if new_password:
        update_query += ' password = ?,'
        update_values.append(new_password)
    # Remove the trailing comma and add the where clause which the old email
    update_query = update_query.rstrip(',') + ' WHERE mail = ?;'
    update_values.append(old_email)
    return update_query, update_values


####bonus
@app.route('/find_duplicates', methods=['POST'])
@auth_required
def find_duplicates():
    """
        @param: None
        @return: users that have common property, or error
        @exception: Returns error if we got no identifier.

    """
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    data = request.json

    # Extract details from the request data
    name = data.get('name')
    password = data.get('password')
    email = data.get('email')

    # Check if either name or password is provided
    if not name and not password and not email:
        return jsonify({'error': 'At least one identifier must be provided'}), 400

    query, values = find_duplicates_query(email, name, password)

    # Execute the query
    cursor.execute(query, tuple(values))
    users = cursor.fetchall()
    db.close()

    # Convert the users to a list of dictionaries, so we can jsonify
    users_list = [{'username': user[0], 'email': user[1], 'password': user[2]} for user in users]
    return jsonify(users_list)


def find_duplicates_query(email, name, password):
    """
        @param: email, password, name
        @return: sql query and all the values that we need to check whether users with them
    """
    # This mechanism helps us to define the sql query based on the info we got
    query = 'SELECT * FROM users WHERE'
    values = []
    if name:
        query += ' username = ?'
        values.append(name)
    if password:
        if name:
            query += ' AND'  # Add AND if both name and password are provided
        query += ' password = ?'
        values.append(password)
    if email:
        if name or password:
            query += ' AND'
        query += ' email = ?'
        values.append(email)
    query += ';'
    return query, values


if __name__ == '__main__':
    create_db()
    app.run(debug=True)
