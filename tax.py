# Create an income tax calculator: 
#  - Generate at least 500 documents , with fields: name, surname, date of birth , age (determined from date of birth), 
# anual salary before tax (EUR, round to 2 numbers after comma)
#  - Create a CLI application that would let us get first 10 people from database within the age bracket 
# [min_age, max_age]
#  - Those people name surname and age should be shown as an option to choose.
#  - When one of ten options is chosen, there should be calculated tax return 
# (it should be created a document as a tax card, values taken from database). 
# Lets say GPM tax is 20% and HealtTax is 15% from 90% of the income left after GPM deduction.
#  - The final values should be show and wrriten to database (like a generated data and taxes paid, take home pay etc.) 
# and portrayed in a web page (use flask and docker, show the url were to click )

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Dict
from bson import ObjectId
# import random
# from faker import Faker
# from datetime import datetime, date


class MongoRepresentater:
    def __init__(self, host: str, port: int, db_name: str) -> Database:
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = MongoClient(host, port)
        self.database = self.client[db_name]

    def insert_document(self, collection: Collection, document: Dict) -> str:
        collection = self.database[collection]
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def find_documents_by_age_range(self, collection: Collection, min_age: int, max_age: int) -> Dict:
        collection = self.database[collection]
        query = {"age": {"$gte": min_age, "$lte": max_age}}
        documents = collection.find(query)
        return list(documents)

    def update_tax_return(self, collection: Collection, person_id: str, gpm_tax: float, health_tax: float, take_home_pay: float) -> None:
        collection = self.database[collection]
        query = {"_id": ObjectId(person_id)}
        update = {"$set": {"gpm_tax": gpm_tax, "health_tax": health_tax, "take_home_pay": take_home_pay}}
        collection.update_one(query, update)


def calculate_tax_return(salary: float) -> float:
    gpm_tax_rate = 0.2
    health_tax_rate = 0.15
    gpm_tax = round(salary * gpm_tax_rate, 2)
    salary_after_gpm = round(salary - gpm_tax,2)
    health_tax = round(salary_after_gpm * health_tax_rate, 2)
    take_home_pay = round(salary_after_gpm - health_tax, 2)
    return gpm_tax, health_tax, take_home_pay


if __name__ == "__main__":

    mongo_representer = MongoRepresentater(host='localhost', port=27017, db_name='tax_calculator')

    collection = 'clients'
    # iteration = 500

    # fake = Faker()
    # today = date.today()

    # for _ in range(iteration):
    #     date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=90)
    #     date_of_birth_date = datetime(date_of_birth.year, date_of_birth.month, date_of_birth.day)
    #     age = today.year - date_of_birth_date.year - ((today.month, today.day) < (date_of_birth_date.month, date_of_birth_date.day))

    #     document = {
    #         "name": fake.first_name(),
    #         "surname": fake.last_name(),
    #         "date_of_birth": date_of_birth_date,
    #         "age": age,
    #         "salary": round(random.uniform(1000, 5000), 2)
    #     }
    #     inserted_id = mongo_representer.insert_document(collection, document)
    #     print(f"Inserted document with ID: {inserted_id}")

    while True:
        try:
            min_age = int(input("Enter minimum age: "))
            max_age = int(input("Enter maximum age: "))

            if min_age < 0 or max_age < 0 or min_age > max_age:
                raise ValueError("Invalid age range")

            documents = mongo_representer.find_documents_by_age_range(collection, min_age, max_age)
            print("People within the specified age range:")
            for index, doc in enumerate(documents[:10], 1):
                print(f"{index}. {doc['name']} {doc['surname']}, Age: {doc['age']}")

        except ValueError as ve:
            print(ve)
        
        choice = input("Please choose the person: ")
        
        try:
            choice_index = int(choice) - 1
            if choice_index < 0 or choice_index >= len(documents[:10]):
                raise ValueError("Invalid choice")

            selected_person = documents[choice_index]
            person_id = str(selected_person['_id'])
            # cursor = collection.find({"_id": ObjectId(person_id)})
           
            # for doc in cursor:
            #     print(doc)

            url = f"http://127.0.0.1:5000/{person_id}"
            print(f"Tax details URL: {url}")
            salary = selected_person['salary']
            gpm_tax, health_tax, take_home_pay = calculate_tax_return(salary)
            mongo_representer.update_tax_return(collection, person_id, gpm_tax, health_tax, take_home_pay)

            print(f"Tax details for {selected_person['name']} {selected_person['surname']}:")
            print(f"- GPM tax: {gpm_tax}")
            print(f"- Health tax: {health_tax}")
            print(f"- Take home pay: {take_home_pay}")

        except ValueError as ve:
            print(ve)

        decision = input("Do you want to choose another person? (yes/no): ").lower()
        if decision != "yes":
            break
