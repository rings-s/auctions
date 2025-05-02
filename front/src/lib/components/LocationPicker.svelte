<!-- src/lib/components/LocationPicker.svelte -->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { t } from '$lib/i18n/i18n';
  
  export let latitude = null;
  export let longitude = null;
  export let address = '';
  export let city = '';
  export let state = '';
  export let postalCode = '';
  export let country = 'المملكة العربية السعودية';
  export let zoom = 13;
  export let height = '400px';
  
  const dispatch = createEventDispatcher();
  
  let mapElement;
  let map;
  let marker;
  let searchControl;
  let geocodeResult = null;
  let locationLoading = false;
  let locationError = '';
  let locationSuccess = '';
  let locationMode = 'manual'; // Changed default to 'manual' or 'map'
  
  onMount(() => {
    loadMapScript();
  });
  
  function loadMapScript() {
    if (!document.getElementById('leaflet-css')) {
      const cssLink = document.createElement('link');
      cssLink.id = 'leaflet-css';
      cssLink.rel = 'stylesheet';
      cssLink.href = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css';
      document.head.appendChild(cssLink);
    }
    
    if (!window.L) {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js';
      script.onload = initializeMap;
      document.head.appendChild(script);
    } else {
      initializeMap();
    }
  }
  
  function initializeMap() {
    if (!window.L || !mapElement) return;
    
    try {
      const defaultLat = latitude || 24.7136;
      const defaultLng = longitude || 46.6753;
      
      map = window.L.map(mapElement, {
        center: [defaultLat, defaultLng],
        zoom,
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
        updateCoordinates(position.lat, position.lng);
        reverseGeocode(position.lat, position.lng);
      });
      
      map.on('click', (e) => {
        marker.setLatLng(e.latlng);
        updateCoordinates(e.latlng.lat, e.latlng.lng);
        reverseGeocode(e.latlng.lat, e.latlng.lng);
      });
      
      addSearchControl();
      
      setTimeout(() => {
        map.invalidateSize();
      }, 100);
    } catch (error) {
      console.error('Error initializing map:', error);
    }
  }
  
  // Keep all your existing functions...
</script>

<div class="space-y-6">
<div>
  <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('location.title')}</h3>
  <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('location.locationDesc')}</p>
</div>

<div class="flex space-x-4">
  <button
    type="button"
    class={`px-4 py-2 text-sm font-medium rounded-md ${locationMode === 'map' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-white text-gray-700 dark:bg-gray-800 dark:text-gray-300 border border-gray-300 dark:border-gray-600'}`}
    on:click={() => locationMode = 'map'}
  >
    <svg class="inline-block w-4 h-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
    </svg>
    {$t('location.useMap')}
  </button>
  <button
    type="button"
    class={`px-4 py-2 text-sm font-medium rounded-md ${locationMode === 'manual' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-white text-gray-700 dark:bg-gray-800 dark:text-gray-300 border border-gray-300 dark:border-gray-600'}`}
    on:click={() => locationMode = 'manual'}
  >
    <svg class="inline-block w-4 h-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
    </svg>
    {$t('location.enterManually')}
  </button>
</div>

<!-- Form Fields (Always Visible) -->
<div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
  <!-- Address -->
  <div class="sm:col-span-6">
    <label for="address" class="block text-sm font-medium text-gray-700 dark:text-gray-300 required">
      {$t('location.address')} *
    </label>
    <div class="mt-1">
      <input
        type="text"
        id="address"
        bind:value={address}
        required
        maxlength="255"
        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
      />
    </div>
  </div>

  <!-- City -->
  <div class="sm:col-span-3">
    <label for="city" class="block text-sm font-medium text-gray-700 dark:text-gray-300 required">
      {$t('location.city')} *
    </label>
    <div class="mt-1">
      <input
        type="text"
        id="city"
        bind:value={city}
        required
        maxlength="100"
        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
      />
    </div>
  </div>

  <!-- State -->
  <div class="sm:col-span-3">
    <label for="state" class="block text-sm font-medium text-gray-700 dark:text-gray-300 required">
      {$t('location.state')} *
    </label>
    <div class="mt-1">
      <input
        type="text"
        id="state"
        bind:value={state}
        required
        maxlength="100"
        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
      />
    </div>
  </div>

  <!-- Postal Code -->
  <div class="sm:col-span-3">
    <label for="postal_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      {$t('location.postalCode')}
    </label>
    <div class="mt-1">
      <input
        type="text"
        id="postal_code"
        bind:value={postalCode}
        maxlength="20"
        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
      />
    </div>
  </div>

  <!-- Country (Read-only) -->
  <div class="sm:col-span-3">
    <label for="country" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      {$t('location.country')}
    </label>
    <div class="mt-1">
      <input
        type="text"
        id="country"
        bind:value={country}
        readonly
        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white bg-gray-100 dark:bg-gray-700"
      />
    </div>
  </div>
</div>

{#if locationMode === 'map'}
  <!-- Map View -->
  <div class="space-y-4">
    <!-- Location Detection -->
    <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-md">
      <div class="flex items-center justify-between">
        <div>
          <h4 class="text-sm font-medium text-gray-900 dark:text-white">{$t('location.detect')}</h4>
          <p class="text-xs text-gray-500 dark:text-gray-400">{$t('location.detectHelp')}</p>
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
          <svg class="h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {$t('location.detectButton')}
        </button>
      </div>

      {#if locationError}
        <div class="mt-2 text-sm text-red-600 dark:text-red-400">{locationError}</div>
      {/if}

      {#if locationSuccess}
        <div class="mt-2 text-sm text-green-600 dark:text-green-400">{locationSuccess}</div>
      {/if}
    </div>

    <!-- Map -->
    <div class="bg-gray-100 dark:bg-gray-800 rounded-md overflow-hidden" style="height: {height};">
      <div bind:this={mapElement} class="w-full h-full"></div>
    </div>

    <!-- Coordinates -->
    <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
      <div>
        <label for="latitude" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('location.latitude')}
        </label>
        <div class="mt-1">
          <input
            type="number"
            id="latitude"
            bind:value={latitude}
            step="0.000001"
            min="-90"
            max="90"
            class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>

      <div>
        <label for="longitude" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('location.longitude')}
        </label>
        <div class="mt-1">
          <input
            type="number"
            id="longitude"
            bind:value={longitude}
            step="0.000001"
            min="-180"
            max="180"
            class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>
    </div>
  </div>
{/if}
</div>

<style>
.required::after {
  content: " *";
  color: rgb(239, 68, 68);
}
</style>