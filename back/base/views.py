from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Media, Property, Room, Auction, Bid,
    PropertyType, BuildingType, Location, RoomType,
    AuctionType
)
from .serializers import (
    MediaSerializer, PropertySerializer, RoomSerializer,
    AuctionSerializer, BidSerializer, PropertyTypeSerializer,
    BuildingTypeSerializer, LocationSerializer, RoomTypeSerializer,
    AuctionTypeSerializer
)
from .permissions import (
    IsVerifiedUser, IsAppraiser, IsDataEntry, IsObjectOwner,
    IsPropertyOwner, IsAppraiserOrDataEntry,
    IsPropertyOwnerOrAppraiserOrDataEntry, IsPropertyOwnerOrAppraiser,
    IsAdminUser
)

# Type Model Views
class PropertyTypeListCreateView(generics.ListCreateAPIView):
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

class PropertyTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [IsVerifiedUser, IsAdminUser]

class BuildingTypeListCreateView(generics.ListCreateAPIView):
    queryset = BuildingType.objects.all()
    serializer_class = BuildingTypeSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

class BuildingTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BuildingType.objects.all()
    serializer_class = BuildingTypeSerializer
    permission_classes = [IsVerifiedUser, IsAdminUser]

class LocationListCreateView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city', 'state', 'country']
    search_fields = ['city', 'state', 'country']

class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsVerifiedUser, IsAdminUser]

# Media Views
class MediaListCreateView(generics.ListCreateAPIView):
    queryset = Media.objects.select_related('content_type')
    serializer_class = MediaSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['media_type', 'is_primary']
    search_fields = ['name']

class MediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Media.objects.select_related('content_type')
    serializer_class = MediaSerializer
    permission_classes = [IsVerifiedUser, IsObjectOwner]

# Property Views
class PropertyListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property_type', 'building_type', 'status', 'location__city']
    search_fields = ['title', 'deed_number', 'location__city']

    def get_queryset(self):
        return Property.objects.select_related(
            'owner', 'property_type', 'building_type', 'location'
        ).prefetch_related('rooms', 'media').filter(
            is_published=True
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Property.objects.select_related(
            'owner', 'property_type', 'building_type', 'location'
        ).prefetch_related('rooms', 'media')

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsPropertyOwnerOrAppraiserOrDataEntry]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsPropertyOwner]
        return super().get_permissions()

class PropertySlugDetailView(PropertyDetailView):
    lookup_field = 'slug'

# Room Views
class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property', 'room_type', 'floor']
    search_fields = ['name']

    def get_queryset(self):
        return Room.objects.select_related(
            'property', 'room_type'
        ).prefetch_related('media')

    def perform_create(self, serializer):
        property_obj = serializer.validated_data.get('property')
        user = self.request.user
        
        if not (user.is_superuser or 
                user.role in ['appraiser', 'data_entry'] or 
                (property_obj and property_obj.owner == user)):
            raise ValidationError(_("Insufficient permissions"))
            
        serializer.save()

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.select_related('property', 'room_type').prefetch_related('media')
    serializer_class = RoomSerializer
    permission_classes = [IsVerifiedUser, IsAppraiserOrDataEntry]

# Auction Views
class AuctionListCreateView(generics.ListCreateAPIView):
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction_type', 'status', 'related_property']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Auction.objects.select_related(
            'auction_type', 'related_property',
            'related_property__owner', 'related_property__property_type'
        ).prefetch_related(
            'bids', 'media'
        ).filter(is_published=True).order_by('-start_date')

    def perform_create(self, serializer):
        related_property = serializer.validated_data.get('related_property')
        user = self.request.user
        
        if not (user.is_superuser or 
                user.role == 'appraiser' or 
                (related_property and related_property.owner == user)):
            raise ValidationError(_("Insufficient permissions"))
            
        serializer.save()

class AuctionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AuctionSerializer
    permission_classes = [IsVerifiedUser, IsObjectOwner]

    def get_queryset(self):
        return Auction.objects.select_related(
            'auction_type', 'related_property',
            'related_property__owner', 'related_property__property_type'
        ).prefetch_related('bids', 'media')

class AuctionSlugDetailView(AuctionDetailView):
    lookup_field = 'slug'

# Bid Views
class BidListCreateView(generics.ListCreateAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction', 'status']
    search_fields = ['auction__title']

    def get_queryset(self):
        return Bid.objects.select_related(
            'auction', 'bidder', 'auction__related_property'
        )

    def perform_create(self, serializer):
        auction = serializer.validated_data.get('auction')
        if not auction:
            raise ValidationError(_("Auction is required"))

        if auction.status != 'live':
            raise ValidationError(_("Auction is not live"))

        if auction.end_date <= timezone.now():
            raise ValidationError(_("Auction has ended"))

        if auction.related_property.owner == self.request.user:
            raise ValidationError(_("Cannot bid on own property"))

        bid_amount = serializer.validated_data.get('bid_amount')
        current_bid = auction.current_bid or auction.starting_bid
        if bid_amount <= current_bid + auction.minimum_increment:
            raise ValidationError(_("Bid too low"))

        serializer.save(bidder=self.request.user)

class BidDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.select_related('auction', 'bidder')
    serializer_class = BidSerializer
    permission_classes = [IsVerifiedUser, IsObjectOwner]




'''


Key features of this clean version:

Consistent naming conventions
Proper query optimization
Clear permission handling
Standard filter setup
Minimal code duplication
Clear validation logic
Proper inheritance patterns
Standard Django REST patterns

Major improvements:

Removed redundant code
Simplified class structures
Better organized imports
Clearer validation logic
More efficient queries
Standard naming patterns
Cleaner permission handling
Better error messages

This version follows Django community standards while keeping the code concise and maintainable.

'''