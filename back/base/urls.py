from django.urls import path
from . import views

# Arabic slug converter
class ArabicSlugConverter:
    regex = r'[-\w\u0600-\u06FF]+'
    
    def to_python(self, value):
        if not value:
            raise ValueError("Invalid slug value")
        return value
    
    def to_url(self, value):
        if not value:
            raise ValueError("Invalid slug value")
        return value

from django.urls import register_converter
register_converter(ArabicSlugConverter, 'arabicslug')

urlpatterns = [
    # Types
    path('types/property/', views.PropertyTypeListCreateAPIView.as_view(), name='property-types'),
    path('types/property/<int:pk>/', views.PropertyTypeRetrieveUpdateDestroyAPIView.as_view(), name='property-type'),
    path('types/building/', views.BuildingTypeListCreateAPIView.as_view(), name='building-types'),
    path('types/building/<int:pk>/', views.BuildingTypeRetrieveUpdateDestroyAPIView.as_view(), name='building-type'),
    path('types/room/', views.RoomTypeListCreateAPIView.as_view(), name='room-types'),
    path('types/room/<int:pk>/', views.RoomTypeRetrieveUpdateDestroyAPIView.as_view(), name='room-type'),
    path('types/auction/', views.AuctionTypeListCreateAPIView.as_view(), name='auction-types'),
    path('types/auction/<int:pk>/', views.AuctionTypeRetrieveUpdateDestroyAPIView.as_view(), name='auction-type'),
    
    # Locations
    path('locations/', views.LocationListCreateAPIView.as_view(), name='locations'),
    path('locations/<int:pk>/', views.LocationRetrieveUpdateDestroyAPIView.as_view(), name='location'),
    
    # Core resources
    path('media/', views.MediaListCreateAPIView.as_view(), name='media'),
    path('media/<int:pk>/', views.MediaRetrieveUpdateDestroyAPIView.as_view(), name='media-detail'),
    
    path('properties/', views.PropertyListCreateAPIView.as_view(), name='properties'),
    path('properties/<int:pk>/', views.PropertyRetrieveUpdateDestroyAPIView.as_view(), name='property'),
    path('properties/<arabicslug:slug>/', views.PropertySlugDetailAPIView.as_view(), name='property-by-slug'),
    
    path('rooms/', views.RoomListCreateAPIView.as_view(), name='rooms'),
    path('rooms/<int:pk>/', views.RoomRetrieveUpdateDestroyAPIView.as_view(), name='room'),
    
    path('auctions/', views.AuctionListCreateAPIView.as_view(), name='auctions'),
    path('auctions/<int:pk>/', views.AuctionRetrieveUpdateDestroyAPIView.as_view(), name='auction'),
    path('auctions/<arabicslug:slug>/', views.AuctionSlugDetailAPIView.as_view(), name='auction-by-slug'),
    
    path('bids/', views.BidListCreateAPIView.as_view(), name='bids'),
    path('bids/<int:pk>/', views.BidRetrieveUpdateDestroyAPIView.as_view(), name='bid'),
]