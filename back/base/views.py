# back/views.py (Complete and Corrected)

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

# Import permissions ONLY from the consolidated file (e.g., base.permissions)
# Adjust the import path if permissions.py is elsewhere (e.g., from base.permissions import ...)
from .permissions import (
    IsVerifiedUser, IsAppraiser, IsDataEntry, IsObjectOwner,
    IsPropertyOwner, IsAppraiserOrDataEntry,
    IsPropertyOwnerOrAppraiserOrDataEntry, IsPropertyOwnerOrAppraiser,
    IsAdminUser # Keep if view-level staff access is needed
    # IsSelfOrStaff - Import if needed for User views, not used here
)


# ==================
# MEDIA VIEWS
# ==================
class MediaListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all media items or create a new one.
    Requires user to be verified.
    """
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    # Only verified users can list/create Media
    permission_classes = [IsVerifiedUser] # Checks authentication and verification
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['media_type', 'content_type']
    search_fields = ['name']

    # Optional: Set owner during creation if Media has an owner field
    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)


class MediaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific media item.
    Requires user to be verified and own the object (or be superuser).
    """
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    # Use generic IsObjectOwner (checks obj.owner/user + superuser)
    # Requires user to be verified first.
    permission_classes = [IsVerifiedUser, IsObjectOwner]


# ==================
# PROPERTY VIEWS
# ==================
class PropertyListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all properties or create a new one.
    Listing is allowed for any authenticated user.
    Creation is restricted to Appraisers, Data Entry, and Superusers.
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property_type', 'status', 'city']
    search_fields = ['title', 'slug', 'deed_number', 'city']

    def get_permissions(self):
        """
        Dynamically set permissions based on HTTP method.
        """
        # For GET requests (listing), require basic authentication.
        if self.request.method == 'GET':
            # Return CLASS reference
            return [IsAuthenticated]

        # For POST requests (creation), require authentication AND specific roles.
        # Return CLASS references for both permissions.
        return [IsAuthenticated, IsAppraiserOrDataEntry]

    def perform_create(self, serializer):
        """
        Automatically set the property owner to the logged-in user upon creation.
        """
        serializer.save(owner=self.request.user)


class PropertyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific property by its primary key.
    Retrieval is allowed for any authenticated user.
    Update is allowed for Owner, Appraiser, Data Entry, or Superuser.
    Deletion is restricted to the Owner or Superuser.
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def get_permissions(self):
        """
        Dynamically set permissions based on HTTP method.
        DRF calls has_object_permission on these classes after object retrieval.
        """
        # For safe methods (GET, HEAD, OPTIONS), require basic authentication.
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated]
        # For PUT/PATCH (update), require specific roles or ownership.
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated, IsPropertyOwnerOrAppraiserOrDataEntry]
        # For DELETE, require ownership.
        elif self.request.method == 'DELETE':
            return [IsAuthenticated, IsPropertyOwner]
        # Fallback (should not typically be reached for standard methods)
        return [IsAuthenticated] # Default restrictive


class PropertySlugDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific property using its slug.
    Permissions mirror the primary key based view.
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = 'slug' # Use 'slug' for object lookup

    def get_permissions(self):
        """
        Dynamically set permissions based on HTTP method, same as PK view.
        """
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated, IsPropertyOwnerOrAppraiserOrDataEntry]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated, IsPropertyOwner]
        return [IsAuthenticated]


# ==================
# ROOM VIEWS
# ==================
class RoomListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list rooms or create a new room associated with a property.
    Requires user to be verified.
    Creation requires additional validation in perform_create.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    # Base permission: User must be verified to attempt listing/creation.
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property', 'room_type']
    search_fields = ['name']

    def perform_create(self, serializer):
        """
        Validate if the user has permission to add a room to the specified property.
        Allow owner, appraiser, data entry, or superuser.
        """
        property_obj = serializer.validated_data.get('property')
        user = self.request.user
        # Check if user meets the criteria
        allowed = (
            user.is_superuser or
            user.role in ['appraiser', 'data_entry'] or
            (property_obj and property_obj.owner == user)
        )
        if not allowed:
            # Raise validation error if permission denied
            raise serializers.ValidationError(
                "You do not have permission to add rooms to this property."
            )
        # Proceed with saving if validation passes
        # Optionally set room owner if applicable: serializer.save(owner=user)
        serializer.save()


class RoomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific room.
    Requires user to be verified.
    Modification restricted (e.g., to Appraisers/Data Entry/Superusers).
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    # Requires user to be verified.
    # Further restricts modification to Appraisers, Data Entry, or Superusers.
    # A more specific permission checking parent property ownership might be better.
    permission_classes = [IsVerifiedUser, IsAppraiserOrDataEntry]


# ==================
# AUCTION VIEWS
# ==================
class AuctionListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list auctions or create a new auction for a property.
    Listing allowed for authenticated users.
    Creation attempt allowed for Appraisers, Superusers, or potential Property Owners.
    Requires validation in perform_create to confirm property ownership if needed.
    """
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction_type', 'status', 'related_property']
    search_fields = ['title', 'slug', 'description']

    def get_permissions(self):
        """
        Dynamically set permissions based on HTTP method.
        """
        if self.request.method == 'GET':
            # Allow any authenticated user to view auctions
            return [IsAuthenticated]
        # Allow attempt by Authenticated Appraisers, Superusers, or potential Owners
        return [IsAuthenticated, IsPropertyOwnerOrAppraiser]

    def perform_create(self, serializer):
        """
        Validate if the user (if not appraiser/superuser) owns the related property.
        """
        related_property = serializer.validated_data.get('related_property')
        user = self.request.user

        # Check if user has an allowed role or owns the property
        is_allowed_role = user.is_superuser or user.role == 'appraiser'
        is_owner_of_property = related_property and related_property.owner == user

        if not (is_allowed_role or is_owner_of_property):
            # Raise validation error if permission denied
            raise serializers.ValidationError({
                "related_property": "You must be an appraiser or the owner of the selected property to create an auction for it."
            })

        # Set creator if Auction model has a creator/owner field
        # serializer.save(creator=user)
        serializer.save()


class AuctionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific auction by PK.
    Requires user to be verified and own the auction object (or be superuser).
    Assumes Auction model has 'owner' or 'user' field checked by IsObjectOwner.
    """
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    # Requires verification and ownership of the auction object.
    permission_classes = [IsVerifiedUser, IsObjectOwner]


class AuctionSlugDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific auction using its slug.
    Permissions mirror the primary key based view.
    """
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    lookup_field = 'slug' # Use 'slug' for lookup
    # Requires verification and ownership of the auction object.
    permission_classes = [IsVerifiedUser, IsObjectOwner]


# ==================
# BID VIEWS
# ==================
class BidListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list bids or create a new bid for an auction.
    Listing allowed for authenticated users (consider filtering in get_queryset).
    Creation requires user to be verified and pass validation checks.
    """
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction', 'bidder', 'status']
    search_fields = ['auction__title', 'bidder__email'] # Use double underscore

    def get_permissions(self):
        """
        Dynamically set permissions based on HTTP method.
        """
        if self.request.method == 'GET':
            # Allow authenticated users to list bids.
            # Consider filtering in get_queryset for non-admins.
            return [IsAuthenticated]
        # Require verified user to attempt bid creation.
        return [IsVerifiedUser]

    def perform_create(self, serializer):
        """
        Validate bid eligibility (auction status, user role, bid amount etc.).
        Set the bidder to the current user.
        """
        auction = serializer.validated_data.get('auction')
        user = self.request.user

        # --- Start Validation ---
        if not auction:
             raise serializers.ValidationError({"auction": "Auction is required."})
        # Example: Check if auction is active (assuming StatusChoices exist)
        # Adjust 'Auction.StatusChoices.ACTIVE' to your actual status value
        if auction.status != 'active': # Replace 'active' if needed
             raise serializers.ValidationError({"auction": "Bids can only be placed on active auctions."})
        # Example: Prevent property owner from bidding on their own auction
        if hasattr(auction, 'related_property') and auction.related_property.owner == user:
             raise serializers.ValidationError({"detail": "Property owners cannot bid on their own auctions."})
        # Example: Add check for minimum bid increment, auction end time etc.
        # current_highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        # if current_highest_bid and serializer.validated_data.get('amount') <= current_highest_bid.amount:
        #    raise serializers.ValidationError({"amount": "Bid must be higher than the current highest bid."})
        # --- End Validation ---

        # Set the bidder to the current user and save
        serializer.save(bidder=self.request.user)


class BidRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific bid.
    Requires user to be verified and own the bid object (or be superuser).
    Assumes Bid model has 'bidder' field checked by IsObjectOwner.
    """
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    # Requires verification and ownership of the bid object.
    permission_classes = [IsVerifiedUser, IsObjectOwner]

