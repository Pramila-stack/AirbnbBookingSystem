from django import forms

from booking.models import Reservation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# class ReservationForm(forms.ModelForm):
#     class Meta:
#         model = Reservation
#         # Only show dates to the user. 
#         # Calculate price and fee in the background for security.
#         fields = ['check_in', 'check_out']
#         widgets = {
#             'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#         }


from django import forms
from .models import Listing, Reservation

from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['check_in', 'check_out']
        # Upgrade HTML rendering via Django Widgets without changing logic
        widgets = {
            'check_in': forms.DateInput(
                attrs={
                    'type': 'date', 
                    'class': 'form-input',
                    'placeholder': 'Select check-in date'
                }
            ),
            'check_out': forms.DateInput(
                attrs={
                    'type': 'date', 
                    'class': 'form-input',
                    'placeholder': 'Select check-out date'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        # Pass the listing down from the view initialization block
        self.listing = kwargs.pop('listing', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out and self.listing:
            overlapping = Reservation.objects.filter(
                listing=self.listing,
                check_in__lt=check_out,
                check_out__gt=check_in
            ).exists()
            
            if overlapping:
                raise forms.ValidationError("These dates are already booked. Please choose different dates.")
        return cleaned_data


from django.contrib.auth import get_user_model

User = get_user_model()


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


from django import forms
from .models import Listing # Adjusted based on your code context

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ListingForm(forms.ModelForm):
    # Injecting advanced custom classes into our multiple file widgets
    livingroom_images = MultipleFileField(required=False, widget=MultipleFileInput(attrs={'class': 'form-control-file-custom'}))
    kitchen_images = MultipleFileField(required=False, widget=MultipleFileInput(attrs={'class': 'form-control-file-custom'}))
    bedroom_images = MultipleFileField(required=False, widget=MultipleFileInput(attrs={'class': 'form-control-file-custom'}))
    bathroom_images = MultipleFileField(required=False, widget=MultipleFileInput(attrs={'class': 'form-control-file-custom'}))
    exterior_images = MultipleFileField(required=False, widget=MultipleFileInput(attrs={'class': 'form-control-file-custom'}))

    class Meta:
        model = Listing
        fields = ['title', 'description', 'category', 'city', 'country', 'price_per_night']
        # UPGRADE: Add Bootstrap classes directly to standard model fields
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control modern-input', 'placeholder': 'e.g. Luxury Beachside Villa'}),
            'description': forms.Textarea(attrs={'class': 'form-control modern-input', 'rows': 4, 'placeholder': 'Tell guests what makes your place unique...'}),
            'category': forms.Select(attrs={'class': 'form-select modern-input'}),
            'city': forms.TextInput(attrs={'class': 'form-control modern-input', 'placeholder': 'e.g. Los Angeles'}),
            'country': forms.TextInput(attrs={'class': 'form-control modern-input', 'placeholder': 'e.g. United States'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control modern-input', 'placeholder': '0.00'}),
        }