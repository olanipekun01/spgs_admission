from django import forms
from .models import ProfessionalCredential
from django.utils import timezone

class ProfessionalCredentialForm(forms.ModelForm):
    class Meta:
        model = ProfessionalCredential
        fields = ['credential_name', 'issuing_organization', 'issue_date', 'expiry_date', 'credential_number']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')

        if expiry_date and issue_date and expiry_date <= issue_date:
            raise forms.ValidationError("Expiry date must be after issue date.")
        if issue_date and issue_date > timezone.now().date():
            raise forms.ValidationError("Issue date cannot be in the future.")
        return cleaned_data