from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
import uuid
import os
import random

# -------------------------------------------------------------------------
# Base Model
# -------------------------------------------------------------------------
class BaseModel(models.Model):
    """Abstract base model with common fields"""
    is_deleted = models.BooleanField(_('محذوف'), default=False)
    deleted_at = models.DateTimeField(_('تاريخ الحذف'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        abstract = True

# -------------------------------------------------------------------------
# Media Models
# -------------------------------------------------------------------------
class Media(BaseModel):
    """Enhanced media model with additional fields"""
    MEDIA_TYPES = [
        ('image', _('صورة')),
        ('document', _('مستند')),
        ('video', _('فيديو')),
        ('other', _('أخرى')),
    ]

    file = models.FileField(_('الملف'), upload_to='uploads/%Y/%m/%d/')
    name = models.CharField(_('الاسم'), max_length=255, blank=True)
    media_type = models.CharField(_('نوع الوسائط'), max_length=10, choices=MEDIA_TYPES, default='other')
    file_size = models.PositiveIntegerField(_('حجم الملف'), editable=False)
    mime_type = models.CharField(_('نوع MIME'), max_length=100, blank=True)
    width = models.PositiveIntegerField(_('العرض'), null=True, blank=True)
    height = models.PositiveIntegerField(_('الارتفاع'), null=True, blank=True)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    is_primary = models.BooleanField(_('صورة رئيسية'), default=False)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('وسائط')
        verbose_name_plural = _('وسائط')
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['media_type']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = os.path.basename(self.file.name)
        
        if not self.pk: # Only set file_size on creation
            if self.file:
                 self.file_size = self.file.size
            else:
                self.file_size = 0 
            
        if self.file and not self.mime_type: # Check if file exists before accessing content_type
            try:
                self.mime_type = self.file.content_type
            except AttributeError: # Handle cases where file might not have content_type
                 self.mime_type = ''

        if self.media_type == 'image' and self.file and not (self.width and self.height): # Check if file exists
            from PIL import Image
            try:
                self.file.open() # Ensure file is open
                img = Image.open(self.file)
                self.width, self.height = img.size
                self.file.close()
            except Exception: # Catch potential errors during image processing
                pass # Or log the error
                
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.file.url if self.file else None,
            'name': self.name,
            'type': self.media_type,
            'size': self.file_size,
            'mime_type': self.mime_type,
            'dimensions': {'width': self.width, 'height': self.height} if self.media_type == 'image' else None,
            'is_primary': self.is_primary,
        }

# -------------------------------------------------------------------------
# Property Related Models
# -------------------------------------------------------------------------
class PropertyType(BaseModel):
    """Property type model"""
    name = models.CharField(_('الاسم'), max_length=50)
    code = models.CharField(_('الرمز'), max_length=10, unique=True)
    description = models.TextField(_('الوصف'), blank=True)

    class Meta:
        verbose_name = _('نوع العقار')
        verbose_name_plural = _('أنواع العقارات')

    def __str__(self):
        return self.name

class BuildingType(BaseModel):
    """Building type model"""
    name = models.CharField(_('الاسم'), max_length=50)
    code = models.CharField(_('الرمز'), max_length=10, unique=True)
    description = models.TextField(_('الوصف'), blank=True)

    class Meta:
        verbose_name = _('نوع المبنى')
        verbose_name_plural = _('أنواع المباني')

    def __str__(self):
        return self.name

class Location(BaseModel):
    """Location model"""
    city = models.CharField(_('المدينة'), max_length=100)
    state = models.CharField(_('المنطقة/المحافظة'), max_length=100)
    country = models.CharField(_('الدولة'), max_length=100, default='المملكة العربية السعودية')
    postal_code = models.CharField(_('الرمز البريدي'), max_length=20, blank=True)
    latitude = models.DecimalField(_('خط العرض'), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_('خط الطول'), max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = _('موقع')
        verbose_name_plural = _('المواقع')
        unique_together = ['city', 'state', 'country', 'postal_code']
        indexes = [
            models.Index(fields=['city', 'state']),
        ]
        
    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"

class Property(BaseModel):
    """Enhanced property model"""
    STATUS_CHOICES = [
        ('available', _('متاح')),
        ('under_contract', _('تحت العقد')),
        ('sold', _('مباع')),
        ('auction', _('في المزاد')),
    ]

    # Basic Information
    property_number = models.CharField(_('رقم العقار'), max_length=50, unique=True, blank=True)
    title = models.CharField(_('العنوان'), max_length=255)
    slug = models.SlugField(_('الرابط المختصر'), max_length=255, unique=True, blank=True)
    property_type = models.ForeignKey(
        PropertyType, 
        on_delete=models.PROTECT, 
        verbose_name=_('نوع العقار'),
        related_name='properties'  # Added related_name
    )
    building_type = models.ForeignKey(
        BuildingType, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        verbose_name=_('نوع المبنى'),
        related_name='properties'  # Added related_name
    )
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='available')

    # Deed Information
    deed_number = models.CharField(_('رقم الصك'), max_length=100, unique=True, help_text=_('رقم صك الملكية الرسمي للعقار'))

    # Property Details
    description = models.TextField(_('الوصف'))
    meta_description = models.TextField(_('وصف ميتا'), blank=True)
    search_keywords = models.TextField(_('كلمات البحث'), blank=True)
    size_sqm = models.DecimalField(_('المساحة (متر مربع)'), max_digits=10, decimal_places=2)
    floors = models.PositiveSmallIntegerField(_('عدد الطوابق'), null=True, blank=True)
    year_built = models.PositiveIntegerField(_('سنة البناء'), null=True, blank=True)

    # Location
    location = models.ForeignKey(
        Location, 
        on_delete=models.PROTECT, 
        verbose_name=_('الموقع'),
        related_name='properties'  # Added related_name
    )
    address = models.CharField(_('العنوان التفصيلي'), max_length=255)

    # Financial Information
    market_value = models.DecimalField(_('القيمة السوقية'), max_digits=14, decimal_places=2)
    minimum_bid = models.DecimalField(_('الحد الأدنى للمزايدة'), max_digits=14, decimal_places=2, null=True, blank=True)

    # Features and Amenities
    features = models.JSONField(_('المميزات'), default=list, blank=True)
    amenities = models.JSONField(_('المرافق'), default=list, blank=True)

    # Ownership and Visibility
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='owned_properties', null=True, verbose_name=_('المالك'))
    is_published = models.BooleanField(_('منشور'), default=False)
    is_featured = models.BooleanField(_('مميز'), default=False)
    is_verified = models.BooleanField(_('موثق'), default=False)
    view_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    availability_date = models.DateField(_('تاريخ التوفر'), null=True, blank=True)

    # Relations
    media = GenericRelation(Media, related_query_name='property')

    class Meta:
        verbose_name = _('عقار')
        verbose_name_plural = _('العقارات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_number']),
            models.Index(fields=['deed_number']),
            models.Index(fields=['status']),
            models.Index(fields=['market_value']),
            models.Index(fields=['property_type']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return self.title

    def get_cache_key(self):
        return f'property_{self.id}'

    def save(self, *args, **kwargs):
        if not self.property_number and self.property_type: # Ensure property_type is set
            prefix = self.property_type.code
            random_num = random.randint(10000, 99999)
            self.property_number = f"{prefix}-{random_num}"

        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            count = 1
            # Ensure slug is unique
            while Property.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        
        super().save(*args, **kwargs)
        cache.delete(self.get_cache_key())

    def get_main_image(self):
        primary_image = self.media.filter(media_type='image', is_primary=True).first()
        if primary_image:
            return primary_image
        return self.media.filter(media_type='image').first()

    def to_dict(self):
        main_image_data = None
        main_image_obj = self.get_main_image()
        if main_image_obj:
            main_image_data = main_image_obj.to_dict()

        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'property_number': self.property_number,
            'property_type': {
                'id': self.property_type.id,
                'name': self.property_type.name,
            } if self.property_type else None,
            'building_type': {
                'id': self.building_type.id,
                'name': self.building_type.name,
            } if self.building_type else None,
            'status': self.status,
            'status_display': self.get_status_display(),
            'description': self.description,
            'size_sqm': float(self.size_sqm) if self.size_sqm is not None else None,
            'location': {
                'address': self.address,
                'city': self.location.city if self.location else None,
                'state': self.location.state if self.location else None,
                'country': self.location.country if self.location else None,
            } if self.location else None,
            'market_value': float(self.market_value) if self.market_value is not None else None,
            'main_image': main_image_data,
            'media': [media_item.to_dict() for media_item in self.media.all()],
            'features': self.features,
            'amenities': self.amenities,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

# -------------------------------------------------------------------------
# Room Related Models
# -------------------------------------------------------------------------
class RoomType(BaseModel):
    """Room type model"""
    name = models.CharField(_('الاسم'), max_length=50)
    code = models.CharField(_('الرمز'), max_length=10, unique=True)
    description = models.TextField(_('الوصف'), blank=True)

    class Meta:
        verbose_name = _('نوع الغرفة')
        verbose_name_plural = _('أنواع الغرف')

    def __str__(self):
        return self.name

class Room(BaseModel):
    """Enhanced room model"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms', verbose_name=_('العقار'))
    name = models.CharField(_('اسم الغرفة'), max_length=100)
    room_type = models.ForeignKey(
        RoomType, 
        on_delete=models.PROTECT, 
        verbose_name=_('نوع الغرفة'),
        related_name='rooms'  # Added related_name
    )
    floor = models.PositiveSmallIntegerField(_('الطابق'), default=1)
    area_sqm = models.DecimalField(_('المساحة (متر مربع)'), max_digits=8, decimal_places=2, null=True, blank=True)
    description = models.TextField(_('الوصف'), blank=True)
    features = models.JSONField(_('المميزات'), default=list, blank=True)
    dimensions = models.JSONField(_('الأبعاد'), default=dict)  # {length, width, height}
    capacity = models.PositiveIntegerField(_('السعة'), null=True, blank=True)
    has_window = models.BooleanField(_('يحتوي على نافذة'), default=False)
    has_bathroom = models.BooleanField(_('يحتوي على حمام'), default=False)

    media = GenericRelation(Media, related_query_name='room')

    class Meta:
        verbose_name = _('غرفة')
        verbose_name_plural = _('الغرف')
        ordering = ['floor', 'room_type']
        indexes = [
            models.Index(fields=['property', 'floor']),
            models.Index(fields=['room_type']),
        ]

    def __str__(self):
        return f"{self.room_type.name if self.room_type else 'N/A'} - {self.name} ({self.property.title if self.property else 'N/A'})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'room_type': {
                'id': self.room_type.id,
                'name': self.room_type.name,
            } if self.room_type else None,
            'floor': self.floor,
            'area_sqm': float(self.area_sqm) if self.area_sqm else None,
            'dimensions': self.dimensions,
            'features': self.features,
            'media': [media_item.to_dict() for media_item in self.media.all()],
        }

# -------------------------------------------------------------------------
# Auction Related Models
# -------------------------------------------------------------------------
class AuctionType(BaseModel):
    """Auction type model"""
    name = models.CharField(_('الاسم'), max_length=50)
    code = models.CharField(_('الرمز'), max_length=10, unique=True)
    description = models.TextField(_('الوصف'), blank=True)

    class Meta:
        verbose_name = _('نوع المزاد')
        verbose_name_plural = _('أنواع المزادات')

    def __str__(self):
        return self.name

class Auction(BaseModel):
    """Enhanced auction model"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('scheduled', _('مجدول')),
        ('live', _('مباشر')),
        ('ended', _('منتهي')),
        ('cancelled', _('ملغي')),
        ('completed', _('مكتمل')),
    ]

    title = models.CharField(_('العنوان'), max_length=255)
    slug = models.SlugField(_('الرابط المختصر'), max_length=255, unique=True, blank=True)
    auction_type = models.ForeignKey(
        AuctionType, 
        on_delete=models.PROTECT, 
        verbose_name=_('نوع المزاد'),
        related_name='auctions'  # Added related_name
    )
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='draft')
    description = models.TextField(_('الوصف'))

    start_date = models.DateTimeField(_('تاريخ البدء'))
    end_date = models.DateTimeField(_('تاريخ الانتهاء'))
    registration_deadline = models.DateTimeField(_('موعد انتهاء التسجيل'), null=True, blank=True)

    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='auctions', verbose_name=_('العقار'))

    starting_bid = models.DecimalField(_('المزايدة الأولية'), max_digits=14, decimal_places=2)
    current_bid = models.DecimalField(_('المزايدة الحالية'), max_digits=14, decimal_places=2, null=True, blank=True)
    minimum_increment = models.DecimalField(_('الحد الأدنى للزيادة'), max_digits=14, decimal_places=2, default=100.00)
    minimum_participants = models.PositiveIntegerField(_('الحد الأدنى للمشاركين'), default=1)
    auto_extend_minutes = models.PositiveIntegerField(_('تمديد تلقائي (دقائق)'), default=0)

    is_published = models.BooleanField(_('منشور'), default=False)
    is_featured = models.BooleanField(_('مميز'), default=False)

    terms_conditions = models.TextField(_('الشروط والأحكام'), blank=True)
    
    view_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    bid_count = models.PositiveIntegerField(_('عدد المزايدات'), default=0)
    registered_bidders = models.PositiveIntegerField(_('المزايدين المسجلين'), default=0)

    notify_before_start = models.PositiveIntegerField(_('إشعار قبل البدء (دقائق)'), default=60)
    notify_before_end = models.PositiveIntegerField(_('إشعار قبل الانتهاء (دقائق)'), default=30)

    media = GenericRelation(Media, related_query_name='auction')

    class Meta:
        verbose_name = _('مزاد')
        verbose_name_plural = _('المزادات')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['related_property']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            count = 1
            while Auction.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1

        if self.is_published and self.status in ['scheduled', 'live'] and self.related_property:
            self.related_property.status = 'auction'
            self.related_property.save(update_fields=['status'])

        super().save(*args, **kwargs)

    @property
    def time_remaining(self):
        if not self.end_date or self.end_date <= timezone.now():
            return {"days": 0, "hours": 0, "minutes": 0, "seconds": 0, "total_seconds": 0}
        
        time_left = self.end_date - timezone.now()
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": time_left.total_seconds()
        }

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'auction_type': {
                'id': self.auction_type.id,
                'name': self.auction_type.name,
            } if self.auction_type else None,
            'status': self.status,
            'status_display': self.get_status_display(),
            'description': self.description,
            'dates': {
                'start': self.start_date.isoformat() if self.start_date else None,
                'end': self.end_date.isoformat() if self.end_date else None,
                'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            },
            'property': self.related_property.to_dict() if self.related_property else None,
            'bids': {
                'starting': float(self.starting_bid) if self.starting_bid is not None else None,
                'current': float(self.current_bid) if self.current_bid is not None else None,
                'minimum_increment': float(self.minimum_increment) if self.minimum_increment is not None else None,
                'count': self.bid_count,
            },
            'time_remaining': self.time_remaining,
            'media': [media_item.to_dict() for media_item in self.media.all()],
        }

