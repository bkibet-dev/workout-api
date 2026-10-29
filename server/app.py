from flask import Flask, abort, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutExerciseSchema, WorkoutSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workouts',))
workout_exercise_schema = WorkoutExerciseSchema()
# Only these fields are accepted when adding an exercise to a workout.
workout_exercise_input_schema = WorkoutExerciseSchema(only=('reps', 'sets', 'duration_seconds'))


def get_or_404(model, record_id):
    """Fetch a record by primary key or abort with a JSON 404."""
    record = db.session.get(model, record_id)
    if record is None:
        abort(404, description=f'{model.__name__} {record_id} not found.')
    return record


@app.errorhandler(404)
def handle_not_found(err):
    return jsonify(error=err.description), 404


@app.errorhandler(ValidationError)
def handle_schema_error(err):
    return jsonify(errors=err.messages), 400


@app.errorhandler(ValueError)
def handle_model_error(err):
    """Raised by model @validates methods."""
    db.session.rollback()
    return jsonify(errors=str(err)), 400


@app.errorhandler(IntegrityError)
def handle_integrity_error(err):
    """Raised when a database table constraint is violated."""
    db.session.rollback()
    return jsonify(error='Database constraint violated.', detail=str(err.orig)), 409


@app.route('/workouts', methods=['GET'])
def get_workouts():
    return jsonify(workouts_schema.dump(Workout.query.all())), 200


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    return jsonify(workout_schema.dump(get_or_404(Workout, id))), 200


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = workout_schema.load(request.get_json(silent=True) or {})
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = get_or_404(Workout, id)
    db.session.delete(workout)  # cascades to its WorkoutExercises
    db.session.commit()
    return '', 204
