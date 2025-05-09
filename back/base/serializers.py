from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
   Media, Property, Room, Auction, Bid,
   PropertyType, BuildingType, Location, RoomType,
   AuctionType
)

class BaseTypeSerializer(serializers.ModelSerializer):
   """Base serializer for type models"""
   class Meta:
       abstract = True
       fields = ['id', 'name', 'code', 'created_at', 'updated_at']
       read_only_fields = ['created_at', 'updated_at']

class MediaSerializer(serializers.ModelSerializer):
   url = serializers.SerializerMethodField()
   size = serializers.SerializerMethodField()

   class Meta:
       model = Media
       fields = [
           'id', 'url', 'name', 'media_type', 
           'size', 'mime_type', 'width', 'height',
           'is_primary', 'created_at'
       ]
       read_only_fields = [
           'size', 'mime_type', 'width', 
           'height', 'created_at'
       ]

   def get_url(self, obj):
       return obj.file.url if obj.file else None

   def get_size(self, obj):
       return obj.file_size if obj.file else 0

   def validate_file(self, value):
       if value.size > 10 * 1024 * 1024:  # 10MB
           raise serializers.ValidationError(_("File size cannot exceed 10MB"))
       return value

class PropertyTypeSerializer(BaseTypeSerializer):
   class Meta(BaseTypeSerializer.Meta):
       model = PropertyType

class BuildingTypeSerializer(BaseTypeSerializer):
   class Meta(BaseTypeSerializer.Meta):
       model = BuildingType

class RoomTypeSerializer(BaseTypeSerializer):
   class Meta(BaseTypeSerializer.Meta):
       model = RoomType

class AuctionTypeSerializer(BaseTypeSerializer):
   class Meta(BaseTypeSerializer.Meta):
       model = AuctionType

class LocationSerializer(serializers.ModelSerializer):
   class Meta:
       model = Location
       fields = [
           'id', 'city', 'state', 'country',
           'postal_code', 'latitude', 'longitude'
       ]

   def validate(self, attrs):
       if any([attrs.get('latitude'), attrs.get('longitude')]):
           if not all([attrs.get('latitude'), attrs.get('longitude')]):
               raise serializers.ValidationError(
                   _("Both latitude and longitude must be provided")
               )
       return attrs

class RoomSerializer(serializers.ModelSerializer):
   type = RoomTypeSerializer(source='room_type', read_only=True)
   media = MediaSerializer(many=True, read_only=True)

   class Meta:
       model = Room
       fields = [
           'id', 'name', 'type', 'floor', 
           'area_sqm', 'dimensions', 'features',
           'has_window', 'has_bathroom', 'media'
       ]

   def validate_dimensions(self, value):
       if not isinstance(value, dict):
           raise serializers.ValidationError(
               _("Dimensions must be a JSON object")
           )
       
       required = ['length', 'width', 'height']
       missing = [key for key in required if key not in value]
       
       if missing:
           raise serializers.ValidationError(
               _("Missing dimensions: {}").format(", ".join(missing))
           )
       return value

