<!-- src/lib/components/PropertySearch.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { t } from '$lib/i18n/i18n';
    
    export let searchParams = {
      query: '',
      propertyType: '',
      minPrice: '',
      maxPrice: '',
      city: '',
      minSize: '',
      maxSize: ''
    };
    
    const dispatch = createEventDispatcher();
    
    const propertyTypes = [
      { value: 'residential', label: 'nav.propertyTypes.residential' },
      { value: 'commercial', label: 'nav.propertyTypes.commercial' },
      { value: 'land', label: 'nav.propertyTypes.land' },
      { value: 'industrial', label: 'nav.propertyTypes.industrial' },
      { value: 'mixed_use', label: 'nav.propertyTypes.mixedUse' }
    ];
    
    function handleSearch() {
      dispatch('search', searchParams);
    }
    
    function clearFilters() {
      searchParams = {
        query: '',
        propertyType: '',
        minPrice: '',
        maxPrice: '',
        city: '',
        minSize: '',
        maxSize: ''
      };
      dispatch('search', searchParams);
    }
  </script>
  
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
    <div class="mb-4">
      <label for="query" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{$t('search.keyword')}</label>
      <div class="mt-1 relative rounded-md shadow-sm">
        <input
          type="text"
          bind:value={searchParams.query}
          id="query"
          class="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          placeholder={$t('search.keywordPlaceholder')}
        />
      </div>
    </div>
    
    <div class="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label for="propertyType" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{$t('search.propertyType')}</label>
        <select
          id="propertyType"
          bind:value={searchParams.propertyType}
          class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option value="">{$t('search.all')}</option>
          {#each propertyTypes as type}
            <option value={type.value}>{$t(type.label)}</option>
          {/each}
        </select>
      </div>
      
      <div>
        <label for="city" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{$t('search.city')}</label>
        <input
          type="text"
          bind:value={searchParams.city}
          id="city"
          class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          placeholder={$t('search.cityPlaceholder')}
        />
      </div>
    </div>
    
    <div class="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{$t('search.price')}</label>
        <div class="flex items-center space-x-2">
          <input
            type="number"
            bind:value={searchParams.minPrice}
            class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder={$t('search.min')}
          />
          <span class="dark:text-gray-300">-</span>
          <input
            type="number"
            bind:value={searchParams.maxPrice}
            class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder={$t('search.max')}
          />
        </div>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{$t('search.size')} (m²)</label>
        <div class="flex items-center space-x-2">
          <input
            type="number"
            bind:value={searchParams.minSize}
            class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder={$t('search.min')}
          />
          <span class="dark:text-gray-300">-</span>
          <input
            type="number"
            bind:value={searchParams.maxSize}
            class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder={$t('search.max')}
          />
        </div>
      </div>
    </div>
    
    <div class="flex justify-between">
      <button
        type="button"
        on:click={clearFilters}
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        {$t('search.clear')}
      </button>
      <button
        type="button"
        on:click={handleSearch}
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        {$t('search.search')}
      </button>
    </div>
  </div>