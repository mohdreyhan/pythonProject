from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import ObjectId, json_util
import jwt
from datetime import datetime, timedelta


app = Flask(__name__)

# Replace 'your_secret_key' with a secret key for JWT
app.config['SECRET_KEY'] = 'your secret key'

# Replace the following with your MongoDB connection string
app.config['MONGO_URI'] = 'mongodb+srv://reyhanrab:NeedforSpeed@cluster0.ufcfhbz.mongodb.net/ebookshop'
mongo = PyMongo(app)

# Login route to generate JWT token
@app.route('/login', methods=['POST'])
def login():
    try:
        request_body = request.get_json()

        collection = mongo.db["users"]

        # Replace 'email' with the key used in your user collection
        user = collection.find_one({'email': request_body.get('email')})

        # Check if the user exists and the password is correct
        if user and user['password'] == request_body.get('password'):
            try:
                # Create JWT token
                token = jwt.encode({
                    'email': user['email'],
                    'exp': datetime.utcnow() + timedelta(minutes=30)
                }, app.config['SECRET_KEY'], algorithm='HS256')  # Specify the algorithm

                return jsonify({'token': token.decode('UTF-8')})  # Decode the token to a string
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
def get_all_books():
    try:
        collection = mongo.db["books"]
        # Access the collection to retrieve all books
        all_books = list(collection.find())
        # Convert ObjectId to string for JSON serialization
        result = json_util.dumps(all_books)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to retrieve all books from the "books" collection
@app.route('/books/<book_id>', methods=['GET'])
def get_one_books(book_id):
    try:
        collection = mongo.db["books"]
        # Convert the provided book_id string to ObjectId
        book_id = ObjectId(book_id)
        # Access the collection to retrieve all books
        book = collection.find_one({'_id': book_id})
        # Check if the book exists
        if book:
            # Convert ObjectId to string for JSON serialization
            result = json_util.dumps(book)
            return jsonify({'result': result})
        else:
            return jsonify({'message': 'Book not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to retrieve all books from the "books" collection
@app.route('/books', methods=['POST'])
def craete_book():
    try:
        request_book = request.get_json()
        collection = mongo.db["books"]
        # Insert the new record into the collection and retrieve the inserted document
        result = collection.insert_one(request_book)
        inserted_id = result.inserted_id
        inserted_book = collection.find_one({'_id': inserted_id})

        # Convert ObjectId to string for JSON serialization
        inserted_book['_id'] = str(inserted_book['_id'])

        return jsonify({'message': 'Book inserted successfully', 'book': inserted_book})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sample route to update a book by its ID
@app.route('/books/<book_id>', methods=['PATCH'])
def update_book(book_id):
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

# Sample route to delete a book by its ID
@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
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

# Sample route to retrieve data from MongoDB
@app.route('/get_users', methods=['GET'])
def get_users():
    # Replace 'your_collection_name' with the actual name of your collection
    data = mongo.db.users.find()
    result = json_util.dumps(list(data))
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
