from django.urls import path

from booking import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("list-detail/<int:pk>/", views.ListDetailView.as_view(), name="list-detail"),
    path(
        "listing/<int:pk>/gallery/",
        views.ListingGalleryView.as_view(),
        name="listing_gallery",
    ),
    path(
        "reserve/<int:listing_id>/",
        views.ReservationView.as_view(),
        name="create-reservation",
    ),
    path(
        "booking-success/", views.BookingSuccessView.as_view(), name="booking-success"
    ),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("become-host/", views.BecomeHostView.as_view(), name="become-host"),
    path(
        "wishlist/add/<int:listing_id>/",
        views.AddToWishlistView.as_view(),
        name="add-to-wishlist",
    ),
    path("wishlist/", views.WishlistView.as_view(), name="wishlist"),
    path("delete/<int:pk>/", views.ListingDeleteView.as_view(), name="listing-delete"),
    path("update/<int:pk>/", views.ListingUpdateView.as_view(), name="listing-update"),
]
