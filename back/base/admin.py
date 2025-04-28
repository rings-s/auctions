from django.contrib import admin
from .models import Media, Property, Room, Auction, Bid

class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'media_type', 'uploaded_at', 'content_type', 'object_id')
    search_fields = ('name',)
    list_filter = ('media_type', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'property_type', 'status', 'city', 'created_at')
    search_fields = ('title', 'slug', 'deed_number', 'city')
    list_filter = ('property_type', 'status', 'city')
    inlines = [RoomInline]
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0

class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'auction_type', 'status', 'related_property', 'start_date', 'end_date', 'is_published')
    search_fields = ('title', 'slug', 'description')
    list_filter = ('auction_type', 'status', 'is_published', 'start_date')
    inlines = [BidInline]
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at', 'bid_count', 'current_bid')

class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'bidder', 'bid_amount', 'bid_time', 'status')
    search_fields = ('auction__title', 'bidder__email')
    list_filter = ('status', 'bid_time')
    date_hierarchy = 'bid_time'
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Media, MediaAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Room)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
