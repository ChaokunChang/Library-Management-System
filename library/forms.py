from django import forms
from .models import *


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = LibrarySuggestion
        fields = ['name', 'author', 'publisher', 'isbn']
        labels = {'name': '书名', 'author': '作者', 'publisher': '出版社'}


class ReviewForm(forms.ModelForm):
    class Meta:
        model = LibraryReview
        fields = ['text', 'rate']
        labels = {'text': '书评', 'rate': '打分'}

