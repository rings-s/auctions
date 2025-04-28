from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
import uuid
import os
import random

# -------------------------------------------------------------------------
# نموذج الوسائط المبسط
# -------------------------------------------------------------------------
class Media(models.Model):
    """نموذج مبسط للوسائط (صور، مستندات، فيديو)"""
    MEDIA_TYPES = [
        ('image', _('صورة')),
        ('document', _('مستند')),
        ('video', _('فيديو')),
        ('other', _('أخرى')),
    ]

    file = models.FileField(_('الملف'), upload_to='uploads/%Y/%m/%d/')
    name = models.CharField(_('الاسم'), max_length=255, blank=True)
    media_type = models.CharField(_('نوع الوسائط'), max_length=10, choices=MEDIA_TYPES, default='other')
    uploaded_at = models.DateTimeField(_('تاريخ الرفع'), auto_now_add=True)
    
    # حقول العلاقة العامة
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('وسائط')
        verbose_name_plural = _('وسائط')
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = os.path.basename(self.file.name)
        
        # الكشف التلقائي عن نوع الوسائط من امتداد الملف
        if not self.pk or self.media_type == 'other':
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                self.media_type = 'image'
            elif ext in ['.pdf', '.doc', '.docx', '.txt']:
                self.media_type = 'document'
            elif ext in ['.mp4', '.mov', '.avi']:
                self.media_type = 'video'
                
        super().save(*args, **kwargs)

