<!-- src/routes/properties/create/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { t } from '$lib/i18n/i18n';
  import { user } from '$lib/stores/user';
  import { createProperty, uploadPropertyMedia } from '$lib/api/property';
  
  import TagSelector from '$lib/components/TagSelector.svelte';
  import MediaUploader from '$lib/components/MediaUploader.svelte';
  import RoomManager from '$lib/components/RoomManager.svelte';
  import LocationPicker from '$lib/components/LocationPicker.svelte';
  
  // Create a default property object
  let propertyData = {
    title: '',
    slug: '',
    property_type: 'residential',
    building_type: '',
    status: 'available',
    deed_number: '',
    description: '',
    size_sqm: '',
    floors: '',
    year_built: '',
    address: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'المملكة العربية السعودية',
    latitude: null,
    longitude: null,
    market_value: '',
    minimum_bid: '',
    features: [],
    amenities: [],
    is_published: false,
    is_featured: false
  };
  
  let rooms = [];
  let activeTab = 'basic';
  let step = 1;
  let loading = false;
  let error = '';
  let success = '';
  let mediaFiles = [];
  let uploadingMedia = false;
  let propertyId = null;
  let totalSteps = 5; // Total number of steps in the form
  
  // Features and amenities lists
  let availableFeatures = [
    'Balcony', 'Garden', 'Pool', 'Garage', 'Parking', 'Elevator', 
    'Security System', 'Central AC', 'Fiber Internet', 'Smart Home', 
    'Solar Panels', 'Fire Place', 'Storage Room'
  ];
  
  let availableAmenities = [
    'Gym', 'Sauna', 'Jacuzzi', 'Swimming Pool', 'Tennis Court', 
    'Basketball Court', 'Children Playground', 'BBQ Area', 
    'Walking Trails', 'Community Center', 'Mosque', 'Supermarket'
  ];

  onMount(() => {
    // Check if user is logged in
    if (!$user) {
      goto('/login?redirect=/properties/create');
    }
  });

  function nextStep() {
    if (step < totalSteps) {
      step++;
      updateTabBasedOnStep();
    }
  }

  function prevStep() {
    if (step > 1) {
      step--;
      updateTabBasedOnStep();
    }
  }

  function updateTabBasedOnStep() {
    switch(step) {
      case 1:
        activeTab = 'basic';
        break;
      case 2:
        activeTab = 'location';
        break;
      case 3:
        activeTab = 'details';
        break;
      case 4:
        activeTab = 'rooms';
        break;
      case 5:
        activeTab = 'financial';
        break;
    }
  }

  function setTab(tab) {
    activeTab = tab;
    // Update step based on tab
    switch(tab) {
      case 'basic':
        step = 1;
        break;
      case 'location':
        step = 2;
        break;
      case 'details':
        step = 3;
        break;
      case 'rooms':
        step = 4;
        break;
      case 'financial':
        step = 5;
        break;
    }
  }
  
  function handleFeaturesChange(event) {
    propertyData.features = event.detail;
  }
  
  function handleAmenitiesChange(event) {
    propertyData.amenities = event.detail;
  }
  
  function handleRoomsChange(event) {
    rooms = event.detail;
  }
  
  function handleMediaChange(event) {
    mediaFiles = event.detail;
  }
  
  function handleLocationChange(event) {
    propertyData.latitude = event.detail.latitude;
    propertyData.longitude = event.detail.longitude;
  }
  
  function handleAddressChange(event) {
    propertyData.address = event.detail.address;
    propertyData.city = event.detail.city;
    propertyData.state = event.detail.state;
    propertyData.postal_code = event.detail.postalCode;
    propertyData.country = event.detail.country;
  }

  function validateForm() {
    error = '';
    
    // Basic validation
    if (!propertyData.title) {
      error = $t('property.titleRequired');
      return false;
    }
    
    if (!propertyData.deed_number) {
      error = $t('property.deedNumberRequired');
      return false;
    }
    
    if (!propertyData.market_value) {
      error = $t('property.marketValueRequired');
      return false;
    }
    
    return true;
  }
  
  function prepareDataForSubmission() {
    const preparedProperty = { ...propertyData };
    
    // Convert numeric fields to numbers
    if (typeof preparedProperty.size_sqm === 'string' && preparedProperty.size_sqm) {
      preparedProperty.size_sqm = parseFloat(preparedProperty.size_sqm) || 0;
    }
    
    if (typeof preparedProperty.market_value === 'string' && preparedProperty.market_value) {
      preparedProperty.market_value = parseFloat(preparedProperty.market_value) || 0;
    }
    
    if (typeof preparedProperty.minimum_bid === 'string' && preparedProperty.minimum_bid) {
      preparedProperty.minimum_bid = parseFloat(preparedProperty.minimum_bid) || null;
    }
    
    if (typeof preparedProperty.floors === 'string' && preparedProperty.floors) {
      preparedProperty.floors = parseInt(preparedProperty.floors) || null;
    }
    
    if (typeof preparedProperty.year_built === 'string' && preparedProperty.year_built) {
      preparedProperty.year_built = parseInt(preparedProperty.year_built) || null;
    }
    
    // Prepare rooms data
    const preparedRooms = rooms.map(room => {
      const preparedRoom = { ...room };
      
      // Ensure numeric fields are numbers
      if (typeof preparedRoom.area_sqm === 'string' && preparedRoom.area_sqm) {
        preparedRoom.area_sqm = parseFloat(preparedRoom.area_sqm) || null;
      }
      
      if (typeof preparedRoom.floor === 'string') {
        preparedRoom.floor = parseInt(preparedRoom.floor) || 1;
      }
      
      return preparedRoom;
    });
    
    return { property: preparedProperty, rooms: preparedRooms };
  }

  async function handleSubmit() {
    try {
      // Prevent submitting the form multiple times
      if (loading) {
        return;
      }
      
      loading = true;
      error = '';
      success = '';

      // Validate form
      if (!validateForm()) {
        loading = false;
        return;
      }

      // Get prepared data
      const { property: preparedProperty, rooms: preparedRooms } = prepareDataForSubmission();

      console.log("Submitting property data:", preparedProperty);
      
      // Create property
      const response = await createProperty(preparedProperty);
      
      if (response && response.id) {
        propertyId = response.id;
        
        console.log("Property created with ID:", propertyId);
        
        // If we have media files, upload them
        if (mediaFiles.length > 0) {
          uploadingMedia = true;
          
          try {
            console.log("Uploading media files:", mediaFiles.length);
            for (const file of mediaFiles) {
              await uploadPropertyMedia(propertyId, file);
            }
            console.log("Media uploads complete");
          } catch (uploadErr) {
            console.error('Error uploading media:', uploadErr);
            error = uploadErr.message || $t('property.mediaUploadFailed');
            // Continue - we've created the property, so we should still navigate
          } finally {
            uploadingMedia = false;
          }
        }
        
        success = $t('property.createSuccess');
        
        // Redirect after a short delay
        setTimeout(() => {
          goto(`/properties/${response.slug}`);
        }, 2000);
      }
    } catch (err) {
      console.error('Error creating property:', err);
      error = err.message || $t('property.createFailed');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>{$t('property.createProperty')} | Real Estate Platform</title>
</svelte:head>

<div class="bg-gray-50 dark:bg-gray-900 py-8">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="md:flex md:items-center md:justify-between mb-8">
      <div class="flex-1 min-w-0">
        <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
          {$t('property.createProperty')}
        </h1>
        <p class="mt-1 text-gray-500 dark:text-gray-400">
          {$t('property.createPropertyDesc')}
        </p>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="mb-8">
      <div class="relative pt-1">
        <div class="flex mb-2 items-center justify-between">
          <div>
            <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-primary-600 bg-primary-200 dark:bg-primary-900 dark:text-primary-200">
              {$t('property.step')} {step} {$t('property.of')} {totalSteps}
            </span>
          </div>
          <div class="text-right">
            <span class="text-xs font-semibold inline-block text-primary-600 dark:text-primary-400">
              {Math.round((step / totalSteps) * 100)}%
            </span>
          </div>
        </div>
        <div class="overflow-hidden h-2 mb-4 text-xs flex rounded bg-primary-200 dark:bg-primary-900/30">
          <div style="width:{(step / totalSteps) * 100}%" class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary-500 dark:bg-primary-500 transition-all duration-500"></div>
        </div>
      </div>
    </div>

    {#if success}
      <div class="mb-8 rounded-md bg-green-50 dark:bg-green-900/30 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-green-800 dark:text-green-200">
              {success}
            </h3>
          </div>
        </div>
      </div>
    {/if}

    {#if error}
      <div class="mb-8 rounded-md bg-red-50 dark:bg-red-900/30 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill