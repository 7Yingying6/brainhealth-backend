from django import forms
from .models import UserProfile, SkinType

class SkinTypeForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['skin_type']
        widgets = {
            'skin_type': forms.Select(attrs={'class': 'form-control'})
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['skin_type'].queryset = SkinType.objects.all()
            self.fields['skin_type'].empty_label = "Select your skin type"

class CityForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['city']
        widgets = {
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your suburb or city (e.g., Melbourne, Carlton, Fitzroy)'
            })
        }
        labels = {
            'city': 'Suburb or City'
        }