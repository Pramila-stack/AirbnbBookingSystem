from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView,TemplateView

from booking.forms import ReservationForm, SignupForm
from booking.models import Listing, Reservation
from decimal import Decimal  # Add this import at the top
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

# Create your views here.
class HomeView(ListView):
    model = Listing
    template_name = "home.html"
    context_object_name = "listings"

    def get_queryset(self):
        queryset = Listing.objects.prefetch_related("images").all()

        query = self.request.GET.get("q")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)|Q(city__icontains=query)|Q(country__icontains=query))

        return queryset
    


class ListDetailView(DetailView):
    model = Listing
    template_name = "list_detail.html"
    context_object_name = "listing"


class ListingGalleryView(DetailView):
    model = Listing
    template_name = "listing_gallery.html"
    context_object_name = "listing"




from decimal import Decimal
from django.shortcuts import get_object_or_404

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from decimal import Decimal

class ReservationView(LoginRequiredMixin,CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = "reservation.html"

    def form_valid(self, form):
        # 1. Save the reservation logic
        reservation = form.save(commit=False)
        listing_id = self.kwargs.get('listing_id')
        listing = get_object_or_404(Listing, id=listing_id)
        
        reservation.guest = self.request.user
        reservation.listing = listing
        reservation.service_fee = Decimal('15.00')
        
        # Calculate Price
        nights = (reservation.check_out - reservation.check_in).days
        if nights < 1: nights = 1
        reservation.total_price = (listing.price_per_night * nights) + reservation.service_fee
        
        reservation.save()

        # 2. EMAIL NOTIFICATION LOGIC
        subject = f"Booking Confirmed: {listing.title}"
        message = f"""
        Hi {reservation.guest.username},

        Your booking for {listing.title} is confirmed!
        
        Details:
        - Check-in: {reservation.check_in}
        - Check-out: {reservation.check_out}
        - Total Price: ${reservation.total_price}
        
        Address: {listing.city}, {listing.country}
        
        Enjoy your stay!
        """
        # Send to both guest and host
        recipient_list = [reservation.guest.email, listing.host.email]
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL, # Usually set in settings.py
            recipient_list,
            fail_silently=False, # Set to True in production to avoid crashing if email fails
        )

        # 3. Redirect to your simple thank you page
        return redirect('booking-success')
    
class BookingSuccessView(LoginRequiredMixin,TemplateView):
    template_name = "booking_success.html"



class SignupView(CreateView):
    template_name = "registration/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        login(self.request,user)
        return super().form_valid(form)

