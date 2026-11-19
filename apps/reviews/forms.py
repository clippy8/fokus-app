from django import forms

from .models import WeeklyReview


class WeeklyReviewForm(forms.ModelForm):
    class Meta:
        model = WeeklyReview
        fields = [
            "reflection_good",
            "reflection_improve",
            "weekly_goal_text",
            "weekly_goal_achieved",
            "weekly_goal_reflection",
            "numbers_reviewed",
            "most_important_confirmed",
            "status",
        ]
        widgets = {
            "reflection_good": forms.Textarea(attrs={"rows": 3}),
            "reflection_improve": forms.Textarea(attrs={"rows": 3}),
            "weekly_goal_text": forms.Textarea(attrs={"rows": 2}),
            "weekly_goal_reflection": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "reflection_good": "Was lief gut?",
            "reflection_improve": "Was könnte besser laufen?",
            "weekly_goal_text": "Wochenziel",
            "weekly_goal_achieved": "Wochenziel erreicht?",
            "weekly_goal_reflection": "Reflexion zum Wochenziel",
            "numbers_reviewed": "Zahlen überprüft",
            "most_important_confirmed": "Wichtigstes bestätigt",
            "status": "Status",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["weekly_goal_achieved"].choices = [("", "---------"), *WeeklyReview.ACHIEVED_CHOICES]
