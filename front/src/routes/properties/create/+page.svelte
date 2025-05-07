<!-- src/routes/properties/create/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { t } from '$lib/i18n/i18n';
  import { user } from '$lib/stores/user';
  import { createProperty, uploadPropertyMediaBatch } from '$lib/api/property';
  
  import TagSelector from '$lib/components/TagSelector.svelte';
  import MediaUploader from '$lib/components/MediaUploader.svelte';
  import RoomManager from '$lib/components/RoomManager.svelte';
  import LocationPicker from '$lib/components/LocationPicker.svelte';

  // Property Initial State
  let propertyData = {
    title: '',
    property_type: 'residential',
    building_type: null,
    status: 'available',
    deed_number: '',
    description: '',
    meta_description: '',
    search_keywords: '',
    size_sqm: '',
    floors: null,
    year_built: null,
    address: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'المملكة العربية السعودية',
    latitude: null,
    longitude: null,
    market_value: '',
    minimum_bid: null,
    features: [],
    amenities: [],
    rooms: [],
    is_published: false,
    is_featured: false,
    is_verified: false
  };

  // Form State
  let step = 1;
  let totalSteps = 5;
  let activeTab = 'basic';
  let loading = false;
  let error = '';
  let success = '';
  let mediaFiles = [];
  let uploadingMedia = false;

  // Form Options
  const propertyTypes = [
    { id: 'residential', name: 'سكني', label: 'property.types.residential' },
    { id: 'commercial', name: 'تجاري', label: 'property.types.commercial' },
    { id: 'land', name: 'أرض', label: 'property.types.land' },
    { id: 'industrial', name: 'صناعي', label: 'property.types.industrial' },
    { id: 'mixed_use', name: 'متعدد الاستخدامات', label: 'property.types.mixedUse' }
  ];

  const buildingTypes = [
    { id: 'apartment', name: 'شقة', label: 'property.building.apartment' },
    { id: 'villa', name: 'فيلا', label: 'property.building.villa' },
    { id: 'building', name: 'مبنى', label: 'property.building.building' },
    { id: 'farmhouse', name: 'مزرعة', label: 'property.building.farmhouse' },
    { id: 'shop', name: 'محل تجاري', label: 'property.building.shop' },
    { id: 'office', name: 'مكتب', label: 'property.building.office' }
  ];

  const statusTypes = [
    { id: 'available', name: 'متاح', label: 'property.status.available' },
    { id: 'under_contract', name: 'تحت العقد', label: 'property.status.underContract' },
    { id: 'sold', name: 'مباع', label: 'property.status.sold' },
    { id: 'auction', name: 'في المزاد', label: 'property.status.auction' }
  ];

  const availableFeatures = [
    'parking', 'elevator', 'central_ac', 'garden', 'pool', 'security',
    'gym', 'storage', 'balcony', 'private_entrance', 'maid_room'
  ];

  const availableAmenities = [
    'mosque', 'schools', 'shopping', 'restaurants', 'hospital',
    'pharmacy', 'park', 'gas_station', 'supermarket'
  ];

  // Validation Functions
  function validateRequired(value, fieldName) {
    if (!value || value.toString().trim() === '') {
      return `${fieldName} is required`;
    }
    return null;
  }

  function validateNumber(value, fieldName, min = 0, max = null) {
    const num = parseFloat(value);
    if (isNaN(num)) {
      return `${fieldName} must be a number`;
    }
    if (num < min) {
      return `${fieldName} must be at least ${min}`;
    }
    if (max && num > max) {
      return `${fieldName} must be less than ${max}`;
    }
    return null;
  }

  function validateDeedNumber(value) {
    const pattern = /^[A-Za-z0-9]{5,}$/;
    if (!pattern.test(value)) {
      return 'Invalid deed number format';
    }
    return null;
  }

  function validateForm() {
    const errors = [];

    // Required Fields
    const requiredFields = [
      { field: 'title', name: 'Title' },
      { field: 'property_type', name: 'Property Type' },
      { field: 'deed_number', name: 'Deed Number' },
      { field: 'description', name: 'Description' },
      { field: 'size_sqm', name: 'Size' },
      { field: 'market_value', name: 'Market Value' },
      { field: 'address', name: 'Address' },
      { field: 'city', name: 'City' },
      { field: 'state', name: 'State' }
    ];

    for (const { field, name } of requiredFields) {
      const error = validateRequired(propertyData[field], name);
      if (error) errors.push(error);
    }

    // Number Validations
    if (propertyData.size_sqm) {
      const error = validateNumber(propertyData.size_sqm, 'Size', 1);
      if (error) errors.push(error);
    }

    if (propertyData.market_value) {
      const error = validateNumber(propertyData.market_value, 'Market Value', 1);
      if (error) errors.push(error);
    }

    if (propertyData.minimum_bid) {
      const error = validateNumber(propertyData.minimum_bid, 'Minimum Bid', 1);
      if (error) errors.push(error);
    }

    // Deed Number Format
    if (propertyData.deed_number) {
      const error = validateDeedNumber(propertyData.deed_number);
      if (error) errors.push(error);
    }

    return errors;
  }

  // Event Handlers
  function handleLocationChange(event) {
    const { latitude, longitude, address, city, state, postalCode, country } = event.detail;
    propertyData = {
      ...propertyData,
      latitude,
      longitude,
      address,
      city,
      state,
      postal_code: postalCode,
      country
    };
  }

  function handleFeaturesChange(event) {
    propertyData.features = event.detail;
  }

  function handleAmenitiesChange(event) {
    propertyData.amenities = event.detail;
  }

  function handleRoomsChange(event) {
    propertyData.rooms = event.detail;
  }

  function handleMediaChange(event) {
    mediaFiles = event.detail.files;
  }

  // Navigation Functions
  function nextStep() {
    if (step < totalSteps) {
      step++;
      updateActiveTab();
    }
  }

  function prevStep() {
    if (step > 1) {
      step--;
      updateActiveTab();
    }
  }

  function updateActiveTab() {
    const tabs = ['basic', 'location', 'details', 'rooms', 'media'];
    activeTab = tabs[step - 1];
  }

  // Form Submission
  async function handleSubmit() {
    try {
      if (loading) return;
      
      loading = true;
      error = '';
      success = '';

      // Validate form
      const errors = validateForm();
      if (errors.length > 0) {
        error = errors.join('\n');
        loading = false;
        return;
      }

      // Create property
      const response = await createProperty(propertyData);

      if (response?.data) {
        const propertyId = response.data.id;

        // Upload media if any
        if (mediaFiles.length > 0) {
          uploadingMedia = true;
          try {
            await uploadPropertyMediaBatch(
              propertyId,
              mediaFiles,
              (completed, total) => {
                progress = Math.round((completed / total) * 100);
              }
            );
          } catch (uploadError) {
            console.error('Media upload error:', uploadError);
            error = 'Some media files failed to upload';
          } finally {
            uploadingMedia = false;
          }
        }

        success = 'Property created successfully';
        setTimeout(() => goto(`/properties/${response.data.slug}`), 2000);
      }
    } catch (err) {
      console.error('Error creating property:', err);
      error = err.message || 'Failed to create property';
    } finally {
      loading = false;
    }
  }

  // Authentication Check
  onMount(() => {
    if (!$user) {
      goto('/login?redirect=/properties/create');
    } else if (!['owner', 'appraiser', 'data_entry'].includes($user.role) && !$user.is_staff) {
      goto('/properties');
    }
  });
