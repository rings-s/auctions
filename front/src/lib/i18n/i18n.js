// src/lib/i18n/i18n.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Available locales
export const locales = writable({
  en: 'English',
  ar: 'العربية'
});

// Initial locale detection
function getInitialLocale() {
  if (browser) {
    const savedLocale = localStorage.getItem('locale');
    if (savedLocale) return savedLocale;
    
    const browserLang = navigator.language.split('-')[0];
    if (browserLang === 'ar') return 'ar';
  }
  return 'en'; // Default to English
}

// Current locale store
export const locale = writable(getInitialLocale());

// Set direction based on locale
if (browser) {
  locale.subscribe(value => {
    document.documentElement.lang = value;
    document.documentElement.dir = value === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.classList.remove('ltr', 'rtl');
    document.documentElement.classList.add(value === 'ar' ? 'rtl' : 'ltr');
  });
}

// Translation dictionaries
const translations = {
  en: {
    // Navigation
    nav: {
      home: 'Home',
      properties: 'Properties',
      auctions: 'Auctions',
      about: 'About',
      contact: 'Contact',
      login: 'Login',
      register: 'Register',
      logout: 'Logout',
      profile: 'My Profile',
      propertyTypes: {
        residential: 'Residential',
        commercial: 'Commercial',
        land: 'Land',
        industrial: 'Industrial',
        mixedUse: 'Mixed Use'
      }
    },
    
    // Search
    search: {
      keyword: 'Search by keyword',
      keywordPlaceholder: 'Property name, location, etc.',
      propertyType: 'Property Type',
      city: 'City',
      cityPlaceholder: 'Enter city name',
      price: 'Price Range',
      size: 'Size',
      min: 'Min',
      max: 'Max',
      search: 'Search',
      clear: 'Clear Filters',
      all: 'All',
      sort: 'Sort by',
      sortOptions: {
        newest: 'Newest first',
        priceAsc: 'Price: Low to High',
        priceDesc: 'Price: High to Low',
        sizeAsc: 'Size: Small to Large',
        sizeDesc: 'Size: Large to Small'
      }
    },
    
    // Property
    property: {
      featured: 'Featured',
      rooms: 'Rooms',
      viewDetails: 'View Details',
      features: 'Features',
      amenities: 'Amenities',
      location: 'Location',
      propertyDetails: 'Property Details',
      description: 'Description',
      marketValue: 'Market Value',
      size: 'Size',
      propertyType: 'Property Type',
      buildingType: 'Building Type',
      yearBuilt: 'Year Built',
      floors: 'Floors',
      roomList: 'Room List',
      roomType: 'Room Type',
      floor: 'Floor',
      area: 'Area',
      relatedAuctions: 'Related Auctions',
      noAuctions: 'No auctions currently listed for this property',
      contactOwner: 'Contact Owner',
      noLocationData: 'No location data available for this property'
    },
    
    // Auction
    auction: {
      featured: 'Featured',
      currentBid: 'Current Bid',
      bids: 'Bids',
      viewDetails: 'View Details',
      timeRemaining: 'Time Remaining',
      days: 'Days',
      hours: 'Hours',
      minutes: 'Min',
      seconds: 'Sec',
      statusLive: 'Live',
      statusScheduled: 'Scheduled',
      statusEnded: 'Ended',
      statusCompleted: 'Completed',
      statusDraft: 'Draft',
      typeSealed: 'Sealed Bid',
      typeReserve: 'Reserve',
      typeNoReserve: 'No Reserve',
      placeBid: 'Place Bid',
      bidAmount: 'Bid Amount',
      minimumBid: 'Minimum Bid',
      bidHistory: 'Bid History',
      noBids: 'No bids have been placed yet',
      bidderName: 'Bidder',
      bidTime: 'Time',
      bidStatus: 'Status',
      auctionDetails: 'Auction Details',
      startDate: 'Start Date',
      endDate: 'End Date',
      registrationDeadline: 'Registration Deadline',
      termsConditions: 'Terms & Conditions',
      registerForAuction: 'Register for this Auction',
      auctionEnded: 'This auction has ended',
      yourBid: 'Your Bid',
      highestBid: 'Highest Bid',
      outbid: 'You have been outbid',
      winning: 'You are currently winning',
      auctionProperty: 'Property for Auction'
    },

    // Auth
    auth: {
      login: 'Login to your account',
      email: 'Email address',
      password: 'Password',
      forgotPassword: 'Forgot password?',
      noAccount: "Don't have an account?",
      createAccount: 'Create an account',
      register: 'Register a new account',
      firstName: 'First name',
      lastName: 'Last name',
      confirmPassword: 'Confirm password',
      phoneNumber: 'Phone number',
      dateOfBirth: 'Date of birth',
      alreadyAccount: 'Already have an account?',
      signIn: 'Sign in',
      resetPassword: 'Reset your password',
      sendResetLink: 'Send reset link',
      resetInstructions: 'Enter your email address and we will send you instructions to reset your password.',
      backToLogin: 'Back to login',
      verifyEmail: 'Verify your email',
      verificationCode: 'Verification code',
      verifyAccount: 'Verify account',
      verifyInstructions: 'Enter the verification code sent to your email to activate your account.',
      resendCode: 'Resend code',
      updateProfile: 'Update your profile',
      update: 'Update',
      cancel: 'Cancel',
      logOut: 'Log out'
    },

    // Profile
    profile: {
      myProfile: 'My Profile',
      personalInfo: 'Personal Information',
      contactInfo: 'Contact Information',
      companyInfo: 'Company Information',
      preferenceInfo: 'Preferences',
      bio: 'Bio',
      companyName: 'Company Name',
      companyRegistration: 'Company Registration',
      taxId: 'Tax ID',
      address: 'Address',
      city: 'City',
      state: 'State/Province',
      postalCode: 'Postal Code',
      country: 'Country',
      licenseNumber: 'License Number',
      licenseExpiry: 'License Expiry',
      preferredLocations: 'Preferred Locations',
      propertyPreferences: 'Property Preferences',
      changePassword: 'Change Password',
      currentPassword: 'Current Password',
      newPassword: 'New Password',
      confirmNewPassword: 'Confirm New Password',
      myProperties: 'My Properties',
      myAuctions: 'My Auctions',
      myBids: 'My Bids',
      addProperty: 'Add New Property',
      addAuction: 'Create New Auction'
    },

    // Errors
    error: {
      generic: 'An error occurred',
      notFound: 'Page not found',
      unauthorized: 'Unauthorized access',
      invalidCredentials: 'Invalid email or password',
      emailTaken: 'Email is already in use',
      weakPassword: 'Password is too weak',
      passwordMismatch: 'Passwords do not match',
      serverError: 'Server error, please try again later',
      invalidToken: 'Invalid or expired token',
      notVerified: 'Email not verified',
      forbidden: 'Access forbidden',
      noResults: 'No results found'
    },

    // Footer
    footer: {
      about: 'About Us',
      aboutText: 'We are a leading real estate auction platform connecting buyers and sellers for residential, commercial, and land properties.',
      links: 'Quick Links',
      legal: 'Legal',
      terms: 'Terms of Service',
      privacy: 'Privacy Policy',
      cookies: 'Cookie Policy',
      contact: 'Contact Us',
      rights: 'All rights reserved.'
    }
  },
  
  ar: {
    // Navigation
    nav: {
      home: 'الرئيسية',
      properties: 'العقارات',
      auctions: 'المزادات',
      about: 'من نحن',
      contact: 'اتصل بنا',
      login: 'تسجيل الدخول',
      register: 'تسجيل جديد',
      logout: 'تسجيل الخروج',
      profile: 'الملف الشخصي',
      propertyTypes: {
        residential: 'سكني',
        commercial: 'تجاري',
        land: 'أرض',
        industrial: 'صناعي',
        mixedUse: 'متعدد الاستخدامات'
      }
    },
    
    // Search
    search: {
      keyword: 'بحث بالكلمات المفتاحية',
      keywordPlaceholder: 'اسم العقار، الموقع، إلخ',
      propertyType: 'نوع العقار',
      city: 'المدينة',
      cityPlaceholder: 'أدخل اسم المدينة',
      price: 'نطاق السعر',
      size: 'المساحة',
      min: 'الحد الأدنى',
      max: 'الحد الأقصى',
      search: 'بحث',
      clear: 'مسح الفلاتر',
      all: 'الكل',
      sort: 'ترتيب حسب',
      sortOptions: {
        newest: 'الأحدث أولاً',
        priceAsc: 'السعر: من الأقل إلى الأعلى',
        priceDesc: 'السعر: من الأعلى إلى الأقل',
        sizeAsc: 'المساحة: من الأصغر إلى الأكبر',
        sizeDesc: 'المساحة: من الأكبر إلى الأصغر'
      }
    },
    
    // Property
    property: {
      featured: 'مميز',
      rooms: 'غرف',
      viewDetails: 'عرض التفاصيل',
      features: 'المميزات',
      amenities: 'المرافق',
      location: 'الموقع',
      propertyDetails: 'تفاصيل العقار',
      description: 'الوصف',
      marketValue: 'القيمة السوقية',
      size: 'المساحة',
      propertyType: 'نوع العقار',
      buildingType: 'نوع المبنى',
      yearBuilt: 'سنة البناء',
      floors: 'الطوابق',
      roomList: 'قائمة الغرف',
      roomType: 'نوع الغرفة',
      floor: 'الطابق',
      area: 'المساحة',
      relatedAuctions: 'المزادات المرتبطة',
      noAuctions: 'لا توجد مزادات حالية لهذا العقار',
      contactOwner: 'التواصل مع المالك',
      noLocationData: 'لا تتوفر بيانات الموقع لهذا العقار'
    },
    
    // Auction
    auction: {
      featured: 'مميز',
      currentBid: 'المزايدة الحالية',
      bids: 'مزايدات',
      viewDetails: 'عرض التفاصيل',
      timeRemaining: 'الوقت المتبقي',
      days: 'أيام',
      hours: 'ساعات',
      minutes: 'دقائق',
      seconds: 'ثواني',
      statusLive: 'مباشر',
      statusScheduled: 'مجدول',
      statusEnded: 'منتهي',
      statusCompleted: 'مكتمل',
      statusDraft: 'مسودة',
      typeSealed: 'عطاءات مغلقة',
      typeReserve: 'بحد أدنى',
      typeNoReserve: 'بدون حد أدنى',
      placeBid: 'تقديم مزايدة',
      bidAmount: 'مبلغ المزايدة',
      minimumBid: 'الحد الأدنى للمزايدة',
      bidHistory: 'سجل المزايدات',
      noBids: 'لم يتم تقديم أي مزايدات بعد',
      bidderName: 'المزايد',
      bidTime: 'الوقت',
      bidStatus: 'الحالة',
      auctionDetails: 'تفاصيل المزاد',
      startDate: 'تاريخ البدء',
      endDate: 'تاريخ الانتهاء',
      registrationDeadline: 'الموعد النهائي للتسجيل',
      termsConditions: 'الشروط والأحكام',
      registerForAuction: 'التسجيل في هذا المزاد',
      auctionEnded: 'انتهى هذا المزاد',
      yourBid: 'مزايدتك',
      highestBid: 'أعلى مزايدة',
      outbid: 'تمت المزايدة عليك',
      winning: 'أنت الفائز حاليًا',
      auctionProperty: 'عقار المزاد'
    },

    // Auth
    auth: {
      login: 'تسجيل الدخول إلى حسابك',
      email: 'البريد الإلكتروني',
      password: 'كلمة المرور',
      forgotPassword: 'نسيت كلمة المرور؟',
      noAccount: 'ليس لديك حساب؟',
      createAccount: 'إنشاء حساب جديد',
      register: 'تسجيل حساب جديد',
      firstName: 'الاسم الأول',
      lastName: 'اسم العائلة',
      confirmPassword: 'تأكيد كلمة المرور',
      phoneNumber: 'رقم الهاتف',
      dateOfBirth: 'تاريخ الميلاد',
      alreadyAccount: 'لديك حساب بالفعل؟',
      signIn: 'تسجيل الدخول',
      resetPassword: 'إعادة تعيين كلمة المرور',
      sendResetLink: 'إرسال رابط إعادة التعيين',
      resetInstructions: 'أدخل بريدك الإلكتروني وسنرسل لك تعليمات لإعادة تعيين كلمة المرور.',
      backToLogin: 'العودة إلى تسجيل الدخول',
      verifyEmail: 'تحقق من بريدك الإلكتروني',
      verificationCode: 'رمز التحقق',
      verifyAccount: 'تحقق من الحساب',
      verifyInstructions: 'أدخل رمز التحقق المرسل إلى بريدك الإلكتروني لتفعيل حسابك.',
      resendCode: 'إعادة إرسال الرمز',
      updateProfile: 'تحديث ملفك الشخصي',
      update: 'تحديث',
      cancel: 'إلغاء',
      logOut: 'تسجيل الخروج'
    },

    // Profile
    profile: {
      myProfile: 'ملفي الشخصي',
      personalInfo: 'المعلومات الشخصية',
      contactInfo: 'معلومات الاتصال',
      companyInfo: 'معلومات الشركة',
      preferenceInfo: 'التفضيلات',
      bio: 'نبذة',
      companyName: 'اسم الشركة',
      companyRegistration: 'رقم تسجيل الشركة',
      taxId: 'الرقم الضريبي',
      address: 'العنوان',
      city: 'المدينة',
      state: 'المحافظة/المنطقة',
      postalCode: 'الرمز البريدي',
      country: 'الدولة',
      licenseNumber: 'رقم الترخيص',
      licenseExpiry: 'تاريخ انتهاء الترخيص',
      preferredLocations: 'المواقع المفضلة',
      propertyPreferences: 'تفضيلات العقارات',
      changePassword: 'تغيير كلمة المرور',
      currentPassword: 'كلمة المرور الحالية',
      newPassword: 'كلمة المرور الجديدة',
      confirmNewPassword: 'تأكيد كلمة المرور الجديدة',
      myProperties: 'عقاراتي',
      myAuctions: 'مزاداتي',
      myBids: 'مزايداتي',
      addProperty: 'إضافة عقار جديد',
      addAuction: 'إنشاء مزاد جديد'
    },

    // Errors
    error: {
      generic: 'حدث خطأ',
      notFound: 'الصفحة غير موجودة',
      unauthorized: 'دخول غير مصرح به',
      invalidCredentials: 'بريد إلكتروني أو كلمة مرور غير صحيحة',
      emailTaken: 'البريد الإلكتروني مستخدم بالفعل',
      weakPassword: 'كلمة المرور ضعيفة جدًا',
      passwordMismatch: 'كلمات المرور غير متطابقة',
      serverError: 'خطأ في الخادم، يرجى المحاولة مرة أخرى لاحقًا',
      invalidToken: 'رمز غير صالح أو منتهي الصلاحية',
      notVerified: 'البريد الإلكتروني غير مؤكد',
      forbidden: 'الوصول ممنوع',
      noResults: 'لم يتم العثور على نتائج'
    },

    // Footer
    footer: {
      about: 'من نحن',
      aboutText: 'نحن منصة رائدة لمزادات العقارات تربط المشترين والبائعين للعقارات السكنية والتجارية والأراضي.',
      links: 'روابط سريعة',
      legal: 'قانوني',
      terms: 'شروط الخدمة',
      privacy: 'سياسة الخصوصية',
      cookies: 'سياسة ملفات تعريف الارتباط',
      contact: 'اتصل بنا',
      rights: 'جميع الحقوق محفوظة.'
    }
  }
};

