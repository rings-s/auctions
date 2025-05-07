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
    path('types/property/', views.PropertyTypeListCreateView.as_view(), name='property-types'),
    path('types/property/<int:pk>/', views.PropertyTypeDetailView.as_view(), name='property-type'),
    path('types/building/', views.BuildingTypeListCreateView.as_view(), name='building-types'),
    path('types/building/<int:pk>/', views.BuildingTypeDetailView.as_view(), name='building-type'),
    path('types/room/', views.RoomTypeListCreateView.as_view(), name='room-types'),
    path('types/room/<int:pk>/', views.RoomTypeDetailView.as_view(), name='room-type'),
    path('types/auction/', views.AuctionTypeListCreateView.as_view(), name='auction-types'),
    path('types/auction/<int:pk>/', views.AuctionTypeDetailView.as_view(), name='auction-type'),
    
    # Locations
    path('locations/', views.LocationListCreateView.as_view(), name='locations'),
    path('locations/<int:pk>/', views.LocationDetailView.as_view(), name='location'),
    
    # Core resources
    path('media/', views.MediaListCreateView.as_view(), name='media'),
    path('media/<int:pk>/', views.MediaDetailView.as_view(), name='media-detail'),
    
    path('properties/', views.PropertyListCreateView.as_view(), name='properties'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property'),
    path('properties/<arabicslug:slug>/', views.PropertySlugDetailView.as_view(), name='property-by-slug'),
    
    path('rooms/', views.RoomListCreateView.as_view(), name='rooms'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room'),
    
    path('auctions/', views.AuctionListCreateView.as_view(), name='auctions'),
    path('auctions/<int:pk>/', views.AuctionDetailView.as_view(), name='auction'),
    path('auctions/<arabicslug:slug>/', views.AuctionSlugDetailView.as_view(), name='auction-by-slug'),
    
    path('bids/', views.BidListCreateView.as_view(), name='bids'),
    path('bids/<int:pk>/', views.BidDetailView.as_view(), name='bid'),
]