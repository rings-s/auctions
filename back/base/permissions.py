# back/base/permissions.py (Consolidated & Refined)

from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from django.utils.translation import gettext_lazy as _

# --- Core Status/Role Permissions ---

class IsVerifiedUser(BasePermission):
    """
    Allows access only to authenticated and email-verified users.
    (Copied from accounts.permissions)
    """
    message = _('User account must be verified.')

    def has_permission(self, request, view):
        # Ensure user is authenticated before checking verification status
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'is_verified', False)
        )

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users (is_staff).
    (Copied from accounts.permissions)
    Use this for view-level access specific to staff.
    """
    message = _('You must be an administrator (staff) to perform this action.')

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsAppraiser(BasePermission):
    """Allows access only to appraiser users or superusers."""
    message = _('You must be an appraiser to perform this action.')

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'appraiser' or request.user.is_superuser)
        )

class IsDataEntry(BasePermission):
    """Allows access only to data entry specialists or superusers."""
    message = _('You must be a data entry specialist to perform this action.')

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'data_entry' or request.user.is_superuser)
        )

# --- Object Ownership / Specific Relation Permissions ---

class IsObjectOwner(BasePermission):
    """
    Generic check: Allows access only to the object's owner (via 'owner' or 'user' field) or superusers.
    """
    message = _('You must be the owner of this object to perform this action.')

    def has_permission(self, request, view):
        # Essential: User must be authenticated to own anything.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Superusers always have permission.
        if request.user.is_superuser:
            return True

        # Check for standard ownership fields. Add more ('creator', 'bidder') if needed.
        owner = None
        if hasattr(obj, 'owner'):
            owner = obj.owner
        elif hasattr(obj, 'user'):
            owner = obj.user
        elif hasattr(obj, 'bidder'): # Common for Bid models
             owner = obj.bidder
        
        # Grant permission if the user is the owner.
        # Ensure comparison is between user objects.
        return owner is not None and owner == request.user


class IsPropertyOwner(BasePermission):
    """
    Specific check: Allows access only if the user owns the Property object or is a superuser.
    Relies primarily on object-level check.
    """
    message = _('You must be the owner of this property to perform this action.')

    def has_permission(self, request, view):
        # User must be authenticated.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Superusers always have permission.
        if request.user.is_superuser:
            return True

        # Check ownership specifically via the 'owner' attribute.
        # Ensure 'obj' is expected to be a Property instance with an 'owner'.
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsSelfOrStaff(BasePermission):
    """
    Specific check: Allows access if the object *is* the user OR the user is staff.
    Useful for UserProfile views where obj is a User instance.
    (Refined from accounts.IsOwnerOrAdmin)
    """
    message = _('You must be the relevant user or an admin (staff) to perform this action.')

    def has_permission(self, request, view):
        # User must be authenticated.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Grant permission if the user is staff or if the object is the user themselves.
        return request.user.is_staff or obj == request.user

# --- Combined Permissions (for OR logic) ---

class IsAppraiserOrDataEntry(BasePermission):
    """Allows access only to appraisers, data entry users, or superusers."""
    message = _('You must be an appraiser or data entry specialist to perform this action.')

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role in ['appraiser', 'data_entry'] or request.user.is_superuser)
        )


class IsPropertyOwnerOrAppraiserOrDataEntry(BasePermission):
    """
    Allows access if the user owns the Property object, is an Appraiser, is Data Entry, or is a Superuser.
    Used for updating properties.
    """
    message = _('You must be the property owner, an appraiser, or a data entry specialist to modify this property.')

    def has_permission(self, request, view):
        # User must be authenticated.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Grant access if superuser or has a relevant role.
        if request.user.is_superuser or request.user.role in ['appraiser', 'data_entry']:
            return True

        # Grant access if the user is the owner of the property object.
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsPropertyOwnerOrAppraiser(BasePermission):
    """
    Allows access if the user has the 'appraiser' role or potentially owns the related property.
    Used for *attempting* to create Auctions. Actual property ownership check for creation
    must happen in the view's perform_create or serializer based on request data.
    """
    message = _('You must be an appraiser or potentially the property owner to perform this action.')

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Superusers and Appraisers can always attempt creation.
        if request.user.is_superuser or request.user.role == 'appraiser':
            return True

        # Allow users with the 'owner' role to attempt (validation needed in view/serializer).
        # Alternatively, remove this check if only Appraisers/Superusers can create auctions.
        if request.user.role == 'owner':
            return True # Requires further validation in perform_create

        return False
        
    # No has_object_permission needed here as it's for ListCreate view access.
    # Object permissions for Auction *detail* views would use IsObjectOwner or similar.