// Translation function
export const t = derived(
  locale,
  ($locale) => (key) => {
    // Split the key by dots to access nested properties
    const keys = key.split('.');
    let value = translations[$locale];
    
    // Navigate through the nested properties
    for (const k of keys) {
      if (value && value[k] !== undefined) {
        value = value[k];
      } else {
        console.warn(`Translation key not found: ${key} in locale ${$locale}`);
        return key; // Return the key itself if translation is not found
      }
    }
    
    return value;
  }
);



// createProperty: 'Create New Property',
//   createPropertyDesc: 'Fill in the details to add a new property to your portfolio.',
//   basicInfo: 'Basic Information',
//   basicInfoDesc: 'General information about the property',
//   location: 'Location',
//   locationDesc: 'Address and geographic coordinates',
//   details: 'Property Details',
//   detailsDesc: 'Size, construction, and special features',
//   rooms: 'Rooms',
//   roomsDesc: 'Define the rooms within this property',
//   financial: 'Financial Information',
//   financialDesc: 'Market value and bid information',
//   buildingTypes: {
//     apartment: 'Apartment',
//     villa: 'Villa',
//     building: 'Building',
//     farmhouse: 'Farmhouse',
//     shop: 'Shop',
//     office: 'Office'
//   },
//   statusTypes: {
//     available: 'Available',
//     underContract: 'Under Contract',
//     sold: 'Sold',
//     auction: 'In Auction'
//   },
//   deedNumber: 'Deed Number',
//   deedNumberHelp: 'The official property deed registration number',
//   publishingOptions: 'Publishing Options',
//   published: 'Publish Property',
//   publishedHelp: 'Make this property visible to users',
//   featured: 'Featured Property',
//   featuredHelp: 'Show this property in featured listings',
//   detectLocation: 'Detect Current Location',
//   detectLocationHelp: 'Use your current location for this property',
//   detect: 'Detect Location',
//   geolocationNotSupported: 'Geolocation is not supported by your browser',
//   locationDetected: 'Location detected successfully',
//   locationDetectionFailed: 'Failed to detect location',
//   latitude: 'Latitude',
//   longitude: 'Longitude',
//   roomName: 'Room Name',
//   roomType: 'Room Type',
//   area: 'Area',
//   roomFeatures: 'Room Features',
//   addRoom: 'Add Room',
//   roomList: 'Room List',
//   noRooms: 'No rooms added yet',
//   addRoomHelp: 'Use the form above to add rooms to this property',
//   remove: 'Remove',
//   actions: 'Actions',
//   mediaUpload: 'Media Upload',
//   mediaUploadDesc: 'Upload photos and documents for this property',
//   mediaFiles: 'Media Files',
//   uploadFiles: 'Upload files',
//   dragDrop: 'or drag and drop',
//   fileTypes: 'PNG, JPG, GIF up to 10MB',
//   selectedFiles: 'Selected Files',
//   cancel: 'Cancel',
//   create: 'Create Property',
//   marketValue: 'Market Value',
//   minimumBid: 'Minimum Bid',
//   titleRequired: 'Property title is required',
//   deedNumberRequired: 'Deed number is required',
//   marketValueRequired: 'Market value is required',
//   createSuccess: 'Property created successfully',
//   createFailed: 'Failed to create property',
//   select: 'Select',
//   commaSeparated: 'comma separated',
//   addressInfoDesc: 'Detailed location information'
// },