# -------------------------------------------------------------------------
# نموذج العقار
# -------------------------------------------------------------------------
class Property(models.Model):
    """نموذج العقار المحدث (بدون حقل غرف النوم)"""
    PROPERTY_TYPES = [
        ('residential', _('سكني')),
        ('commercial', _('تجاري')),
        ('land', _('أرض')),
        ('industrial', _('صناعي')),
        ('mixed_use', _('متعدد الاستخدامات')),
    ]
    
    BUILDING_TYPES = [
        ('apartment', _('شقة')),
        ('villa', _('فيلا')),
        ('building', _('مبنى')),
        ('farmhouse', _('مزرعة')),
        ('shop', _('محل تجاري')),
        ('office', _('مكتب')),
    ]
    
    STATUS_CHOICES = [
        ('available', _('متاح')),
        ('under_contract', _('تحت العقد')),
        ('sold', _('مباع')),
        ('auction', _('في المزاد')),
    ]
    
    # معلومات أساسية
    property_number = models.CharField(_('رقم العقار'), max_length=50, unique=True, blank=True)
    title = models.CharField(_('العنوان'), max_length=255)
    slug = models.SlugField(_('الرابط المختصر'), max_length=255, unique=True, blank=True)
    property_type = models.CharField(_('نوع العقار'), max_length=20, choices=PROPERTY_TYPES)
    building_type = models.CharField(_('نوع المبنى'), max_length=20, choices=BUILDING_TYPES, blank=True, null=True)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='available')
    
    # معلومات الصك
    deed_number = models.CharField(_('رقم الصك'), max_length=100, unique=True, help_text=_('رقم صك الملكية الرسمي للعقار'))
    
    # تفاصيل العقار
    description = models.TextField(_('الوصف'))
    size_sqm = models.DecimalField(_('المساحة (متر مربع)'), max_digits=10, decimal_places=2)
    floors = models.PositiveSmallIntegerField(_('عدد الطوابق'), null=True, blank=True)
    year_built = models.PositiveIntegerField(_('سنة البناء'), null=True, blank=True)
    
    # الموقع
    address = models.CharField(_('العنوان'), max_length=255)
    city = models.CharField(_('المدينة'), max_length=100)
    state = models.CharField(_('المنطقة/المحافظة'), max_length=100)
    postal_code = models.CharField(_('الرمز البريدي'), max_length=20, blank=True)
    country = models.CharField(_('الدولة'), max_length=100, default='المملكة العربية السعودية')
    
    # الإحداثيات
    latitude = models.DecimalField(_('خط العرض'), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_('خط الطول'), max_digits=9, decimal_places=6, null=True, blank=True)
    
    # المعلومات المالية
    market_value = models.DecimalField(_('القيمة السوقية'), max_digits=14, decimal_places=2)
    minimum_bid = models.DecimalField(_('الحد الأدنى للمزايدة'), max_digits=14, decimal_places=2, null=True, blank=True)
    
    # المميزات
    features = models.JSONField(_('المميزات'), default=list, blank=True)
    amenities = models.JSONField(_('المرافق'), default=list, blank=True)
    
    # الملكية والرؤية - استخدام نموذج المستخدم من تطبيق الحسابات
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='owned_properties', 
        null=True, 
        verbose_name=_('المالك')
    )
    is_published = models.BooleanField(_('منشور'), default=False)
    is_featured = models.BooleanField(_('مميز'), default=False)
    is_verified = models.BooleanField(_('موثق'), default=False)
    view_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    
    # علاقة الوسائط
    media = GenericRelation(Media, related_query_name='property')
    
    # الطوابع الزمنية
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('عقار')
        verbose_name_plural = _('العقارات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_number']),
            models.Index(fields=['deed_number']),
            models.Index(fields=['status']),
            models.Index(fields=['city', 'property_type']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # إنشاء رقم العقار إذا لم يتم توفيره
        if not self.property_number:
            prefix = self.property_type[:3].upper()
            random_num = random.randint(10000, 99999)
            self.property_number = f"{prefix}-{random_num}"
            
        # إنشاء الرابط المختصر إذا لم يتم توفيره
        if not self.slug:
            self.slug = slugify(self.title)
            
            # ضمان تفرد الرابط المختصر
            original_slug = self.slug
            count = 1
            while Property.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
                
        super().save(*args, **kwargs)
    
    def get_main_image(self):
        """إرجاع رابط الصورة الرئيسية للعقار"""
        main_image = self.media.filter(media_type='image').first()
        if main_image:
            return main_image.file.url
        return None

    def to_dict(self):
        """إرجاع تمثيل قاموس مناسب للواجهة الأمامية"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'property_number': self.property_number,
            'property_type': self.property_type,
            'property_type_display': self.get_property_type_display(),
            'deed_number': self.deed_number,
            'status': self.status,
            'status_display': self.get_status_display(),
            'description': self.description[:250] + '...' if len(self.description) > 250 else self.description,
            'address': self.address,
            'city': self.city,
            'size_sqm': float(self.size_sqm),
            'market_value': float(self.market_value),
            'main_image': self.get_main_image(),
            'rooms_count': self.rooms.count(),
            'created_at': self.created_at.isoformat(),
        }

# -------------------------------------------------------------------------
# نموذج الغرفة
# -------------------------------------------------------------------------
class Room(models.Model):
    """نموذج لتفاصيل غرف العقار"""
    ROOM_TYPES = [
        ('bedroom', _('غرفة نوم')),
        ('bathroom', _('حمام')),
        ('kitchen', _('مطبخ')),
        ('living', _('غرفة معيشة')),
        ('dining', _('غرفة طعام')),
        ('office', _('مكتب')),
        ('storage', _('مخزن')),
        ('other', _('أخرى')),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms', verbose_name=_('العقار'))
    name = models.CharField(_('اسم الغرفة'), max_length=100)
    room_type = models.CharField(_('نوع الغرفة'), max_length=20, choices=ROOM_TYPES)
    floor = models.PositiveSmallIntegerField(_('الطابق'), default=1)
    area_sqm = models.DecimalField(_('المساحة (متر مربع)'), max_digits=8, decimal_places=2, null=True, blank=True)
    description = models.TextField(_('الوصف'), blank=True)
    features = models.JSONField(_('المميزات'), default=list, blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('غرفة')
        verbose_name_plural = _('الغرف')
        ordering = ['floor', 'room_type']
    
    def __str__(self):
        return f"{self.get_room_type_display()} - {self.name} ({self.property.title})"

# -------------------------------------------------------------------------
# نموذج المزاد
# -------------------------------------------------------------------------
class Auction(models.Model):
    """نموذج مزاد محسّن للتكامل مع واجهة المستخدم"""
    AUCTION_TYPES = [
        ('sealed', _('مزاد العطاءات المغلقة')),
        ('reserve', _('مزاد بحد أدنى')),
        ('no_reserve', _('مزاد بدون حد أدنى')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('scheduled', _('مجدول')),
        ('live', _('مباشر')),
        ('ended', _('منتهي')),
        ('cancelled', _('ملغي')),
        ('completed', _('مكتمل')),
    ]
    
    # المعلومات الأساسية
    title = models.CharField(_('العنوان'), max_length=255)
    slug = models.SlugField(_('الرابط المختصر'), max_length=255, unique=True, blank=True)
    auction_type = models.CharField(_('نوع المزاد'), max_length=20, choices=AUCTION_TYPES)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='draft')
    description = models.TextField(_('الوصف'))
    
    # التواريخ
    start_date = models.DateTimeField(_('تاريخ البدء'))
    end_date = models.DateTimeField(_('تاريخ الانتهاء'))
    registration_deadline = models.DateTimeField(_('موعد انتهاء التسجيل'), null=True, blank=True)
    
    # العقار المرتبط
    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='auctions', verbose_name=_('العقار'))
    
    # التفاصيل المالية
    starting_bid = models.DecimalField(_('المزايدة الأولية'), max_digits=14, decimal_places=2)
    current_bid = models.DecimalField(_('المزايدة الحالية'), max_digits=14, decimal_places=2, null=True, blank=True)
    minimum_increment = models.DecimalField(_('الحد الأدنى للزيادة'), max_digits=14, decimal_places=2, default=100.00)
    
    # إعدادات الرؤية
    is_published = models.BooleanField(_('منشور'), default=False)
    is_featured = models.BooleanField(_('مميز'), default=False)
    
    # الشروط والأحكام
    terms_conditions = models.TextField(_('الشروط والأحكام'), blank=True)
    
    # الإحصائيات
    view_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    bid_count = models.PositiveIntegerField(_('عدد المزايدات'), default=0)
    registered_bidders = models.PositiveIntegerField(_('المزايدين المسجلين'), default=0)
    
    # علاقة الوسائط
    media = GenericRelation(Media, related_query_name='auction')
    
    # الطوابع الزمنية
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
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
        # إنشاء الرابط المختصر إذا لم يتم توفيره
        if not self.slug:
            self.slug = slugify(self.title)
            
            # ضمان تفرد الرابط المختصر
            original_slug = self.slug
            count = 1
            while Auction.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
                
        # تحديث حالة العقار عند نشر المزاد
        if self.is_published and self.status in ['scheduled', 'live']:
            self.related_property.status = 'auction'
            self.related_property.save(update_fields=['status'])
            
        super().save(*args, **kwargs)
    
    @property
    def time_remaining(self):
        """حساب الوقت المتبقي للمزاد"""
        if self.end_date <= timezone.now():
            return {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}
            
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
    
    @property
    def highest_bid(self):
        """إرجاع معلومات أعلى مزايدة"""
        highest = self.bids.filter(status__in=['accepted', 'winning']).order_by('-bid_amount').first()
        if not highest:
            return None
            
        return {
            "amount": float(highest.bid_amount),
            "bidder": {
                "id": highest.bidder.id,
                "name": f"{highest.bidder.first_name} {highest.bidder.last_name}" or highest.bidder.email
            },
            "time": highest.bid_time.isoformat()
        }

# -------------------------------------------------------------------------
# نموذج المزايدة
# -------------------------------------------------------------------------
class Bid(models.Model):
    """نموذج المزايدة المبسط"""
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('accepted', _('مقبولة')),
        ('rejected', _('مرفوضة')),
        ('outbid', _('تمت المزايدة بأعلى')),
        ('winning', _('فائزة')),
    ]
    
    auction = models.ForeignKey('base.Auction', on_delete=models.CASCADE, related_name='bids', verbose_name=_('المزاد'))
    # استخدام نموذج المستخدم من تطبيق الحسابات
    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bids', 
        verbose_name=_('المزايد')
    )
    bid_amount = models.DecimalField(_('مبلغ المزايدة'), max_digits=14, decimal_places=2)
    bid_time = models.DateTimeField(_('وقت المزايدة'), default=timezone.now)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
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
        return f"{self.bidder} زايد بمبلغ {self.bid_amount} على {self.auction.title}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # تحديث عدد المزايدات والمزايدة الحالية
            self.auction.bid_count += 1
            
            if not self.auction.current_bid or self.bid_amount > self.auction.current_bid:
                self.auction.current_bid = self.bid_amount
                
                # تحديث حالة المزايدات
                if self.status == 'accepted':
                    # تحديث جميع المزايدات الأخرى كـ "تمت المزايدة بأعلى"
                    Bid.objects.filter(
                        auction=self.auction,
                        status='winning'
                    ).exclude(id=self.id).update(status='outbid')
                    
                    # تحديث هذه المزايدة كـ "فائزة"
                    self.status = 'winning'
                    self.save(update_fields=['status'])
            
            # حفظ تحديثات المزاد
            self.auction.save(update_fields=['bid_count', 'current_bid'])