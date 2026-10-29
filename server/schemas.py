from marshmallow import Schema, ValidationError, fields, validate, validates, validates_schema

from models import EXERCISE_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.OneOf(EXERCISE_CATEGORIES))
    equipment_needed = fields.Bool(load_default=False)
    workouts = fields.Nested(
        'WorkoutSchema', many=True, exclude=('workout_exercises',), dump_only=True
    )

    @validates('name')
    def validate_name_not_blank(self, value):
        if not value.strip():
            raise ValidationError('Name cannot be blank.')


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, strict=True, validate=validate.Range(min=1))
    notes = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=1000))
    workout_exercises = fields.Nested(
        'WorkoutExerciseSchema', many=True, exclude=('workout',), dump_only=True
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(strict=True, allow_none=True, load_default=None, validate=validate.Range(min=1))
    sets = fields.Int(strict=True, allow_none=True, load_default=None, validate=validate.Range(min=1))
    duration_seconds = fields.Int(
        strict=True, allow_none=True, load_default=None, validate=validate.Range(min=1)
    )
    workout = fields.Nested('WorkoutSchema', exclude=('workout_exercises',), dump_only=True)
    exercise = fields.Nested('ExerciseSchema', exclude=('workouts',), dump_only=True)

    @validates_schema
    def validate_reps_or_duration(self, data, **kwargs):
        if data.get('reps') is None and data.get('duration_seconds') is None:
            raise ValidationError('Provide reps (with sets) or duration_seconds.')
        if data.get('reps') is not None and data.get('sets') is None:
            raise ValidationError('sets is required when reps is provided.', field_name='sets')
