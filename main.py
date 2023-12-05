from flask import Flask, jsonify
from flask_pymongo import PyMongo
from bson import json_util

app = Flask(__name__)

# Replace the following with your MongoDB connection string
app.config['MONGO_URI'] = 'mongodb+srv://reyhanrab:NeedforSpeed@cluster0.ufcfhbz.mongodb.net/Cluster0'
mongo = PyMongo(app)

# Sample route to check if the connection to MongoDB is successful
@app.route('/check_connection', methods=['GET'])
def check_connection():
    try:
        # Access a collection to check the connection
        collections = mongo.db.list_collection_names()
        return jsonify({'message': 'Connection to MongoDB successful!', 'result': collections})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sample route to retrieve data from MongoDB
@app.route('/get_users', methods=['GET'])
def get_data():
    # Replace 'your_collection_name' with the actual name of your collection
    data = mongo.db.users.find()
    result = json_util.dumps(list(data))
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
