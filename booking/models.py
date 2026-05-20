from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from django.core.validators import MinValueValidator,MaxValueValidator

class User(AbstractUser):
    is_host = models.BooleanField(default=False)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Listing(models.Model):
    host = models.ForeignKey(User,on_delete=models.CASCADE,related_name="listings")
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)

    title = models.CharField(max_length=250)
    description = models.TextField()

    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    price_per_night = models.DecimalField(max_digits=10,decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class ListingImage(models.Model):
    # Added categories to identify different parts of the house
    ROOM_TYPES = [
        ('living_room', 'Living Room'),
        ('bedroom', 'Bedroom'),
        ('bathroom', 'Bathroom'),
        ('kitchen', 'Kitchen'),
        ('exterior', 'Exterior'),
    ]
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="listings/")
    room_type = models.CharField(max_length=50, choices=ROOM_TYPES, default='exterior') # New Field

    def __str__(self):
        return f"{self.listing.title} - {self.get_room_type_display()}"

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    listings = models.ManyToManyField(Listing,related_name="amenities")

    def __str__(self):
        return self.name
    
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('cancelled','Cancelled'),
        ('completed','Completed'),
    ]

    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='reservations')
    guest = models.ForeignKey(User,on_delete=models.CASCADE,related_name='bookings')

    check_in = models.DateField()
    check_out = models.DateField()

    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    service_fee = models.DecimalField(max_digits=10,decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    reservation = models.OneToOneField(Reservation,on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User,on_delete=models.CASCADE)

    rating = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

class Conversation(models.Model):
    participants = models.ManyToManyField(User)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name="messages")
    sender = models.ForeignKey(User,on_delete=models.CASCADE)
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a user from adding the same listing to their wishlist multiple times
        unique_together = ('user', 'listing')

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"
    
class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlists"
    )

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "listing")

    def __str__(self):
        return f"{self.user.username} saved {self.listing.title}"
