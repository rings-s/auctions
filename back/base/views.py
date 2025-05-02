from django.shortcuts import render, get_object_or_404
from rest_framework import generics, filters, status, serializers # Import serializers for validation errors
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Use DRF's IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

# Assuming models are in the same app or adjust import path
from .models import Media, Property, Room, Auction, Bid
# Assuming serializers are in the same app or adjust import path
from .serializers import (
    MediaSerializer, PropertySerializer, RoomSerializer,
    AuctionSerializer, BidSerializer
)

# Import permissions
from .permissions import (
    IsVerifiedUser, IsAppraiser, IsDataEntry, IsObjectOwner,
    IsPropertyOwner, IsAppraiserOrDataEntry,
    IsPropertyOwnerOrAppraiserOrDataEntry, IsPropertyOwnerOrAppraiser,
    IsAdminUser
)


# ==================
# MEDIA VIEWS
# ==================
# No changes needed for Media views regarding nested serialization of Property/Auction

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
    permission_classes = [IsVerifiedUser, IsObjectOwner]


# ==================
# PROPERTY VIEWS
# ==================

class PropertyListCreateAPIView(generics.ListCreateAPIView):
    # Original queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property_type', 'status', 'city']
    search_fields = ['title', 'slug', 'deed_number', 'city']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated()] # Kept simple as per original logic

    def get_queryset(self):
        """
        Optimize queryset for LIST view to include related rooms and media
        for efficient serialization.
        """
        # Apply optimization only for GET requests (listing)
        if self.request.method == 'GET':
            return Property.objects.select_related(
                'owner' # Include owner details if needed by serializer/frontend
            ).prefetch_related(
                'rooms',  # Fetch related rooms
                'media'   # Fetch related media (GenericRelation)
            ).filter(
                 is_published=True # Example: Only list published properties by default
                 # Add other base filters if necessary
            ).order_by('-created_at') # Maintain default ordering
        # For POST, the base manager is sufficient as we're creating, not listing related data
        return Property.objects.all()


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PropertyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # Original queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def get_queryset(self):
        """
        Optimize queryset for RETRIEVE view to include related rooms and media.
        This ensures nested data is present when fetching a single property.
        """
        # Optimization applies primarily to GET (Retrieve) but is safe for others
        return Property.objects.select_related(
            'owner'
        ).prefetch_related(
            'rooms',
            'media'
        )

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            # Corrected: Use class reference without calling ()
            return [IsAuthenticated]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated, IsPropertyOwnerOrAppraiserOrDataEntry]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated, IsPropertyOwner]
        return [IsAuthenticated]


class PropertySlugDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    # Original queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        """
        Optimize queryset for RETRIEVE view (using slug) to include related rooms and media.
        """
        # Same optimization as the PK-based retrieve view
        return Property.objects.select_related(
            'owner'
        ).prefetch_related(
            'rooms',
            'media'
        )

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated] # Corrected
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated, IsPropertyOwnerOrAppraiserOrDataEntry]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated, IsPropertyOwner]
        return [IsAuthenticated]


# ==================
# ROOM VIEWS
# ==================
# No changes needed for Room views regarding nested serialization of Property/Auction

class RoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property', 'room_type']
    search_fields = ['name']

    def perform_create(self, serializer):
        property_obj = serializer.validated_data.get('property')
        user = self.request.user
        allowed = (
            user.is_superuser or
            (hasattr(user, 'role') and user.role in ['appraiser', 'data_entry']) or # Safer check for role
            (property_obj and property_obj.owner == user)
        )
        if not allowed:
            raise serializers.ValidationError(
                "You do not have permission to add rooms to this property."
            )
        serializer.save()


class RoomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    # Consider a more specific permission checking parent property ownership/roles
    permission_classes = [IsVerifiedUser, IsAppraiserOrDataEntry]


# ==================
# AUCTION VIEWS
# ==================
class AuctionListCreateAPIView(generics.ListCreateAPIView):
    # Original queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction_type', 'status', 'related_property']
    search_fields = ['title', 'slug', 'description']

    def get_queryset(self):
        """
        Optimize queryset for LIST view to include related property (with its details),
        bids (with bidders), and media for efficient serialization.
        """
        if self.request.method == 'GET':
            return Auction.objects.select_related(
                'related_property', # Auction -> Property (FK)
                'related_property__owner' # Property -> User (FK) - Optional
            ).prefetch_related(
                'bids',                      # Auction -> Bids (Reverse FK)
                'bids__bidder',              # Bids -> User (FK)
                'media',                     # Auction -> Media (GenericRelation)
                'related_property__rooms',   # Property -> Rooms (Reverse FK)
                'related_property__media'    # Property -> Media (GenericRelation)
            ).filter(
                is_published=True # Example: Only list published auctions
                # status='live' # Example: Only list live auctions
            ).order_by('-start_date') # Maintain default ordering
        # For POST, the base manager is sufficient
        return Auction.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()] # Corrected
        # Corrected: Use class references without calling ()
        return [IsAuthenticated, IsPropertyOwnerOrAppraiser]

    def perform_create(self, serializer):
        related_property = serializer.validated_data.get('related_property')
        user = self.request.user
        is_allowed_role = user.is_superuser or (hasattr(user, 'role') and user.role == 'appraiser') # Safer check
        is_owner_of_property = related_property and related_property.owner == user

        if not (is_allowed_role or is_owner_of_property):
            raise serializers.ValidationError({
                "related_property": "You must be an appraiser or the owner of the selected property to create an auction for it."
            })
        serializer.save()


class AuctionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # Original queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    # Assuming IsObjectOwner checks auction.owner or similar field correctly
    permission_classes = [IsVerifiedUser, IsObjectOwner]

    def get_queryset(self):
        """
        Optimize queryset for RETRIEVE view to include related property (with details),
        bids (with bidders), and media.
        """
        # Same optimization needed for retrieving a single auction
        return Auction.objects.select_related(
            'related_property',
            'related_property__owner' # Optional
        ).prefetch_related(
            'bids',
            'bids__bidder',
            'media',
            'related_property__rooms',
            'related_property__media'
        )


class AuctionSlugDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    # Original queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    lookup_field = 'slug'
    permission_classes = [IsVerifiedUser, IsObjectOwner] # Assuming IsObjectOwner checks auction owner

    def get_queryset(self):
        """
        Optimize queryset for RETRIEVE view (using slug) to include related data.
        """
        # Same optimization as the PK-based retrieve view
        return Auction.objects.select_related(
            'related_property',
            'related_property__owner' # Optional
        ).prefetch_related(
            'bids',
            'bids__bidder',
            'media',
            'related_property__rooms',
            'related_property__media'
        )


# ==================
# BID VIEWS
# ==================
# No changes needed for Bid views regarding nested serialization of Property/Auction

class BidListCreateAPIView(generics.ListCreateAPIView):
    queryset = Bid.objects.prefetch_related('bidder').select_related('auction') # Simple optimization
    serializer_class = BidSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction', 'bidder', 'status']
    search_fields = ['auction__title', 'bidder__email']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()] # Corrected
        return [IsVerifiedUser()] # Corrected

    def perform_create(self, serializer):
        auction = serializer.validated_data.get('auction')
        user = self.request.user

        if not auction:
             raise serializers.ValidationError({"auction": "Auction is required."})

        # --- Adjust Validation Logic based on your exact Auction status values ---
        # Example: Assume 'live' is the correct status string for active auctions
        if auction.status != 'live': # Make sure 'live' matches your Auction.STATUS_CHOICES key
             raise serializers.ValidationError({"detail": "Bids can only be placed on live auctions."})
        # --- End Status Check ---

        if hasattr(auction, 'related_property') and auction.related_property and auction.related_property.owner == user:
             raise serializers.ValidationError({"detail": "Property owners cannot bid on their own auctions."})

        # Add validation for minimum increment, end date etc. here if needed
        # Example minimum increment check (adjust logic as needed):
        current_highest_bid_amount = auction.current_bid or auction.starting_bid
        bid_amount = serializer.validated_data.get('bid_amount')
        min_increment = auction.minimum_increment

        if bid_amount < (current_highest_bid_amount + min_increment):
             raise serializers.ValidationError({
                 "bid_amount": f"Your bid must be at least {current_highest_bid_amount + min_increment} "
                               f"(current bid/start: {current_highest_bid_amount}, min increment: {min_increment})."
             })

        # Check if auction has ended
        if auction.end_date <= timezone.now(): # Make sure timezone is imported: from django.utils import timezone
            raise serializers.ValidationError({"detail": "This auction has already ended."})


        serializer.save(bidder=self.request.user)


class BidRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # Optimize slightly by selecting related bidder and auction
    queryset = Bid.objects.select_related('auction', 'bidder')
    serializer_class = BidSerializer
    # Assuming IsObjectOwner checks bid.bidder correctly
    permission_classes = [IsVerifiedUser, IsObjectOwner]