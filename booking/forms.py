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

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['check_in', 'check_out']

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


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self,*args,**kwargs):
        kwargs.setdefault("widget",MultipleFileInput())
        super().__init__(*args,**kwargs)

    def clean(self, data, initial = None):
        single_file_clean = super().clean
        if isinstance(data, (list,tuple)):
            result = [single_file_clean(d,initial) for d in data]
        else:
            result = single_file_clean(data,initial)

        return result

class ListingForm(forms.ModelForm):
    livingroom_images = MultipleFileField(required=False)
    kitchen_images = MultipleFileField(required=False)
    bedroom_images = MultipleFileField(required=False)
    bathroom_images = MultipleFileField(required=False)
    exterior_images = MultipleFileField(required=False)

    class Meta:
        model = Listing
        fields = ['title','description','category','city','country','price_per_night',]