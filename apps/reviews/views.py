from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import WeeklyReviewForm
from .models import WeeklyReview
from .services import aggregate_week_data, get_or_create_current_review, get_or_create_review


@login_required
def current(request):
    _, iso_year, iso_week = get_or_create_current_review(request.user)
    return redirect("reviews:detail", iso_year=iso_year, iso_week=iso_week)


@login_required
def detail(request, iso_year, iso_week):
    review = get_or_create_review(request.user, iso_year, iso_week)
    if request.method == "POST":
        form = WeeklyReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("reviews:detail", iso_year=iso_year, iso_week=iso_week)
    else:
        form = WeeklyReviewForm(instance=review)

    week_data = aggregate_week_data(request.user, iso_year, iso_week)
    context = {"review": review, "form": form, **week_data}
    return render(request, "reviews/weekly_review_detail.html", context)


@login_required
def history(request):
    reviews = WeeklyReview.objects.filter(user=request.user)
    return render(request, "reviews/weekly_review_history.html", {"reviews": reviews})
