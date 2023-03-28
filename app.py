from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os

# Set up Flask app, SQLAlchemy, and Marshmallow
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'student.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Create Student model
class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    dob = db.Column(db.Date)
    amount_due = db.Column(db.Float)

    def __init__(self, first_name, last_name, dob, amount_due):
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.amount_due = amount_due

# Create Student schema
class StudentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Student

# Initialize schema instances
student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

# Create CRUD routes
@app.route('/students', methods=['GET'])
def get_students():
    all_students = Student.query.all()
    return students_schema.jsonify(all_students)

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    return student_schema.jsonify(student)

@app.route('/students', methods=['POST'])
def add_student():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    dob = datetime.strptime(request.json['dob'], '%Y-%m-%d').date()
    amount_due = request.json['amount_due']
    new_student = Student(first_name, last_name, dob, amount_due)
    db.session.add(new_student)
    db.session.commit()
    return student_schema.jsonify(new_student)

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = Student.query.get(student_id)
    if student:
        student.first_name = request.json['first_name']
        student.last_name = request.json['last_name']
        student.dob = datetime.strptime(request.json['dob'], '%Y-%m-%d').date()
        student.amount_due = request.json['amount_due']
        db.session.commit()
        return student_schema.jsonify(student)
    else:
        return jsonify({'message': 'Student not found'}), 404

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        return student_schema.jsonify(student)
    else:
        return jsonify({'message': 'Student Deleted'}), 404

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database created!")
        except:
            print("Database already exists!")
    app.run(debug=True)
