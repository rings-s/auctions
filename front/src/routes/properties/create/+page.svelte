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
  let totalSteps = 5;

  // Property type options
  const propertyTypes = [
    { value: 'residential', label: 'property.propertyTypes.residential' },
    { value: 'commercial', label: 'property.propertyTypes.commercial' },
    { value: 'land', label: 'property.propertyTypes.land' },
    { value: 'industrial', label: 'property.propertyTypes.industrial' },
    { value: 'mixed_use', label: 'property.propertyTypes.mixedUse' }
  ];

  // Building type options
  const buildingTypes = [
    { value: 'apartment', label: 'property.buildingTypes.apartment' },
    { value: 'villa', label: 'property.buildingTypes.villa' },
    { value: 'building', label: 'property.buildingTypes.building' },
    { value: 'farmhouse', label: 'property.buildingTypes.farmhouse' },
    { value: 'shop', label: 'property.buildingTypes.shop' },
    { value: 'office', label: 'property.buildingTypes.office' }
  ];

  // Status options
  const statusTypes = [
    { value: 'available', label: 'property.statusTypes.available' },
    { value: 'under_contract', label: 'property.statusTypes.underContract' },
    { value: 'sold', label: 'property.statusTypes.sold' },
    { value: 'auction', label: 'property.statusTypes.auction' }
  ];
  
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
    if (!$user) {
      goto('/login?redirect=/properties/create');
    } else if ($user.role !== 'owner' && $user.role !== 'appraiser' && $user.role !== 'data_entry' && !$user.is_staff) {
      // User doesn't have the right role, show a message and redirect
      alert('You do not have permission to create properties. Required role: owner, appraiser, or data entry specialist.');
      goto('/properties');
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
      case 1: activeTab = 'basic'; break;
      case 2: activeTab = 'location'; break;
      case 3: activeTab = 'details'; break;
      case 4: activeTab = 'rooms'; break;
      case 5: activeTab = 'financial'; break;
    }
  }

  function setTab(tab) {
    activeTab = tab;
    switch(tab) {
      case 'basic': step = 1; break;
      case 'location': step = 2; break;
      case 'details': step = 3; break;
      case 'rooms': step = 4; break;
      case 'financial': step = 5; break;
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

  // In the PropertyForm component
  function validateForm() {
    error = '';
    const requiredFields = [
      { field: 'title', message: $t('property.titleRequired') },
      { field: 'deed_number', message: $t('property.deedNumberRequired') },
      { field: 'market_value', message: $t('property.marketValueRequired') }
    ];

    for (const { field, message } of requiredFields) {
      if (!propertyData[field]) {
        error = message;
        return false;
      }
    }

    // Validate numeric fields
    if (propertyData.market_value && isNaN(parseFloat(propertyData.market_value))) {
      error = $t('property.invalidMarketValue');
      return false;
    }

    return true;
  }
  
  function prepareDataForSubmission() {
    // Create a copy of the propertyData object
    const preparedProperty = { ...propertyData };
    
    // Handle numeric fields properly
    ['size_sqm', 'market_value', 'minimum_bid'].forEach(field => {
      if (preparedProperty[field]) {
        preparedProperty[field] = parseFloat(preparedProperty[field]);
      }
    });
    
    ['floors', 'year_built'].forEach(field => {
      if (preparedProperty[field]) {
        preparedProperty[field] = parseInt(preparedProperty[field], 10);
      }
    });
    
    // Make sure booleans are properly formatted
    preparedProperty.is_published = Boolean(preparedProperty.is_published);
    preparedProperty.is_featured = Boolean(preparedProperty.is_featured);
    
    // Log the prepared data for debugging
    console.log('Prepared property data:', preparedProperty);
    
    return { property: preparedProperty, rooms: rooms };
  }

  async function handleSubmit() {
    try {
      if (loading) return;
      
      loading = true;
      error = '';
      success = '';
      
      // Validate form
      if (!validateForm()) {
        loading = false;
        return;
      }
      
      // Prepare data
      const { property: preparedProperty } = prepareDataForSubmission();
      
      // Create property
      console.log('Submitting property data:', preparedProperty);
      const response = await createProperty(preparedProperty);
      console.log('API response:', response);
      
      // Check if the response contains data
      if (response && response.data) {
        propertyId = response.data.id;
        
        // Upload media files if any
        if (mediaFiles.length > 0) {
          uploadingMedia = true;
          try {
            for (const file of mediaFiles) {
              await uploadPropertyMedia(propertyId, file);
            }
          } catch (uploadErr) {
            console.error('Error uploading media:', uploadErr);
            // Don't fail the whole operation if media upload fails
            error = uploadErr.message || $t('property.mediaUploadFailed');
          } finally {
            uploadingMedia = false;
          }
        }
        
        // Set success message and redirect
        success = $t('property.createSuccess');
        setTimeout(() => goto(`/properties/${response.data.slug}`), 2000);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      console.error('Error creating property:', err);
      
      // Handle specific API errors
      if (err.response?.data?.error) {
        error = err.response.data.error.message || err.response.data.error;
      } else {
        error = err.message || $t('property.createFailed');
      }
      
      // Scroll to error message
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }, 100);
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
    <!-- Header -->
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
              Step {step} of {totalSteps}
            </span>
          </div>
          <div class="text-right">
            <span class="text-xs font-semibold inline-block text-primary-600 dark:text-primary-400">
              {Math.round((step / totalSteps) * 100)}%
            </span>
          </div>
        </div>
        <div class="overflow-hidden h-2 mb-4 text-xs flex rounded bg-primary-200 dark:bg-primary-900/30">
          <div 
            style="width:{(step / totalSteps) * 100}%" 
            class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary-500 dark:bg-primary-500 transition-all duration-500"
          ></div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    {#if success}
      <div class="mb-8 rounded-md bg-green-50 dark:bg-green-900/30 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-green-800 dark:text-green-200">{success}</p>
          </div>
        </div>
      </div>
    {/if}

    {#if error}
      <div class="mb-8 rounded-md bg-red-50 dark:bg-red-900/30 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-red-800 dark:text-red-200">{error}</p>
          </div>
        </div>
      </div>
    {/if}

    <!-- Form -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
      <!-- Tabs -->
      <div class="border-b border-gray-200 dark:border-gray-700">
        <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
          {#each ['basic', 'location', 'details', 'rooms', 'financial'] as tab}
            <button
              class={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab 
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'}`}
              on:click={() => setTab(tab)}
            >
              {$t(`property.${tab}`)}
            </button>
          {/each}
        </nav>
      </div>

      <!-- Tab content -->
      <div class="p-6">
        {#if activeTab === 'basic'}
          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
                {$t('property.basicInfo')}
              </h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {$t('property.basicInfoDesc')}
              </p>
            </div>

            <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div class="sm:col-span-4">
                <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.title')} *
                </label>
                <div class="mt-1">
                  <input
                    type="text"
                    id="title"
                    bind:value={propertyData.title}
                    required
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>

              <div class="sm:col-span-4">
                <label for="deed_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.deedNumber')} *
                </label>
                <div class="mt-1">
                  <input
                    type="text"
                    id="deed_number"
                    bind:value={propertyData.deed_number}
                    required
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
                <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  {$t('property.deedNumberHelp')}
                </p>
              </div>

              <div class="sm:col-span-3">
                <label for="property_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.propertyType')}
                </label>
                <div class="mt-1">
                  <select
                    id="property_type"
                    bind:value={propertyData.property_type}
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  >
                    {#each propertyTypes as type}
                      <option value={type.value}>{$t(type.label)}</option>
                    {/each}
                  </select>
                </div>
              </div>

              <div class="sm:col-span-3">
                <label for="building_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.buildingType')}
                </label>
                <div class="mt-1">
                  <select
                    id="building_type"
                    bind:value={propertyData.building_type}
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  >
                    <option value="">{$t('property.select')}</option>
                    {#each buildingTypes as type}
                      <option value={type.value}>{$t(type.label)}</option>
                    {/each}
                  </select>
                </div>
              </div>

              <div class="sm:col-span-6">
                <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.description')}
                </label>
                <div class="mt-1">
                  <textarea
                    id="description"
                    bind:value={propertyData.description}
                    rows="3"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>

        {:else if activeTab === 'location'}
          <LocationPicker
            bind:latitude={propertyData.latitude}
            bind:longitude={propertyData.longitude}
            bind:address={propertyData.address}
            bind:city={propertyData.city}
            bind:state={propertyData.state}
            bind:postalCode={propertyData.postal_code}
            bind:country={propertyData.country}
            on:locationChange={handleLocationChange}
            on:addressChange={handleAddressChange}
          />

        {:else if activeTab === 'details'}
          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
                {$t('property.details')}
              </h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {$t('property.detailsDesc')}
              </p>
            </div>

            <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div class="sm:col-span-2">
                <label for="size_sqm" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.size')} ({$t('property.sqm')})
                </label>
                <div class="mt-1">
                  <input
                    type="number"
                    id="size_sqm"
                    bind:value={propertyData.size_sqm}
                    min="0"
                    step="0.01"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>

              <div class="sm:col-span-2">
                <label for="floors" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.floors')}
                </label>
                <div class="mt-1">
                  <input
                    type="number"
                    id="floors"
                    bind:value={propertyData.floors}
                    min="1"
                    step="1"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>

              <div class="sm:col-span-2">
                <label for="year_built" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.yearBuilt')}
                </label>
                <div class="mt-1">
                  <input
                    type="number"
                    id="year_built"
                    bind:value={propertyData.year_built}
                    min="1900"
                    max="2025"
                    step="1"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>

              <div class="sm:col-span-6">
                <TagSelector
                  tags={availableFeatures}
                  selectedTags={propertyData.features}
                  title={$t('property.features')}
                  on:change={handleFeaturesChange}
                />
              </div>

              <div class="sm:col-span-6">
                <TagSelector
                  tags={availableAmenities}
                  selectedTags={propertyData.amenities}
                  title={$t('property.amenities')}
                  on:change={handleAmenitiesChange}
                />
              </div>

              <div class="sm:col-span-6">
                <MediaUploader
                  bind:mediaFiles
                  on:change={handleMediaChange}
                />
              </div>
            </div>
          </div>

        {:else if activeTab === 'rooms'}
          <RoomManager
            bind:rooms
            {availableFeatures}
            on:change={handleRoomsChange}
          />

        {:else if activeTab === 'financial'}
          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
                {$t('property.financial')}
              </h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {$t('property.financialDesc')}
              </p>
            </div>

            <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div class="sm:col-span-3">
                <label for="market_value" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.marketValue')} *
                </label>
                <div class="mt-1">
                  <input
                    type="number"
                    id="market_value"
                    bind:value={propertyData.market_value}
                    required
                    min="0"
                    step="0.01"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>

              <div class="sm:col-span-3">
                <label for="minimum_bid" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.minimumBid')}
                </label>
                <div class="mt-1">
                  <input
                    type="number"
                    id="minimum_bid"
                    bind:value={propertyData.minimum_bid}
                    min="0"
                    step="0.01"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>

              <div class="sm:col-span-6">
                <div class="flex items-start">
                  <div class="flex items-center h-5">
                    <input
                      id="is_published"
                      type="checkbox"
                      bind:checked={propertyData.is_published}
                      class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded dark:border-gray-700 dark:bg-gray-800"
                    />
                  </div>
                  <div class="ml-3 text-sm">
                    <label for="is_published" class="font-medium text-gray-700 dark:text-gray-300">
                      {$t('property.published')}
                    </label>
                    <p class="text-gray-500 dark:text-gray-400">{$t('property.publishedHelp')}</p>
                  </div>
                </div>
              </div>

              <div class="sm:col-span-6">
                <div class="flex items-start">
                  <div class="flex items-center h-5">
                    <input
                      id="is_featured"
                      type="checkbox"
                      bind:checked={propertyData.is_featured}
                      class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded dark:border-gray-700 dark:bg-gray-800"
                    />
                  </div>
                  <div class="ml-3 text-sm">
                    <label for="is_featured" class="font-medium text-gray-700 dark:text-gray-300">
                      {$t('property.featured')}
                    </label>
                    <p class="text-gray-500 dark:text-gray-400">{$t('property.featuredHelp')}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        {/if}
      </div>

      <!-- Form actions -->
      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-between">
        <!-- Previous Button -->
        <button
          type="button"
          on:click={prevStep}
          disabled={step === 1 || loading}
          class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 transition-all duration-200"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {$t('property.previous')}
        </button>
      
        <!-- Next/Submit Button -->
        {#if step === totalSteps}
          <button
            type="button"
            on:click={handleSubmit}
            disabled={loading || uploadingMedia}
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 transition-all duration-200"
          >
            {#if loading || uploadingMedia}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {uploadingMedia ? $t('property.uploadingMedia') : $t('property.creating')}
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
              </svg>
              {$t('property.create')}
            {/if}
          </button>
        {:else}
          <button
            type="button"
            on:click={nextStep}
            disabled={loading}
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 transition-all duration-200"
          >
            {$t('property.next')}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>