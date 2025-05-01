<!-- src/lib/components/PropertyForm.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n/i18n';
    import TagList from '$lib/components/TagList.svelte';
  
    export let property = {
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
  
    export let rooms = [];
    export let activeTab = 'basic';
    export let loading = false;
    export let error = '';
    export let step = 1;
  
    // For features and amenities
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
  
    // For location detection
    let locationLoading = false;
    let locationError = '';
    let locationSuccess = '';
    let map;
    let marker;
    let mapElement;
  
    // For room management
    let newRoom = {
      name: '',
      room_type: 'bedroom',
      floor: 1,
      area_sqm: '',
      description: '',
      features: []
    };
  
    const roomTypes = [
      { value: 'bedroom', label: 'Bedroom' },
      { value: 'bathroom', label: 'Bathroom' },
      { value: 'kitchen', label: 'Kitchen' },
      { value: 'living', label: 'Living Room' },
      { value: 'dining', label: 'Dining Room' },
      { value: 'office', label: 'Office' },
      { value: 'storage', label: 'Storage' },
      { value: 'other', label: 'Other' }
    ];
  
    onMount(() => {
      initializeMap();
    });
  
    function initializeMap() {
      if (!window.L) {
        // Load Leaflet from CDN if not already loaded
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css';
        document.head.appendChild(cssLink);
        
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js';
        script.onload = createMap;
        document.head.appendChild(script);
      } else {
        createMap();
      }
    }
  
    function createMap() {
      if (!window.L || !mapElement) return;
      
      // Default to Riyadh, Saudi Arabia if no coordinates provided
      const defaultLat = property.latitude || 24.7136;
      const defaultLng = property.longitude || 46.6753;
      
      map = window.L.map(mapElement, {
        center: [defaultLat, defaultLng],
        zoom: 13,
        scrollWheelZoom: true
      });
      
      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      
      marker = window.L.marker([defaultLat, defaultLng], {
        draggable: true
      }).addTo(map);
      
      marker.on('dragend', (event) => {
        const position = event.target.getLatLng();
        property.latitude = position.lat;
        property.longitude = position.lng;
      });
      
      // Refresh map size after render
      setTimeout(() => {
        map.invalidateSize();
      }, 100);
    }
  
    async function detectLocation() {
      locationLoading = true;
      locationError = '';
      locationSuccess = '';
      
      try {
        if (!navigator.geolocation) {
          throw new Error($t('property.geolocationNotSupported'));
        }
        
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
          });
        });
        
        const { latitude, longitude } = position.coords;
        property.latitude = latitude;
        property.longitude = longitude;
        
        if (map && marker) {
          map.setView([latitude, longitude], 15);
          marker.setLatLng([latitude, longitude]);
        }
        
        locationSuccess = $t('property.locationDetected');
        
        // Try to fetch address details based on coordinates
        try {
          const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`);
          const data = await response.json();
          
          if (data.address) {
            property.address = data.address.road || data.address.suburb || '';
            property.city = data.address.city || data.address.town || data.address.village || '';
            property.state = data.address.state || '';
            property.postal_code = data.address.postcode || '';
            property.country = data.address.country || property.country;
          }
        } catch (err) {
          console.warn('Could not fetch address details:', err);
        }
        
      } catch (err) {
        console.error('Geolocation error:', err);
        locationError = err.message || $t('property.locationDetectionFailed');
      } finally {
        locationLoading = false;
      }
    }
  
    function addRoom() {
      if (!newRoom.name) return;
      
      rooms = [...rooms, { ...newRoom, id: Date.now() }];
      
      // Reset form
      newRoom = {
        name: '',
        room_type: 'bedroom',
        floor: 1,
        area_sqm: '',
        description: '',
        features: []
      };
    }
  
    function removeRoom(index) {
      rooms = rooms.filter((_, i) => i !== index);
    }
  
    function handleFeaturesChange(event) {
      property.features = event.detail;
    }
  
    function handleAmenitiesChange(event) {
      property.amenities = event.detail;
    }
  
    function handleRoomFeaturesChange(event) {
      newRoom.features = event.detail;
    }
  
    function setTab(tab) {
      activeTab = tab;
    }
  
    function nextStep() {
      if (step < 5) step++;
    }
  
    function prevStep() {
      if (step > 1) step--;
    }
  
    // Convert arrays to string for API submission
    export function prepareDataForSubmission() {
      const preparedData = { ...property };
      
      // Convert feature and amenity arrays to strings if needed
      if (Array.isArray(preparedData.features)) {
        preparedData.features = JSON.stringify(preparedData.features);
      }
      
      if (Array.isArray(preparedData.amenities)) {
        preparedData.amenities = JSON.stringify(preparedData.amenities);
      }
      
      // Prepare rooms data
      const preparedRooms = rooms.map(room => {
        const preparedRoom = { ...room };
        if (Array.isArray(preparedRoom.features)) {
          preparedRoom.features = JSON.stringify(preparedRoom.features);
        }
        return preparedRoom;
      });
      
      return { property: preparedData, rooms: preparedRooms };
    }
  </script>
  
  <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8 overflow-x-auto" aria-label="Tabs">
        <button
          on:click={() => setTab('basic')}
          class={`${
            activeTab === 'basic'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('property.basicInfo')}
        </button>
        <button
          on:click={() => setTab('location')}
          class={`${
            activeTab === 'location'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('property.location')}
        </button>
        <button
          on:click={() => setTab('details')}
          class={`${
            activeTab === 'details'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('property.details')}
        </button>
        <button
          on:click={() => setTab('rooms')}
          class={`${
            activeTab === 'rooms'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('property.rooms')}
        </button>
        <button
          on:click={() => setTab('financial')}
          class={`${
            activeTab === 'financial'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('property.financial')}
        </button>
      </nav>
    </div>
  
    <div class="px-4 py-5 sm:p-6">
      {#if error}
        <div class="mb-4 rounded-md bg-red-50 dark:bg-red-900/30 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                {error}
              </h3>
            </div>
          </div>
        </div>
      {/if}
  
      <!-- Basic Information -->
      {#if activeTab === 'basic'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('property.basicInfo')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('property.basicInfoDesc')}</p>
          </div>
  
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <!-- Property Title -->
            <div class="sm:col-span-4">
              <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.title')}
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="title"
                  bind:value={property.title}
                  required
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <!-- Property Type -->
            <div class="sm:col-span-3">
              <label for="property_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.propertyType')}
              </label>
              <div class="mt-1">
                <select
                  id="property_type"
                  bind:value={property.property_type}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                >
                  <option value="residential">{$t('nav.propertyTypes.residential')}</option>
                  <option value="commercial">{$t('nav.propertyTypes.commercial')}</option>
                  <option value="land">{$t('nav.propertyTypes.land')}</option>
                  <option value="industrial">{$t('nav.propertyTypes.industrial')}</option>
                  <option value="mixed_use">{$t('nav.propertyTypes.mixedUse')}</option>
                </select>
              </div>
            </div>
  
            <!-- Building Type -->
            <div class="sm:col-span-3">
              <label for="building_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.buildingType')}
              </label>
              <div class="mt-1">
                <select
                  id="building_type"
                  bind:value={property.building_type}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                >
                  <option value="">--{$t('property.select')}--</option>
                  <option value="apartment">{$t('property.buildingTypes.apartment')}</option>
                  <option value="villa">{$t('property.buildingTypes.villa')}</option>
                  <option value="building">{$t('property.buildingTypes.building')}</option>
                  <option value="farmhouse">{$t('property.buildingTypes.farmhouse')}</option>
                  <option value="shop">{$t('property.buildingTypes.shop')}</option>
                  <option value="office">{$t('property.buildingTypes.office')}</option>
                </select>
              </div>
            </div>
  
            <!-- Status -->
            <div class="sm:col-span-3">
              <label for="status" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.status')}
              </label>
              <div class="mt-1">
                <select
                  id="status"
                  bind:value={property.status}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                >
                  <option value="available">{$t('property.statusTypes.available')}</option>
                  <option value="under_contract">{$t('property.statusTypes.underContract')}</option>
                  <option value="sold">{$t('property.statusTypes.sold')}</option>
                  <option value="auction">{$t('property.statusTypes.auction')}</option>
                </select>
              </div>
            </div>
  
            <!-- Deed Number -->
            <div class="sm:col-span-3">
              <label for="deed_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.deedNumber')}
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="deed_number"
                  bind:value={property.deed_number}
                  required
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{$t('property.deedNumberHelp')}</p>
              </div>
            </div>
  
            <!-- Description -->
            <div class="sm:col-span-6">
              <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.description')}
              </label>
              <div class="mt-1">
                <textarea
                  id="description"
                  bind:value={property.description}
                  rows="5"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                ></textarea>
              </div>
            </div>
  
            <!-- Publishing Options -->
            <div class="sm:col-span-6">
              <fieldset>
                <legend class="text-sm font-medium text-gray-700 dark:text-gray-300">{$t('property.publishingOptions')}</legend>
                <div class="mt-2 space-y-4">
                  <div class="relative flex items-start">
                    <div class="flex items-center h-5">
                      <input
                        id="is_published"
                        type="checkbox"
                        bind:checked={property.is_published}
                        class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 dark:border-gray-700 rounded dark:bg-gray-800"
                      />
                    </div>
                    <div class="ml-3 text-sm">
                      <label for="is_published" class="font-medium text-gray-700 dark:text-gray-300">{$t('property.published')}</label>
                      <p class="text-gray-500 dark:text-gray-400">{$t('property.publishedHelp')}</p>
                    </div>
                  </div>
                  <div class="relative flex items-start">
                    <div class="flex items-center h-5">
                      <input
                        id="is_featured"
                        type="checkbox"
                        bind:checked={property.is_featured}
                        class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 dark:border-gray-700 rounded dark:bg-gray-800"
                      />
                    </div>
                    <div class="ml-3 text-sm">
                      <label for="is_featured" class="font-medium text-gray-700 dark:text-gray-300">{$t('property.featured')}</label>
                      <p class="text-gray-500 dark:text-gray-400">{$t('property.featuredHelp')}</p>
                    </div>
                  </div>
                </div>
              </fieldset>
            </div>
          </div>
        </div>
      {/if}
  
      <!-- Location -->
      {#if activeTab === 'location'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('property.location')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('property.locationDesc')}</p>
          </div>
  
          <!-- Location Detection -->
          <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-md">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-medium text-gray-900 dark:text-white">{$t('property.detectLocation')}</h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">{$t('property.detectLocationHelp')}</p>
              </div>
              <button
                type="button"
                on:click={detectLocation}
                disabled={locationLoading}
                class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
              >
                {#if locationLoading}
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                {/if}
                {$t('property.detect')}
              </button>
            </div>
  
            {#if locationError}
              <div class="mt-2 text-sm text-red-600 dark:text-red-400">{locationError}</div>
            {/if}
  
            {#if locationSuccess}
              <div class="mt-2 text-sm text-green-600 dark:text-green-400">{locationSuccess}</div>
            {/if}
          </div>
  
          <!-- Map for location selection -->
          <div class="h-64 bg-gray-100 dark:bg-gray-800 rounded-md overflow-hidden">
            <div bind:this={mapElement} class="w-full h-full"></div>
          </div>
  
          <!-- Address Form -->
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <!-- Address -->
            <div class="sm:col-span-6">
              <label for="address" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.address')}
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="address"
                  bind:value={property.address}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <!-- City and State -->
            <div class="sm:col-span-3">
              <label for="city" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.city')}
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="city"
                  bind:value={property.city}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <div class="sm:col-span-3">
              <label for="state" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.state')}
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="state"
                  bind:value={property.state}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <!-- Postal Code and Country -->
            <div class="sm:col-span-3">
              <label for="postal_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.postalCode')}
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="postal_code"
                  bind:value={property.postal_code}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <div class="sm:col-span-3">
              <label for="country" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.country')}
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="country"
                  bind:value={property.country}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <!-- Coordinates -->
            <div class="sm:col-span-3">
              <label for="latitude" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.latitude')}
              </label>
              <div class="mt-1">
                <input
                  type="number"
                  id="latitude"
                  bind:value={property.latitude}
                  step="any"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <div class="sm:col-span-3">
              <label for="longitude" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.longitude')}
              </label>
              <div class="mt-1">
                <input
                  type="number"
                  id="longitude"
                  bind:value={property.longitude}
                  step="any"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
          </div>
        </div>
      {/if}
  
      <!-- Details -->
      {#if activeTab === 'details'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('property.details')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('property.detailsDesc')}</p>
          </div>
  
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <!-- Size and Floors -->
            <div class="sm:col-span-3">
              <label for="size_sqm" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.size')} ({$t('property.sqm')})
              </label>
              <div class="mt-1">
                <input
                  type="number"
                  id="size_sqm"
                  bind:value={property.size_sqm}
                  min="0"
                  step="0.01"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <div class="sm:col-span-3">
              <label for="floors" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.floors')}
              </label>
              <div class="mt-1">
                <input
                  type="number"
                  id="floors"
                  bind:value={property.floors}
                  min="0"
                  step="1"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <!-- Year Built -->
            <div class="sm:col-span-3">
              <label for="year_built" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.yearBuilt')}
              </label>
              <div class="mt-1">
                <input
                  type="number"
                  id="year_built"
                  bind:value={property.year_built}
                  min="1900"
                  max={new Date().getFullYear()}
                  step="1"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <!-- Features -->
            <div class="sm:col-span-6">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {$t('property.features')}
              </label>
              <TagList 
                tags={availableFeatures} 
                selectedTags={property.features} 
                on:change={handleFeaturesChange} 
              />
            </div>
  
            <!-- Amenities -->
            <div class="sm:col-span-6">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {$t('property.amenities')}
              </label>
              <TagList 
                tags={availableAmenities} 
                selectedTags={property.amenities} 
                on:change={handleAmenitiesChange} 
              />
            </div>
          </div>
        </div>
      {/if}
  
      <!-- Rooms -->
      {#if activeTab === 'rooms'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('property.rooms')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('property.roomsDesc')}</p>
          </div>
  
          <!-- Add Room Form -->
          <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-md">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">{$t('property.addRoom')}</h4>
            
            <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <!-- Room Name and Type -->
              <div class="sm:col-span-3">
                <label for="room_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.roomName')}
                </label>
                <div class="mt-1">
                  <input
                    type="text"
                    id="room_name"
                    bind:value={newRoom.name}
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>
  
              <div class="sm:col-span-3">
                <label for="room_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.roomType')}
                </label>
                <div class="mt-1">
                  <select
                    id="room_type"
                    bind:value={newRoom.room_type}
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  >
                    {#each roomTypes as type}
                      <option value={type.value}>{type.label}</option>
                    {/each}
                  </select>
                </div>
              </div>
  
              <!-- Floor and Area -->
              <div class="sm:col-span-3">
                <label for="room_floor" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.floor')}
                </label>
                <div class="mt-1">
                  <input
                    type="number"
                    id="room_floor"
                    bind:value={newRoom.floor}
                    min="0"
                    step="1"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>
  
              <div class="sm:col-span-3">
                <label for="room_area" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.area')} ({$t('property.sqm')})
                </label>
                <div class="mt-1">
                  <input
                    type="number"
                    id="room_area"
                    bind:value={newRoom.area_sqm}
                    min="0"
                    step="0.01"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>
  
              <!-- Description -->
              <div class="sm:col-span-6">
                <label for="room_description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.description')}
                </label>
                <div class="mt-1">
                  <textarea
                    id="room_description"
                    bind:value={newRoom.description}
                    rows="3"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  ></textarea>
                </div>
              </div>
  
              <!-- Room Features -->
              <div class="sm:col-span-6">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {$t('property.roomFeatures')}
                </label>
                <TagList 
                  tags={availableFeatures} 
                  selectedTags={newRoom.features} 
                  on:change={handleRoomFeaturesChange} 
                />
              </div>
  
              <!-- Add Button -->
              <div class="sm:col-span-6 flex justify-end">
                <button
                  type="button"
                  on:click={addRoom}
                  class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  {$t('property.addRoom')}
                </button>
              </div>
            </div>
          </div>
  
          <!-- Room List -->
          {#if rooms.length > 0}
            <div>
              <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">{$t('property.roomList')}</h4>
              
              <div class="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-md">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead class="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        {$t('property.roomName')}
                      </th>
                      <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        {$t('property.roomType')}
                      </th>
                      <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        {$t('property.floor')}
                      </th>
                      <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        {$t('property.area')}
                      </th>
                      <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        {$t('property.actions')}
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {#each rooms as room, index}
                      <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                          {room.name}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {roomTypes.find(type => type.value === room.room_type)?.label || room.room_type}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {room.floor}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {room.area_sqm} {$t('property.sqm')}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            type="button"
                            on:click={() => removeRoom(index)}
                            class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                          >
                            {$t('property.remove')}
                          </button>
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            </div>
          {:else}
            <div class="text-center py-8 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">{$t('property.noRooms')}</h3>
              <p class="text-gray-500 dark:text-gray-400">{$t('property.addRoomHelp')}</p>
            </div>
          {/if}
        </div>
      {/if}
  
      <!-- Financial Information -->
      {#if activeTab === 'financial'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('property.financial')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('property.financialDesc')}</p>
          </div>
  
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <!-- Market Value -->
            <div class="sm:col-span-3">
              <label for="market_value" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.marketValue')} ($)
              </label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400 sm:text-sm">$</span>
                </div>
                <input
                  type="number"
                  id="market_value"
                  bind:value={property.market_value}
                  min="0"
                  step="0.01"
                  class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  placeholder="0.00"
                />
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400 sm:text-sm">USD</span>
                </div>
              </div>
            </div>
  
            <!-- Minimum Bid -->
            <div class="sm:col-span-3">
              <label for="minimum_bid" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('property.minimumBid')} ($)
              </label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400 sm:text-sm">$</span>
                </div>
                <input
                  type="number"
                  id="minimum_bid"
                  bind:value={property.minimum_bid}
                  min="0"
                  step="0.01"
                  class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  placeholder="0.00"
                />
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400 sm:text-sm">USD</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>