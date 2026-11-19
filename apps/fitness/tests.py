from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.dailydash.services import get_or_create_day

from .models import Exercise, ExerciseCategory, FoodLogEntry, Recipe, WorkoutSet


class ExerciseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.client.force_login(self.user)
        self.brust = ExerciseCategory.objects.get(code=ExerciseCategory.BRUST)
        self.trizeps = ExerciseCategory.objects.get(code=ExerciseCategory.TRIZEPS)

    def test_exercise_can_have_multiple_categories(self):
        exercise = Exercise.objects.create(user=self.user, name="Bankdrücken")
        exercise.categories.set([self.brust, self.trizeps])
        self.assertEqual(exercise.categories.count(), 2)

    def test_deactivate_keeps_exercise_and_history(self):
        exercise = Exercise.objects.create(user=self.user, name="Liegestütze")
        day = get_or_create_day(self.user, timezone.localdate())
        WorkoutSet.objects.create(user=self.user, exercise=exercise, day=day, set_number=1, reps=10)

        response = self.client.post(reverse("fitness:exercise-deactivate", kwargs={"pk": exercise.pk}))
        self.assertEqual(response.status_code, 302)
        exercise.refresh_from_db()
        self.assertFalse(exercise.active)
        self.assertTrue(WorkoutSet.objects.filter(exercise=exercise).exists())


class WorkoutSetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pw")
        self.exercise = Exercise.objects.create(user=self.user, name="Latzug")
        self.day = get_or_create_day(self.user, timezone.localdate())

    def test_duplicate_set_number_rejected(self):
        WorkoutSet.objects.create(user=self.user, exercise=self.exercise, day=self.day, set_number=1, reps=10)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WorkoutSet.objects.create(
                    user=self.user, exercise=self.exercise, day=self.day, set_number=1, reps=8
                )

    def test_bodyweight_exercise_allows_null_weight(self):
        workout_set = WorkoutSet.objects.create(
            user=self.user, exercise=self.exercise, day=self.day, set_number=1, reps=12, weight_kg=None
        )
        self.assertIsNone(workout_set.weight_kg)


class WorkoutDayViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="carol", password="pw")
        self.client.force_login(self.user)
        self.beine = ExerciseCategory.objects.get(code=ExerciseCategory.BEINE)
        self.brust = ExerciseCategory.objects.get(code=ExerciseCategory.BRUST)
        self.leg_press = Exercise.objects.create(user=self.user, name="Beinpresse", equipment_number="12")
        self.leg_press.categories.add(self.beine)
        self.bench = Exercise.objects.create(user=self.user, name="Bankdrücken", equipment_number="7")
        self.bench.categories.add(self.brust)
        self.today = timezone.localdate().isoformat()
        self.url = reverse("fitness:workout-day", kwargs={"date": self.today})

    def test_no_category_selected_shows_no_exercises(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Beinpresse")

    def test_category_filter_shows_matching_exercise_only(self):
        response = self.client.get(self.url, {"categories": [self.beine.id]})
        self.assertContains(response, "Beinpresse")
        self.assertNotContains(response, "Bankdrücken")

    def test_posting_sets_creates_workout_sets(self):
        data = {
            "categories": [str(self.beine.id)],
            "exercises": [str(self.leg_press.id)],
            f"ex{self.leg_press.id}-TOTAL_FORMS": "1",
            f"ex{self.leg_press.id}-INITIAL_FORMS": "0",
            f"ex{self.leg_press.id}-MIN_NUM_FORMS": "0",
            f"ex{self.leg_press.id}-MAX_NUM_FORMS": "1000",
            f"ex{self.leg_press.id}-0-reps": "10",
            f"ex{self.leg_press.id}-0-weight_kg": "50",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        day = get_or_create_day(self.user, timezone.localdate())
        workout_set = WorkoutSet.objects.get(user=self.user, exercise=self.leg_press, day=day)
        self.assertEqual(workout_set.set_number, 1)
        self.assertEqual(workout_set.reps, 10)

        # a second POST adds another set without clobbering the first
        data[f"ex{self.leg_press.id}-0-weight_kg"] = "55"
        data[f"ex{self.leg_press.id}-0-reps"] = "9"
        data[f"ex{self.leg_press.id}-TOTAL_FORMS"] = "1"
        self.client.post(self.url, data)
        self.assertEqual(WorkoutSet.objects.filter(exercise=self.leg_press, day=day).count(), 2)


class RecipeAndFoodLogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dave", password="pw")
        self.client.force_login(self.user)
        self.today = timezone.localdate().isoformat()

    def test_recipe_add(self):
        response = self.client.post(
            reverse("fitness:recipe-add"),
            {
                "name": "Haferflocken",
                "text": "Haferflocken mit Milch",
                "calories_kcal_per_100g": 350,
                "protein_g_per_100g": "15.0",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Recipe.objects.filter(user=self.user, name="Haferflocken").exists())

    def test_food_entry_independent_of_recipe_values(self):
        recipe = Recipe.objects.create(
            user=self.user, name="Shake", calories_kcal_per_100g=200, protein_g_per_100g="30.0"
        )
        response = self.client.post(
            reverse("fitness:food-entry-add", kwargs={"date": self.today}),
            {"name": "Protein Shake", "recipe": recipe.pk, "amount_g": 500, "calories_kcal": 250, "protein_g": "35.0"},
        )
        self.assertEqual(response.status_code, 302)
        entry = FoodLogEntry.objects.get(user=self.user, name="Protein Shake")
        self.assertEqual(entry.amount_g, 500)
        self.assertEqual(entry.calories_kcal, 250)
        self.assertEqual(recipe.calories_kcal_per_100g, 200)

    def test_food_day_totals_ignore_none_entries(self):
        day = get_or_create_day(self.user, timezone.localdate())
        FoodLogEntry.objects.create(user=self.user, day=day, name="A", calories_kcal=300, protein_g="20.0")
        FoodLogEntry.objects.create(user=self.user, day=day, name="B", calories_kcal=150, protein_g="10.0")
        FoodLogEntry.objects.create(user=self.user, day=day, name="C", calories_kcal=None, protein_g="5.0")

        response = self.client.get(reverse("fitness:food-day", kwargs={"date": self.today}))
        self.assertEqual(response.context["totals"]["total_calories"], 450)
        self.assertEqual(float(response.context["totals"]["total_protein"]), 35.0)

    def test_food_entry_delete(self):
        day = get_or_create_day(self.user, timezone.localdate())
        entry = FoodLogEntry.objects.create(user=self.user, day=day, name="Snack", calories_kcal=100)
        response = self.client.post(reverse("fitness:food-entry-delete", kwargs={"pk": entry.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FoodLogEntry.objects.filter(pk=entry.pk).exists())


class FitnessApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="eve", password="pw")
        self.other_user = User.objects.create_user(username="frank", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_unauthenticated_request_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/exercises/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_only_sees_own_exercises(self):
        Exercise.objects.create(user=self.other_user, name="Fremde Übung")
        Exercise.objects.create(user=self.user, name="Eigene Übung")
        response = self.client.get("/api/v1/exercises/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [e["name"] for e in response.data]
        self.assertEqual(names, ["Eigene Übung"])

    def test_exercise_create_and_retrieve(self):
        response = self.client.post("/api/v1/exercises/", {"name": "Latzug"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        exercise_id = response.data["id"]
        response = self.client.get(f"/api/v1/exercises/{exercise_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Latzug")
