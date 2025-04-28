from django.urls import path, register_converter
from . import views

# Custom path converter for Arabic/unicode slugs
import re
class ArabicSlugConverter:
    regex = r'[-\w\u0600-\u06FF]+'
    def to_python(self, value):
        return value
    def to_url(self, value):
        return value

register_converter(ArabicSlugConverter, 'arabicslug')

urlpatterns = [
    # MEDIA
    path('media/', views.MediaListCreateAPIView.as_view(), name='media-list-create'),
    path('media/<int:pk>/', views.MediaRetrieveUpdateDestroyAPIView.as_view(), name='media-detail'),

    # PROPERTY
    path('properties/', views.PropertyListCreateAPIView.as_view(), name='property-list-create'),
    path('properties/<int:pk>/', views.PropertyRetrieveUpdateDestroyAPIView.as_view(), name='property-detail'),
    path('properties/slug/<arabicslug:slug>/', views.PropertySlugDetailAPIView.as_view(), name='property-detail-arabic-slug'),

    # ROOM
    path('rooms/', views.RoomListCreateAPIView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', views.RoomRetrieveUpdateDestroyAPIView.as_view(), name='room-detail'),

    # AUCTION
    path('auctions/', views.AuctionListCreateAPIView.as_view(), name='auction-list-create'),
    path('auctions/<int:pk>/', views.AuctionRetrieveUpdateDestroyAPIView.as_view(), name='auction-detail'),
    path('auctions/slug/<arabicslug:slug>/', views.AuctionSlugDetailAPIView.as_view(), name='auction-detail-arabic-slug'),

    # BID
    path('bids/', views.BidListCreateAPIView.as_view(), name='bid-list-create'),
    path('bids/<int:pk>/', views.BidRetrieveUpdateDestroyAPIView.as_view(), name='bid-detail'),
]