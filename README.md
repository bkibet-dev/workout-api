# Workout Tracker API

A Flask REST API for personal trainers to create workouts, build a reusable library of exercises, and attach exercises to workouts with sets, reps or duration. Built with Flask, SQLAlchemy, Flask-Migrate and Marshmallow.

## Data model

- **Exercise**: `id`, `name`, `category`, `equipment_needed`
- **Workout**: `id`, `date`, `duration_minutes`, `notes`
- **WorkoutExercise** (join table): `id`, `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds`

A workout has many exercises through workout exercises, and an exercise has many workouts through workout exercises.

## Installation

Requires Python 3.8+ and Pipenv.

~~~bash
git clone git@github.com:bkibet-dev/workout-api.git
cd workout-api
pipenv install
pipenv shell
cd server
flask db upgrade head
python seed.py
~~~

## Running the app

~~~bash
cd server
python app.py
~~~

The API runs at `http://localhost:5555` (or use `flask run --port 5555`).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Show one workout with its exercises, including reps/sets/duration |
| POST | `/workouts` | Create a workout (`date` as YYYY-MM-DD, `duration_minutes`, optional `notes`) |
| DELETE | `/workouts/<id>` | Delete a workout and its associated workout exercises |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show one exercise with the workouts it appears in |
| POST | `/exercises` | Create an exercise (`name`, `category`, optional `equipment_needed`) |
| DELETE | `/exercises/<id>` | Delete an exercise and its associated workout exercises |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout (`reps` + `sets`, and/or `duration_seconds`) |

Valid categories: strength, cardio, flexibility, balance, mobility.

## Validation

- **Table constraints**: unique exercise names, non-blank names, positive durations, reps and sets, and reps or duration required on every workout exercise.
- **Model validations**: type, range and category checks via SQLAlchemy `@validates`.
- **Schema validations**: Marshmallow field validators plus a schema-level check for reps/sets/duration.

Errors return JSON with status 400 (invalid data), 404 (not found) or 409 (constraint violation).