class PropertySerializer(serializers.ModelSerializer):
   type = PropertyTypeSerializer(source='property_type', read_only=True)
   building = BuildingTypeSerializer(source='building_type', read_only=True)
   location = LocationSerializer(read_only=True)
   rooms = RoomSerializer(many=True, read_only=True)
   media = MediaSerializer(many=True, read_only=True)
   main_image = serializers.SerializerMethodField()
   status_display = serializers.CharField(source='get_status_display', read_only=True)

   class Meta:
       model = Property
       fields = [
           'id', 'title', 'property_number', 'type', 'property_type',
           'building', 'building_type', 'status', 'status_display',
           'deed_number', 'description', 'size_sqm',
           'floors', 'year_built', 'location',
           'market_value', 'minimum_bid', 'features',
           'amenities', 'owner', 'is_published',
           'is_featured', 'is_verified', 'rooms',
           'media', 'main_image', 'created_at'
       ]
       read_only_fields = [
           'property_number', 'owner', 'created_at'
       ]

   def get_main_image(self, obj):
       image = obj.get_main_image()
       return MediaSerializer(image).data if image else None

   def validate(self, data):
       if 'property_type' not in data or not data['property_type']:
           raise serializers.ValidationError({'property_type': _('Property type is required.')})

       if 'minimum_bid' in data and 'market_value' in data:
           if data['minimum_bid'] >= data['market_value']:
               raise serializers.ValidationError(
                   _("Minimum bid must be less than market value")
               )

       if 'year_built' in data and data['year_built'] > 2025:
           raise serializers.ValidationError(
               _("Year built cannot be in the future")
           )

       return data

   def create(self, validated_data):
       property_type_data = validated_data.pop('property_type', None)
       if property_type_data is None:
           raise serializers.ValidationError({'property_type': 'Property type is required.'})

       property_type = None
       if isinstance(property_type_data, int):
           try:
               property_type = PropertyType.objects.get(id=property_type_data)
           except PropertyType.DoesNotExist:
               raise serializers.ValidationError({'property_type': 'Invalid property type'})
       elif isinstance(property_type_data, str):
           try:
               property_type = PropertyType.objects.get(code=property_type_data)
           except PropertyType.DoesNotExist:
               try:
                   property_type = PropertyType.objects.get(id=property_type_data)
               except (PropertyType.DoesNotExist, ValueError):
                   raise serializers.ValidationError({'property_type': 'Invalid property type'})
       else:
           raise serializers.ValidationError({'property_type': 'Invalid property type'})

       validated_data['property_type'] = property_type
       return super().create(validated_data)

class BidSerializer(serializers.ModelSerializer):
   bidder_info = serializers.SerializerMethodField()
   auction_info = serializers.SerializerMethodField()
   status_display = serializers.CharField(source='get_status_display', read_only=True)

   class Meta:
       model = Bid
       fields = [
           'id', 'auction', 'auction_info',
           'bidder', 'bidder_info', 'bid_amount',
           'status', 'status_display', 'bid_time',
           'is_verified'
       ]
       read_only_fields = [
           'bidder', 'status', 'bid_time', 
           'is_verified'
       ]

   def get_bidder_info(self, obj):
       return {
           'id': obj.bidder.id,
           'name': f"{obj.bidder.first_name} {obj.bidder.last_name}".strip() or obj.bidder.email,
           'email': obj.bidder.email
       }

   def get_auction_info(self, obj):
       return {
           'id': obj.auction.id,
           'title': obj.auction.title,
           'current_bid': obj.auction.current_bid
       }

   def validate(self, data):
       auction = data.get('auction')
       if not auction:
           raise serializers.ValidationError(_("Auction is required"))

       bid_amount = data.get('bid_amount')
       current_bid = auction.current_bid or auction.starting_bid
       min_increment = auction.minimum_increment

       if bid_amount <= current_bid + min_increment:
           raise serializers.ValidationError(
               _("Bid must be at least {} higher than current bid").format(min_increment)
           )

       return data

class AuctionSerializer(serializers.ModelSerializer):
   type = AuctionTypeSerializer(source='auction_type', read_only=True)
   property = PropertySerializer(source='related_property', read_only=True)
   bids = BidSerializer(many=True, read_only=True)
   media = MediaSerializer(many=True, read_only=True)
   status_display = serializers.CharField(source='get_status_display', read_only=True)
   time_remaining = serializers.SerializerMethodField()
   highest_bid = serializers.SerializerMethodField()

   class Meta:
       model = Auction
       fields = [
           'id', 'title', 'type', 'status',
           'status_display', 'description',
           'start_date', 'end_date',
           'registration_deadline', 'property',
           'starting_bid', 'current_bid',
           'minimum_increment', 'minimum_participants',
           'is_published', 'bids', 'media',
           'time_remaining', 'highest_bid',
           'created_at'
       ]
       read_only_fields = [
           'current_bid', 'created_at'
       ]

   def get_time_remaining(self, obj):
       return obj.time_remaining

   def get_highest_bid(self, obj):
       highest_bid = obj.bids.order_by('-bid_amount').first()
       return BidSerializer(highest_bid).data if highest_bid else None

   def validate(self, data):
       if 'end_date' in data and 'start_date' in data:
           if data['end_date'] <= data['start_date']:
               raise serializers.ValidationError(
                   _("End date must be after start date")
               )

       if 'registration_deadline' in data and 'start_date' in data:
           if data['registration_deadline'] >= data['start_date']:
               raise serializers.ValidationError(
                   _("Registration deadline must be before start date")
               )

       return data