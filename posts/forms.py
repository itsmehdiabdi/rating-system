# posts/forms.py
from django import forms


class RatingForm(forms.Form):
    rating = forms.IntegerField(
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter rating (0-5)'})
    )
