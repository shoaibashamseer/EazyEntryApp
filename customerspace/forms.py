from django import forms
from .models import Event, SeatAllocation
import csv
from django.core.exceptions import ValidationError


class BulkQRCodeUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File (QR Code Data)")
    zip_file = forms.FileField(label="Upload ZIP File (QR Code Images)", required=False)

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.endswith('.csv'):
            raise ValidationError("Only CSV files are allowed.")
        return csv_file

    def clean_zip_file(self):
        zip_file = self.cleaned_data.get('zip_file')
        if zip_file and not zip_file.name.endswith('.zip'):
            raise ValidationError("Only ZIP files are allowed.")
        return zip_file
