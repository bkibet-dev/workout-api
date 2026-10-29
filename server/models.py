from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()

EXERCISE_CATEGORIES = ('strength', 'cardio', 'flexibility', 'balance', 'mobility')


def _is_positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


class Exercise(db.Model):
    __tablename__ = 'exercises'
    __table_args__ = (
        db.UniqueConstraint('name', name='uq_exercises_name'),
        db.CheckConstraint('length(trim(name)) > 0', name='ck_exercises_name_not_blank'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Deleting an exercise also deletes its join rows.
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan'
    )
    # Read-only shortcut: exercise.workouts -> list of Workout objects.
    workouts = association_proxy('workout_exercises', 'workout')

    @validates('name')
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Exercise name must be a non-empty string.')
        return value.strip()

    @validates('category')
    def validate_category(self, key, value):
        if not isinstance(value, str) or value.strip().lower() not in EXERCISE_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(EXERCISE_CATEGORIES)}.")
        return value.strip().lower()

    @validates('equipment_needed')
    def validate_equipment_needed(self, key, value):
        if not isinstance(value, bool):
            raise ValueError('equipment_needed must be true or false.')
        return value


class Workout(db.Model):
    __tablename__ = 'workouts'
    __table_args__ = (
        db.CheckConstraint('duration_minutes > 0', name='ck_workouts_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Deleting a workout also deletes its join rows.
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout', cascade='all, delete-orphan'
    )
    # Read-only shortcut: workout.exercises -> list of Exercise objects.
    exercises = association_proxy('workout_exercises', 'exercise')

    @validates('date')
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError('Workout date must be a valid date.')
        return value

    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if not _is_positive_int(value):
            raise ValueError('duration_minutes must be a positive integer.')
        return value


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    __table_args__ = (
        db.CheckConstraint('reps IS NULL OR reps > 0', name='ck_we_reps_positive'),
        db.CheckConstraint('sets IS NULL OR sets > 0', name='ck_we_sets_positive'),
        db.CheckConstraint(
            'duration_seconds IS NULL OR duration_seconds > 0', name='ck_we_duration_positive'
        ),
        db.CheckConstraint(
            'reps IS NOT NULL OR duration_seconds IS NOT NULL', name='ck_we_reps_or_duration'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    @validates('reps', 'sets', 'duration_seconds')
    def validate_positive(self, key, value):
        if value is not None and not _is_positive_int(value):
            raise ValueError(f'{key} must be a positive integer.')
        return value
