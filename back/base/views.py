from django.shortcuts import render
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Media, Property, Room, Auction, Bid
from .serializers import MediaSerializer, PropertySerializer, RoomSerializer, AuctionSerializer, BidSerializer
# Import custom permissions
from accounts.permissions import IsVerifiedUser, IsOwnerOrAdmin
from base.permissions import IsAppraiser, IsDataEntry, IsPropertyOwner, IsAppraiserOrDataEntry
from rest_framework.permissions import AllowAny, IsAuthenticated  




# MEDIA VIEWS
class MediaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['media_type', 'content_type']
    search_fields = ['name']

class MediaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsVerifiedUser, IsOwnerOrAdmin]

# PROPERTY VIEWS
class PropertyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property_type', 'status', 'city']
    search_fields = ['title', 'slug', 'deed_number', 'city']
    
    def get_permissions(self):
        # Everyone can list properties
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        # Only appraisers, data entry, and superusers can create properties
        return [IsAuthenticated(), (IsAppraiser() | IsDataEntry())]
    
    def perform_create(self, serializer):
        # Set the owner to the current user
        serializer.save(owner=self.request.user)


class PropertyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    
    def get_permissions(self):
        # Anyone can view property details
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        # Only owner, appraiser, data entry or superuser can update/delete
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated(), (IsPropertyOwner() | IsAppraiser() | IsDataEntry())]
        # Only owner or superuser can delete
        return [IsAuthenticated(), IsPropertyOwner()]

# Slug-based property detail view
class PropertySlugDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsVerifiedUser, IsOwnerOrAdmin]
    lookup_field = 'slug'

    def get_object(self):
        queryset = self.get_queryset()
        slug = self.kwargs.get(self.lookup_field)
        obj = queryset.filter(slug=slug).first()
        self.check_object_permissions(self.request, obj)
        return obj

# ROOM VIEWS
class RoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property', 'room_type']
    search_fields = ['name']

class RoomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsVerifiedUser, IsOwnerOrAdmin]

# AUCTION VIEWS
class AuctionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction_type', 'status', 'related_property']
    search_fields = ['title', 'slug', 'description']
    
    def get_permissions(self):
        if self.request.method == 'GET':
            # Anyone can view auctions
            return [IsAuthenticated()]
        # Only appraisers, property owners and superusers can create auctions
        return [IsAuthenticated(), (IsAppraiser() | IsPropertyOwner())]


class AuctionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [IsVerifiedUser, IsOwnerOrAdmin]

# Slug-based auction detail view
class AuctionSlugDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [IsVerifiedUser, IsOwnerOrAdmin]
    lookup_field = 'slug'

    def get_object(self):
        queryset = self.get_queryset()
        slug = self.kwargs.get(self.lookup_field)
        obj = queryset.filter(slug=slug).first()
        self.check_object_permissions(self.request, obj)
        return obj

# BID VIEWS
class BidListCreateAPIView(generics.ListCreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction', 'bidder', 'status']
    search_fields = ['auction__title', 'bidder__email']
    
    def get_permissions(self):
        # Anyone can view bids
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        # Anyone can create bids (with validation in perform_create)
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        # Set the bidder to the current user
        serializer.save(bidder=self.request.user)



class BidRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsVerifiedUser, IsOwnerOrAdmin]
