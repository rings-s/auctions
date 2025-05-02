# In back/base/permissions.py
from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

class IsAppraiser(BasePermission):
    """Allows access only to appraiser users"""
    message = _('You must be an appraiser to perform this action.')

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'appraiser' or request.user.is_superuser
        )

class IsDataEntry(BasePermission):
    """Allows access only to data entry specialists"""
    message = _('You must be a data entry specialist to perform this action.')

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'data_entry' or request.user.is_superuser
        )

class IsPropertyOwner(BasePermission):
    """Allows access only to property owners"""
    message = _('You must be a property owner to perform this action.')

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'owner' or request.user.is_superuser
        )
    
    def has_object_permission(self, request, view, obj):
        # For property objects, check if user is the actual owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user or request.user.is_superuser
        return False


class IsAppraiserOrDataEntry(BasePermission):
    """
    Custom permission to allow access only to appraisers or data entry users.
    """
    message = 'You must be an appraiser or data entry specialist to perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['appraiser', 'data_entry'] or 
            request.user.is_superuser
        )

class IsPropertyOwner(BasePermission):
    """
    Custom permission to allow access only to property owners.
    """
    message = 'You must be the owner of this property to perform this action.'

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_superuser



class IsObjectOwner(BasePermission):

    """Checks if the user is the owner of the specific object"""
    message = _('You must be the owner of this object to perform this action.')
    
    def has_object_permission(self, request, view, obj):
        # For objects that have a user or owner field
        if hasattr(obj, 'owner'):
            return obj.owner == request.user or request.user.is_superuser
        elif hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_superuser
        return False