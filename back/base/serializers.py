from rest_framework import serializers
from .models import Media, Property, Room, Auction, Bid

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_at']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PropertySerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True, source='room_set')
    media = MediaSerializer(many=True, read_only=True)  

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
class BidSerializer(serializers.ModelSerializer):
    bidder = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Bid
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'auction']

class AuctionSerializer(serializers.ModelSerializer):
    related_property = PropertySerializer(read_only=True)
    bids = BidSerializer(many=True, read_only=True)
    media = MediaSerializer(many=True, read_only=True)
    highest_bid = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'bid_count', 'current_bid']

    def get_highest_bid(self, obj):
        return obj.highest_bid

    def get_time_remaining(self, obj):
        return obj.time_remaining