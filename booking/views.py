from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView,TemplateView,View,DeleteView,UpdateView

from booking.forms import ReservationForm, SignupForm
from booking.models import Listing, Reservation
from decimal import Decimal  # Add this import at the top
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

# Create your views here.
# class HomeView(ListView):
#     model = Listing
#     template_name = "home.html"
#     context_object_name = "listings"

#     def get_queryset(self):
#         queryset = Listing.objects.prefetch_related("images").all().order_by("-created_at")

#         query = self.request.GET.get("q")

#         if query:
#             queryset = queryset.filter(
#                 Q(title__icontains=query)|Q(city__icontains=query)|Q(country__icontains=query))

#         return queryset


from django.views.generic import ListView
from .models import Listing  # Replace with your actual model import

class HomeView(ListView):
    model = Listing
    template_name = 'home.html'
    context_object_name = 'listings' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # FIXED: Removed the typo line entirely. Just pull 'q' straight from GET parameters.
        query = self.request.GET.get('q')

        if query:
            # Layout A: Search mode
            context['is_search'] = True
        else:
            # Layout B: Grouped Home Feed Slider mode
            context['is_search'] = False
            
            cities = Listing.objects.values_list('city', flat=True).distinct()
            
            grouped_listings = []
            for city in cities:
                city_listings = Listing.objects.filter(city=city)
                
                if city_listings.exists():
                    grouped_listings.append({
                        'city': city,
                        'listings': city_listings
                    })
            
            context['grouped_listings'] = grouped_listings

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            return queryset.filter(city__icontains=query)
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

        overlapping_bookings = Reservation.objects.filter(listing=listing).filter(check_in__lt=reservation.check_out,check_out__gt=reservation.check_in)

        if overlapping_bookings.exists():
            form.add_error(
                None,"These dates are already booked.Please choose different dates."
            )
            return self.form_invalid(form)

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


from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import ListingForm
from .models import ListingImage, Wishlist

class BecomeHostView(LoginRequiredMixin, CreateView):
    form_class = ListingForm
    template_name = "become_host.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        # 1. Elevate user to host status if they aren't already
        user = self.request.user
        if not user.is_host:
            user.is_host = True
            user.save(update_fields=['is_host'])

        # 2. Save listing fields, but don't commit to DB yet
        listing = form.save(commit=False)
        listing.host = user
        listing.save()

        # 3. livingroom_images
        livingroom_images = self.request.FILES.getlist("livingroom_images")
        for img in livingroom_images:
            ListingImage.objects.create(listing=listing,image=img,room_type="living_room")

        # 4. kitchen_images
        kitchen_images = self.request.FILES.getlist("kitchen_images")
        for img in kitchen_images:
            ListingImage.objects.create(listing=listing,image=img,room_type="kitchen")

        # 4. bedroom_images
        bedroom_images = self.request.FILES.getlist("bedroom_images")
        for img in bedroom_images:
            ListingImage.objects.create(listing=listing,image=img,room_type="bedroom")

        # 4. bathroom_images
        bathroom_images = self.request.FILES.getlist("bathroom_images")
        for img in bathroom_images:
            ListingImage.objects.create(listing=listing,image=img,room_type="bathroom")

        # 4. exterior_images
        exterior_images = self.request.FILES.getlist("exterior_images")
        for img in exterior_images:
            ListingImage.objects.create(listing=listing,image=img,room_type="exterior")

        
        return super().form_valid(form)
    


class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = "wishlist.html"
    context_object_name = "wishlist_items"

    def get_queryset(self):
        return Wishlist.objects.filter(
            user=self.request.user
        ).select_related("listing").prefetch_related("listing__images")
    
class AddToWishlistView(LoginRequiredMixin, View):

    def post(self, request, listing_id):
        listing = get_object_or_404(Listing, id=listing_id)

        Wishlist.objects.get_or_create(
            user=request.user,
            listing=listing
        )

        return redirect("wishlist")


class ListingDeleteView(LoginRequiredMixin,DeleteView):
    model = Listing
    template_name = "listing_delete.html"
    context_object_name = "listing"
    success_url = reverse_lazy("home")

class ListingUpdateView(LoginRequiredMixin,UpdateView):
    model = Listing
    template_name = "become_host.html"
    form_class = ListingForm
    success_url = reverse_lazy("home")

    def get_queryset(self):
        return Listing.objects.filter(host=self.request.user)