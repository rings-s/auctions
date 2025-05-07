from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Media, Property, Room, Auction, Bid,
    PropertyType, BuildingType, Location, RoomType,
    AuctionType
)

# Type Models Admin
@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AuctionType)
class AuctionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country', 'postal_code')
    list_filter = ('country', 'state', 'city')
    search_fields = ('city', 'state', 'country', 'postal_code')
    readonly_fields = ('created_at', 'updated_at')

# Media Admin
@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'media_type', 'file_size_display', 'is_primary', 'uploaded_at')
    list_filter = ('media_type', 'is_primary', 'uploaded_at')
    search_fields = ('name', 'content_type')
    readonly_fields = ('file_size', 'mime_type', 'width', 'height', 'uploaded_at')
    ordering = ('-uploaded_at',)

    def file_size_display(self, obj):
        """Convert file size to human readable format"""
        if not obj.file_size:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if obj.file_size < 1024:
                return f"{obj.file_size:.1f} {unit}"
            obj.file_size /= 1024
        return f"{obj.file_size:.1f} TB"
    file_size_display.short_description = _('File Size')

# Room Admin
class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ('name', 'room_type', 'floor', 'area_sqm', 'has_window', 'has_bathroom')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'property', 'room_type', 'floor', 'area_sqm')
    list_filter = ('room_type', 'floor', 'has_window', 'has_bathroom')
    search_fields = ('name', 'property__title')
    readonly_fields = ('created_at', 'updated_at')

# Property Admin
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_number', 'property_type', 'building_type', 'status', 'market_value', 'is_published')
    list_filter = (
        'property_type', 'building_type', 'status',
        'is_published', 'is_featured', 'is_verified'
    )
    search_fields = ('title', 'slug', 'deed_number', 'property_number')
    readonly_fields = (
        'property_number', 'slug', 'created_at',
        'updated_at', 'view_count'
    )
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'title', 'property_number', 'property_type',
                'building_type', 'status', 'deed_number'
            )
        }),
        (_('Location'), {
            'fields': ('location', 'address')
        }),
        (_('Property Details'), {
            'fields': (
                'description', 'size_sqm', 'floors',
                'year_built', 'market_value', 'minimum_bid'
            )
        }),
        (_('Features & Settings'), {
            'fields': (
                'features', 'amenities', 'owner',
                'is_published', 'is_featured', 'is_verified'
            )
        }),
        (_('System Fields'), {
            'fields': ('created_at', 'updated_at', 'view_count'),
            'classes': ('collapse',)
        }),
    )
    inlines = [RoomInline]
    date_hierarchy = 'created_at'

# Bid Admin
class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    fields = ('bidder', 'bid_amount', 'status', 'bid_time')
    readonly_fields = ('bid_time',)

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('auction', 'bidder', 'bid_amount', 'status', 'bid_time', 'is_verified')
    list_filter = ('status', 'is_verified', 'bid_time')
    search_fields = ('auction__title', 'bidder__email')
    readonly_fields = (
        'created_at', 'updated_at', 'ip_address',
        'verification_method'
    )
    date_hierarchy = 'bid_time'

# Auction Admin
@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'auction_type', 'status',
        'start_date', 'end_date', 'current_bid',
        'is_published'
    )
    list_filter = (
        'auction_type', 'status', 'is_published',
        'is_featured', 'start_date'
    )
    search_fields = ('title', 'slug', 'description')
    readonly_fields = (
        'slug', 'created_at', 'updated_at',
        'bid_count', 'current_bid', 'view_count',
        'registered_bidders'
    )
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'title', 'auction_type', 'status',
                'description', 'related_property'
            )
        }),
        (_('Auction Schedule'), {
            'fields': (
                'start_date', 'end_date',
                'registration_deadline'
            )
        }),
        (_('Bidding Settings'), {
            'fields': (
                'starting_bid', 'current_bid',
                'minimum_increment', 'minimum_participants',
                'auto_extend_minutes'
            )
        }),
        (_('Publication'), {
            'fields': (
                'is_published', 'is_featured',
                'terms_conditions'
            )
        }),
        (_('Notifications'), {
            'fields': ('notify_before_start', 'notify_before_end'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': (
                'bid_count', 'view_count',
                'registered_bidders'
            ),
            'classes': ('collapse',)
        }),
        (_('System Fields'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [BidInline]
    date_hierarchy = 'start_date'