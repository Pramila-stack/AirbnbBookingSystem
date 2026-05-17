from django.contrib import admin

from booking.models import Amenity, Category, Conversation, Listing, ListingImage, Message, Reservation, Review, User

# Register your models here.
admin.site.register(Category)
admin.site.register(Amenity)
admin.site.register(ListingImage)
admin.site.register(Review)
admin.site.register(Conversation)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_host', 'is_staff')
    search_fields = ('username', 'email')


class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'city', 'country', 'price_per_night', 'created_at')
    search_fields = ('title', 'city', 'country')
    list_filter = ('city', 'country')

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('listing', 'guest', 'check_in', 'check_out', 'status', 'total_price')
    list_filter = ('status',)
    search_fields = ('listing__title', 'guest__username')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'sent_at')
    search_fields = ('text',)


admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Message, MessageAdmin)