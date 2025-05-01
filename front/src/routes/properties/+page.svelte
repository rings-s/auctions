<!-- src/routes/properties/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n/i18n';
    import { fetchProperties } from '$lib/api/property';
    import { properties as propertiesStore } from '$lib/stores/properties';
    import PropertyCard from '$lib/components/PropertyCard.svelte';
    import PropertySearch from '$lib/components/PropertySearch.svelte';
  
    let properties = [];
    let loading = true;
    let error = '';
    let searchParams = {
      query: '',
      propertyType: '',
      minPrice: '',
      maxPrice: '',
      city: '',
      minSize: '',
      maxSize: ''
    };
  
    async function loadProperties() {
      try {
        loading = true;
        error = '';
  
        const filters = {
          search: searchParams.query || undefined,
          property_type: searchParams.propertyType || undefined,
          city: searchParams.city || undefined,
          min_price: searchParams.minPrice || undefined,
          max_price: searchParams.maxPrice || undefined,
          min_size: searchParams.minSize || undefined,
          max_size: searchParams.maxSize || undefined
        };
  
        const response = await fetchProperties(filters);
        properties = response.results || [];
        propertiesStore.set(properties);
        
      } catch (err) {
        console.error('Error loading properties:', err);
        error = err.message || $t('error.fetchFailed');
      } finally {
        loading = false;
      }
    }
  
    function handleSearch(event) {
      searchParams = event.detail;
      loadProperties();
    }
  
    onMount(() => {
      loadProperties();
    });
  </script>
  
  <svelte:head>
    <title>{$t('nav.properties')} | Real Estate Platform</title>
  </svelte:head>
  
  <div class="bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Hero section -->
      <div class="text-center mb-12">
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">
          {$t('properties.title')}
        </h1>
        <p class="mt-3 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
          {$t('properties.subtitle')}
        </p>
      </div>
  
      <!-- Search section -->
      <div class="mb-8">
        <PropertySearch {searchParams} on:search={handleSearch} />
      </div>
  
      <!-- Property listings -->
      {#if loading}
        <div class="flex justify-center py-24">
          <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      {:else if error}
        <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg text-red-800 dark:text-red-200 max-w-3xl mx-auto my-12">
          <h2 class="text-xl font-semibold mb-2">{$t('error.title')}</h2>
          <p>{error}</p>
        </div>
      {:else if properties.length === 0}
        <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-lg shadow">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">{$t('properties.noResults')}</h3>
          <p class="text-gray-500 dark:text-gray-400">{$t('properties.tryAdjusting')}</p>
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each properties as property}
            <PropertyCard {property} />
          {/each}
        </div>
      {/if}
    </div>
  </div>