class Bid(BaseModel):
    """Enhanced bid model"""
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('accepted', _('مقبولة')),
        ('rejected', _('مرفوضة')),
        ('outbid', _('تمت المزايدة بأعلى')),
        ('winning', _('فائزة')),
    ]

    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids', verbose_name=_('المزاد'))
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids', verbose_name=_('المزايد'))
    bid_amount = models.DecimalField(_('مبلغ المزايدة'), max_digits=14, decimal_places=2)
    max_bid_amount = models.DecimalField(_('الحد الأقصى للمزايدة'), max_digits=14, decimal_places=2, null=True, blank=True)
    bid_time = models.DateTimeField(_('وقت المزايدة'), default=timezone.now)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    ip_address = models.GenericIPAddressField(_('عنوان IP'), null=True, blank=True)
    user_agent = models.TextField(_('معلومات المتصفح'), blank=True)
    is_verified = models.BooleanField(_('تم التحقق'), default=False)
    verification_method = models.CharField(_('طريقة التحقق'), max_length=50, blank=True)

    class Meta:
        verbose_name = _('مزايدة')
        verbose_name_plural = _('المزايدات')
        ordering = ['-bid_time']
        indexes = [
            models.Index(fields=['auction', '-bid_time']),
            models.Index(fields=['bidder']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        bidder_name = f"{self.bidder.first_name} {self.bidder.last_name}".strip() or self.bidder.email if self.bidder else "N/A Bidder"
        auction_title = self.auction.title if self.auction else "N/A Auction"
        return f"{bidder_name} زايد بمبلغ {self.bid_amount} على {auction_title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs) # Save first to get a PK if new

        if is_new and self.auction:
            self.auction.bid_count = models.F('bid_count') + 1 # Use F expression for atomicity

            if not self.auction.current_bid or self.bid_amount > self.auction.current_bid:
                self.auction.current_bid = self.bid_amount

                # Atomically update previous winning bids to 'outbid'
                if self.status == 'accepted' or self.status == 'winning': # Consider new winning bids directly
                    Bid.objects.filter(
                        auction=self.auction,
                        status='winning'
                    ).exclude(id=self.id).update(status='outbid')
                    
                    if self.status != 'winning': # If it was 'accepted', now make it 'winning'
                        self.status = 'winning'
                        super().save(update_fields=['status']) # Save just the status field


            self.auction.save(update_fields=['bid_count', 'current_bid'])

    def to_dict(self):
        bidder_info = None
        if self.bidder:
            bidder_name = f"{self.bidder.first_name} {self.bidder.last_name}".strip()
            bidder_info = {
                'id': self.bidder.id,
                'name': bidder_name or self.bidder.email,
            }
        return {
            'id': self.id,
            'auction_id': self.auction_id,
            'bidder': bidder_info,
            'amount': float(self.bid_amount) if self.bid_amount is not None else None,
            'max_amount': float(self.max_bid_amount) if self.max_bid_amount is not None else None,
            'status': self.status,
            'status_display': self.get_status_display(),
            'bid_time': self.bid_time.isoformat() if self.bid_time else None,
            'is_verified': self.is_verified,
        }