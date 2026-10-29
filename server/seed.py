#!/usr/bin/env python3

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Clearing existing data...')
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print('Seeding exercises...')
    exercises = [
        Exercise(name='Push-up', category='strength', equipment_needed=False),
        Exercise(name='Barbell Squat', category='strength', equipment_needed=True),
        Exercise(name='Running', category='cardio', equipment_needed=False),
        Exercise(name='Jump Rope', category='cardio', equipment_needed=True),
        Exercise(name='Plank', category='strength', equipment_needed=False),
        Exercise(name='Hamstring Stretch', category='flexibility', equipment_needed=False),
    ]
    db.session.add_all(exercises)
    db.session.commit()
    pushup, squat, running, rope, plank, stretch = exercises

    print('Seeding workouts...')
    workouts = [
        Workout(date=date(2026, 10, 26), duration_minutes=45, notes='Full-body strength session'),
        Workout(date=date(2026, 10, 27), duration_minutes=30, notes='Cardio and core'),
        Workout(date=date(2026, 10, 28), duration_minutes=20, notes='Recovery and mobility'),
    ]
    db.session.add_all(workouts)
    db.session.commit()
    w1, w2, w3 = workouts

    print('Linking exercises to workouts...')
    links = [
        WorkoutExercise(workout=w1, exercise=pushup, sets=3, reps=15),
        WorkoutExercise(workout=w1, exercise=squat, sets=4, reps=8),
        WorkoutExercise(workout=w1, exercise=plank, sets=3, duration_seconds=60),
        WorkoutExercise(workout=w2, exercise=running, duration_seconds=1200),
        WorkoutExercise(workout=w2, exercise=rope, sets=5, duration_seconds=120),
        WorkoutExercise(workout=w2, exercise=plank, sets=2, duration_seconds=45),
        WorkoutExercise(workout=w3, exercise=stretch, sets=2, duration_seconds=30),
    ]
    db.session.add_all(links)
    db.session.commit()

    print('Done seeding!')