// auction: {
//   // ... existing translations ...
//   createAuction: 'Create New Auction',
//   createAuctionDesc: 'Set up a new auction for one of your properties',
//   basicInfo: 'Basic Information',
//   basicInfoDesc: 'General information about the auction',
//   scheduling: 'Scheduling',
//   schedulingDesc: 'Set the start, end, and registration deadline',
//   financial: 'Financial Information',
//   financialDesc: 'Starting bid and bid increment information',
//   selectProperty: 'Select Property',
//   selectPropertyDesc: 'Choose a property to auction',
//   auctionType: 'Auction Type',
//   typeSealedDesc: 'Bidders cannot see other bids until the auction ends',
//   typeReserveDesc: 'A minimum price must be met for the sale to be completed',
//   typeNoReserveDesc: 'The property will sell to the highest bidder regardless of price',
//   publishingOptions: 'Publishing Options',
//   published: 'Publish Auction',
//   publishedHelp: 'Make this auction visible to users',
//   featured: 'Featured Auction',
//   featuredHelp: 'Show this auction in featured listings',
//   registrationDeadlineHelp: 'Optional deadline for bidder registration',
//   noProperties: 'No properties found',
//   noPropertiesDesc: 'You need to create a property before you can create an auction',
//   termsConditionsText: 'Terms and Conditions Text',
//   termsConditionsHelp: 'Include any legal terms, payment conditions, or special requirements',
//   tryAgain: 'Try Again',
//   titleRequired: 'Auction title is required',
//   propertyRequired: 'You must select a property',
//   datesRequired: 'Start and end dates are required',
//   startingBidRequired: 'Starting bid is required',
//   createSuccess: 'Auction created successfully',
//   createFailed: 'Failed to create auction',
//   create: 'Create Auction',
//   cancel: 'Cancel'
// }