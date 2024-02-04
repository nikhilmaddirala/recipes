from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv
from dotenv import load_dotenv
from fetch_videos import *

load_dotenv()  # Load environment variables from a .env file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL', 'sqlite:///recipes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)

db.create_all()

@app.route('/recipes', methods=['POST'])
def add_recipe():
    data = request.get_json()
    new_recipe = Recipe(title=data['title'], ingredients=data['ingredients'], instructions=data['instructions'])
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe added successfully'}), 201

@app.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    output = []
    for recipe in recipes:
        recipe_data = {'title': recipe.title, 'ingredients': recipe.ingredients, 'instructions': recipe.instructions}
        output.append(recipe_data)
    return jsonify({'recipes': output})

if __name__ == '__main__':
    app.run(debug=True)
    remington_james_channel_id = 'UCO9Rhj_x_GgJl-Ria7257EA'  # Replace with the actual channel ID of Remington James
    insert_video_data(remington_james_channel_id)



