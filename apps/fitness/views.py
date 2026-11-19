from datetime import date as date_cls
from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.dailydash.services import get_or_create_day

from .forms import ExerciseForm, FoodLogEntryForm, RecipeForm, WorkoutSetFormSet
from .models import Exercise, ExerciseCategory, FoodLogEntry, Recipe, WorkoutSet


@login_required
def fitness_index(request):
    today = timezone.localdate().isoformat()
    return render(request, "fitness/fitness_index.html", {"today": today})


@login_required
def exercise_list(request):
    exercises = Exercise.objects.filter(user=request.user).prefetch_related("categories")
    return render(request, "fitness/exercise_list.html", {"exercises": exercises})


@login_required
def exercise_add(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST, request.FILES, instance=Exercise(user=request.user))
        if form.is_valid():
            form.save()
            return redirect("fitness:exercise-list")
    else:
        form = ExerciseForm()
    return render(request, "fitness/exercise_form.html", {"form": form})


@login_required
def exercise_edit(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk, user=request.user)
    if request.method == "POST":
        form = ExerciseForm(request.POST, request.FILES, instance=exercise)
        if form.is_valid():
            form.save()
            return redirect("fitness:exercise-list")
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, "fitness/exercise_form.html", {"form": form, "exercise": exercise})


@require_POST
@login_required
def exercise_deactivate(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk, user=request.user)
    exercise.active = False
    exercise.save()
    messages.success(request, f"Übung '{exercise.name}' deaktiviert.")
    return redirect("fitness:exercise-list")


@login_required
def exercise_history(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk, user=request.user)
    sets = WorkoutSet.objects.filter(exercise=exercise, user=request.user).select_related("day")
    return render(request, "fitness/exercise_history.html", {"exercise": exercise, "sets": sets})


@login_required
def workout_day(request, date):
    parsed_date = date_cls.fromisoformat(date)
    day = get_or_create_day(request.user, parsed_date)
    all_categories = ExerciseCategory.objects.all()

    params = request.POST if request.method == "POST" else request.GET
    selected_category_ids = params.getlist("categories")
    selected_exercise_ids = params.getlist("exercises")

    exercises_qs = Exercise.objects.filter(user=request.user, active=True)
    if selected_category_ids:
        exercises_qs = exercises_qs.filter(categories__id__in=selected_category_ids).distinct()
    exercises_qs = exercises_qs.order_by("name")

    selected_exercises = list(exercises_qs.filter(id__in=selected_exercise_ids)) if selected_exercise_ids else []

    formsets = {}
    for exercise in selected_exercises:
        qs = WorkoutSet.objects.filter(user=request.user, exercise=exercise, day=day).order_by("set_number")
        formsets[exercise.id] = WorkoutSetFormSet(
            request.POST if request.method == "POST" else None, prefix=f"ex{exercise.id}", queryset=qs
        )

    if request.method == "POST" and selected_exercises and all(formsets[e.id].is_valid() for e in selected_exercises):
        for exercise in selected_exercises:
            formset = formsets[exercise.id]
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            next_number = WorkoutSet.objects.filter(user=request.user, exercise=exercise, day=day).count() + 1
            for instance in instances:
                if not instance.pk:
                    instance.set_number = next_number
                    next_number += 1
                instance.user = request.user
                instance.exercise = exercise
                instance.day = day
                instance.save()
        messages.success(request, "Training gespeichert.")
        query = urlencode(
            {"categories": selected_category_ids, "exercises": selected_exercise_ids}, doseq=True
        )
        return redirect(f"{reverse('fitness:workout-day', kwargs={'date': date})}?{query}")

    exercise_formsets = [{"exercise": exercise, "formset": formsets[exercise.id]} for exercise in selected_exercises]

    context = {
        "day": day,
        "date": date,
        "all_categories": all_categories,
        "selected_category_ids": [int(i) for i in selected_category_ids],
        "exercises": exercises_qs,
        "selected_exercise_ids": [int(i) for i in selected_exercise_ids],
        "exercise_formsets": exercise_formsets,
        "prev_date": (parsed_date - timedelta(days=1)).isoformat(),
        "next_date": (parsed_date + timedelta(days=1)).isoformat(),
        "is_today": parsed_date == timezone.localdate(),
    }
    return render(request, "fitness/workout_day.html", context)


@login_required
def recipe_list(request):
    recipes = Recipe.objects.filter(user=request.user)
    return render(request, "fitness/recipe_list.html", {"recipes": recipes})


@login_required
def recipe_add(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=Recipe(user=request.user))
        if form.is_valid():
            form.save()
            return redirect("fitness:recipe-list")
    else:
        form = RecipeForm()
    return render(request, "fitness/recipe_form.html", {"form": form})


@login_required
def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect("fitness:recipe-list")
    else:
        form = RecipeForm(instance=recipe)
    return render(request, "fitness/recipe_form.html", {"form": form, "recipe": recipe})


@login_required
def food_day(request, date):
    parsed_date = date_cls.fromisoformat(date)
    day = get_or_create_day(request.user, parsed_date)
    entries = FoodLogEntry.objects.filter(user=request.user, day=day).select_related("recipe")
    totals = entries.aggregate(total_calories=Sum("calories_kcal"), total_protein=Sum("protein_g"))
    context = {
        "day": day,
        "date": date,
        "entries": entries,
        "totals": totals,
        "prev_date": (parsed_date - timedelta(days=1)).isoformat(),
        "next_date": (parsed_date + timedelta(days=1)).isoformat(),
        "is_today": parsed_date == timezone.localdate(),
    }
    return render(request, "fitness/food_day.html", context)


def _recipe_prefill_data(user):
    return {
        str(recipe.id): {
            "caloriesPer100g": recipe.calories_kcal_per_100g,
            "proteinPer100g": str(recipe.protein_g_per_100g) if recipe.protein_g_per_100g is not None else None,
        }
        for recipe in Recipe.objects.filter(user=user)
    }


@login_required
def food_entry_add(request, date):
    parsed_date = date_cls.fromisoformat(date)
    if request.method == "POST":
        form = FoodLogEntryForm(request.POST, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.day = get_or_create_day(request.user, parsed_date)
            entry.save()
            return redirect("fitness:food-day", date=date)
    else:
        form = FoodLogEntryForm(user=request.user)
    context = {"form": form, "date": date, "recipe_data": _recipe_prefill_data(request.user)}
    return render(request, "fitness/food_entry_form.html", context)


@login_required
def food_entry_edit(request, pk):
    entry = get_object_or_404(FoodLogEntry, pk=pk, user=request.user)
    date = entry.day.date.isoformat()
    if request.method == "POST":
        form = FoodLogEntryForm(request.POST, instance=entry, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("fitness:food-day", date=date)
    else:
        form = FoodLogEntryForm(instance=entry, user=request.user)
    context = {
        "form": form,
        "date": date,
        "entry": entry,
        "recipe_data": _recipe_prefill_data(request.user),
    }
    return render(request, "fitness/food_entry_form.html", context)


@require_POST
@login_required
def food_entry_delete(request, pk):
    entry = get_object_or_404(FoodLogEntry, pk=pk, user=request.user)
    date = entry.day.date.isoformat()
    entry.delete()
    return redirect("fitness:food-day", date=date)
