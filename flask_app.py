from flask import Flask, render_template
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

@app.route('/<person_id>')
def person_details(person_id):
    client = MongoClient('localhost', 27017)
    db = client['tax_calculator']
    tax_cards_collection = db['clients']
    tax_card = tax_cards_collection.find_one({"_id": ObjectId(person_id)})
    return render_template('person_details.html', tax_card=tax_card)

if __name__ == '__main__':
    app.run(debug=True)


