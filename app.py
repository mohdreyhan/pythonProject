from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import ObjectId, json_util
import jwt
from datetime import datetime, timedelta
from decorators import token_required  # Import the decorator from the decorators file
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)

# Replace 'your_secret_key' with a secret key for JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Replace the following with your MongoDB connection string
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

# Signup route to create a new user
@app.route('/signup', methods=['POST'])
def signup():
    try:
        request_body = request.get_json()

        collection = mongo.db["users"]

        # Check if the email is already registered
        existing_user = collection.find_one({'email': request_body.get('email')})
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400

        # Hash the password before storing it
        hashed_password = generate_password_hash(request_body.get('password'), method='pbkdf2:sha256')

        request_body["password"] = hashed_password

        # Insert the new user into the collection

        new_user = collection.insert_one(request_body)

        # Extract the relevant information for response
        response_data = {
            'message': "Sign Up Successful",
            'user_id': str(new_user.inserted_id)
        }
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Login route to generate JWT token
@app.route('/login', methods=['POST'])
def login():
    try:
        request_body = request.get_json()

        collection = mongo.db["users"]

        # Replace 'email' with the key used in your user collection
        user = collection.find_one({'email': request_body.get('email')})

        # Check if the user exists and the password is correct
        if user and check_password_hash(user['password'], request_body.get('password')):
            try:
                # Create JWT token
                token = jwt.encode({
                    'email': user['email'],
                    'exp': datetime.utcnow() + timedelta(minutes=30)
                }, app.config['SECRET_KEY'], algorithm='HS256')  # Specify the algorithm

                if not isinstance(token, bytes):
                    return jsonify({'token': token})  # No need to decode, assuming token is already a string
       
                return jsonify({'token': token.decode('UTF-8')}) 
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sample route to check if the connection to MongoDB is successful
@app.route('/check_connection', methods=['GET'])
def check_connection():
    try:
        # Access a collection to check the connection
        collections = mongo.db.list_collection_names()
        return jsonify({'message': 'Connection to MongoDB successful!', 'result': collections})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to retrieve all books from the "books" collection
@app.route('/books', methods=['GET'])
@token_required
def get_all_books(data):
    try:
        collection = mongo.db["books"]
        # Access the collection to retrieve all books
        all_books = list(collection.find())
        # Convert ObjectId to string for JSON serialization
        for book in all_books:
            book['_id'] = str(book['_id'])
        return jsonify({'result': all_books})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to update a book from the "books" collection
@app.route('/books/<book_id>', methods=['GET'])
@token_required
def get_one_books(data, book_id):
    try:
        collection = mongo.db["books"]
        # Convert the provided book_id string to ObjectId
        book_id = ObjectId(book_id)
        # Access the collection to retrieve all books
        book = collection.find_one({'_id': book_id})
        # Check if the book exists
        if book:
            # Convert ObjectId to string for JSON serialization
            book['_id'] = str(book['_id'])
            return jsonify({'message': "Book found", 'result': book})
        else:
            return jsonify({'message': 'Book not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to create a book in the "books" collection
@app.route('/books', methods=['POST'])
@token_required
def craete_book(data):
    try:
        request_book = request.get_json()
        collection = mongo.db["books"]
        print(collection)
        # Insert the new record into the collection and retrieve the inserted document
        result = collection.insert_one(request_book)
        inserted_id = result.inserted_id
        inserted_book = collection.find_one({'_id': inserted_id})

        # Convert ObjectId to string for JSON serialization
        inserted_book['_id'] = str(inserted_book['_id'])

        return jsonify({'message': 'Book inserted successfully', 'book': inserted_book})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to update a book by its ID
@app.route('/books/<book_id>', methods=['PATCH'])
@token_required
def update_book(data, book_id):
    try:
        # Access the "books" collection
        collection = mongo.db.books

        # Convert the provided book_id string to ObjectId
        book_id = ObjectId(book_id)

        # Extract data from the request
        data = request.get_json()

        # Update the book record based on its ID
        result = collection.update_one({'_id': book_id}, {'$set': data})

        # Check if the update was successful
        if result.modified_count > 0:
            # Retrieve the updated document
            updated_book = collection.find_one({'_id': book_id})
            # Convert ObjectId to string for JSON serialization
            updated_book['_id'] = str(updated_book['_id'])
            return jsonify({'message': 'Book updated successfully', 'book': updated_book})
        else:
            return jsonify({'message': 'Book not found or no changes made'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to delete a book by its ID
@app.route('/books/<book_id>', methods=['DELETE'])
@token_required
def delete_book(data, book_id):
    try:
        # Access the "books" collection
        collection = mongo.db.books

        # Convert the provided book_id string to ObjectId
        book_id = ObjectId(book_id)

        # Check if the book exists before deletion
        existing_book = collection.find_one({'_id': book_id})
        if existing_book:
            # Delete the book record based on its ID
            result = collection.delete_one({'_id': book_id})
            # Check if the deletion was successful
            if result.deleted_count > 0:
                return jsonify({'message': 'Book deleted successfully'})
            else:
                return jsonify({'message': 'Book not found or could not be deleted'}), 404
        else:
            return jsonify({'message': 'Book not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