</script>

<svelte:head>
  <title>{$t('property.createProperty')} | Real Estate Platform</title>
</svelte:head>

<div class="bg-gray-50 dark:bg-gray-900 min-h-screen py-8">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        {$t('property.createProperty')}
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {$t('property.createPropertyDesc')}
      </p>
    </div>

    <!-- Progress Steps -->
    <div class="mb-8">
      <div class="relative">
        <div class="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200 dark:bg-gray-700">
          <div
            class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary-500"
            style="width: {(step / totalSteps) * 100}%"
          ></div>
        </div>
        <div class="flex justify-between">
          {#each Array(totalSteps) as _, i}
            <div class={`text-xs font-medium ${i + 1 <= step ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 dark:text-gray-400'}`}>
              Step {i + 1}
            </div>
          {/each}
        </div>
      </div>
    </div>

    <!-- Error/Success Messages -->
    {#if error}
      <div class="mb-8 bg-red-50 dark:bg-red-900/20 p-4 rounded-md">
        <p class="text-sm text-red-700 dark:text-red-200">{error}</p>
      </div>
    {/if}

    {#if success}
      <div class="mb-8 bg-green-50 dark:bg-green-900/20 p-4 rounded-md">
        <p class="text-sm text-green-700 dark:text-green-200">{success}</p>
      </div>
    {/if}

    <!-- Form Content -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
      <!-- Form Steps -->
      {#if step === 1}
        <div class="p-6 space-y-6">
          <h2 class="text-lg font-medium text-gray-900 dark:text-white">
            {$t('property.basicInfo')}
          </h2>

          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div class="sm:col-span-4">
              <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.title')} *
              </label>
              <input
                type="text"
                id="title"
                bind:value={propertyData.title}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div class="sm:col-span-3">
              <label for="property_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.propertyType')} *
              </label>
              <select
                id="property_type"
                bind:value={propertyData.property_type}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                {#each propertyTypes as type}
                  <option value={type.id}>{type.name}</option>
                {/each}
              </select>
            </div>

            <div class="sm:col-span-3">
              <label for="building_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.buildingType')}
              </label>
              <select
                id="building_type"
                bind:value={propertyData.building_type}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">{$t('property.select')}</option>
                {#each buildingTypes as type}
                  <option value={type.id}>{type.name}</option>
                {/each}
              </select>
            </div>

            <div class="sm:col-span-3">
              <label for="deed_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.deedNumber')} *
              </label>
              <input
                type="text"
                id="deed_number"
                bind:value={propertyData.deed_number}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div class="sm:col-span-6">
              <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.description')} *
              </label>
              <textarea
                id="description"
                bind:value={propertyData.description}
                rows="4"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              ></textarea>
            </div>
          </div>
        </div>

      {:else if step === 2}
        <div class="p-6">
          <LocationPicker
            on:change={handleLocationChange}
            bind:address={propertyData.address}
            bind:city={propertyData.city}
            bind:state={propertyData.state}
            bind:postalCode={propertyData.postal_code}
            bind:country={propertyData.country}
            bind:latitude={propertyData.latitude}
            bind:longitude={propertyData.longitude}
          />
        </div>

      {:else if step === 3}
        <div class="p-6 space-y-6">
          <h2 class="text-lg font-medium text-gray-900 dark:text-white">
            {$t('property.details')}
          </h2>

          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div class="sm:col-span-2">
              <label for="size_sqm" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.size')} (m²) *
              </label>
              <input
                type="number"
                id="size_sqm"
                bind:value={propertyData.size_sqm}
                min="0"
                step="0.01"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div class="sm:col-span-2">
              <label for="floors" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.floors')}
              </label>
              <input
                type="number"
                id="floors"
                bind:value={propertyData.floors}
                min="1"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div class="sm:col-span-2">
              <label for="year_built" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.yearBuilt')}
              </label>
              <input
                type="number"
                id="year_built"
                bind:value={propertyData.year_built}
                min="1900"
                max={new Date().getFullYear()}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div class="sm:col-span-6">
              <TagSelector
                title={$t('property.features')}
                tags={availableFeatures}
                selectedTags={propertyData.features}
                on:change={handleFeaturesChange}
              />
            </div>

            <div class="sm:col-span-6">
              <TagSelector
                title={$t('property.amenities')}
                tags={availableAmenities}
                selectedTags={propertyData.amenities}
                on:change={handleAmenitiesChange}
              />
            </div>
          </div>
        </div>

      {:else if step === 4}
        <div class="p-6">
          <RoomManager
            bind:rooms={propertyData.rooms}
            on:change={handleRoomsChange}
          />
        </div>

      {:else if step === 5}
        <div class="p-6 space-y-6">
          <h2 class="text-lg font-medium text-gray-900 dark:text-white">
            {$t('property.financial')}
          </h2>

          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div class="sm:col-span-3">
              <label for="market_value" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.marketValue')} *
              </label>
              <input
                type="number"
                id="market_value"
                bind:value={propertyData.market_value}
                min="0"
                step="0.01"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div class="sm:col-span-3">
              <label for="minimum_bid" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.minimumBid')}
              </label>
              <input
                type="number"
                id="minimum_bid"
                bind:value={propertyData.minimum_bid}
                min="0"
                step="0.01"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div class="sm:col-span-6">
              <MediaUploader
                on:change={handleMediaChange}
                {uploadingMedia}
              />
            </div>

            <div class="sm:col-span-6">
              <div class="flex items-start">
                <div class="flex items-center h-5">
                  <input
                    id="is_published"
                    type="checkbox"
                    bind:checked={propertyData.is_published}
                    class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
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
                    class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
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

      <!-- Form Actions -->
      <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 rounded-b-lg flex justify-between">
        <button
          type="button"
          on:click={prevStep}
          disabled={step === 1 || loading}
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
        >
          {$t('property.previous')}
        </button>

        {#if step === totalSteps}
          <button
            type="button"
            on:click={handleSubmit}
            disabled={loading || uploadingMedia}
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {#if loading || uploadingMedia}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {uploadingMedia ? $t('property.uploadingMedia') : $t('property.creating')}
            {:else}
              {$t('property.create')}
            {/if}
          </button>
        {:else}
          <button
            type="button"
            on:click={nextStep}
            disabled={loading}
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {$t('property.next')}
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>