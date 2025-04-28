<!-- src/routes/properties/[slug]/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { t } from '$lib/i18n/i18n';
    import { fetchPropertyBySlug } from '$lib/api/property';
    import { fetchAuctions } from '$lib/api/auction';
    import { user } from '$lib/stores/user';
    
    import PropertyMap from '$lib/components/PropertyMap.svelte';
    import AuctionCard from '$lib/components/AuctionCard.svelte';
    import TagList from '$lib/components/TagList.svelte';
    
    let property = null;
    let relatedAuctions = [];
    let loading = true;
    let error = null;
    let activeImageIndex = 0;
    
    $: slug = $page.params.slug;
    
    async function loadPropertyData() {
      loading = true;
      error = null;
      
      try {
        // Fetch property details
        const propertyData = await fetchPropertyBySlug(slug);
        property = propertyData;
        
        // Fetch auctions related to this property
        const auctionsResponse = await fetchAuctions({ related_property: property.id });
        relatedAuctions = auctionsResponse.results || [];
        
      } catch (err) {
        console.error('Error loading property details:', err);
        error = err.message;
      } finally {
        loading = false;
      }
    }
    
    onMount(() => {
      loadPropertyData();
    });
    
    function changeImage(index) {
      activeImageIndex = index;
    }
  </script>
  
  <svelte:head>
    <title>{property?.title || 'Property'} | Real Estate Platform</title>
  </svelte:head>
  
  <div class="bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      {#if loading}
        <div class="flex justify-center py-24">
          <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      {:else if error}
        <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg text-red-800 dark:text-red-200 max-w-3xl mx-auto my-12">
          <h2 class="text-xl font-semibold mb-2">{$t('error.title')}</h2>
          <p>{error}</p>
          <a href="/properties" class="mt-4 inline-block text-primary-600 dark:text-primary-400 hover:underline">
            &larr; {$t('properties.backToProperties')}
          </a>
        </div>
      {:else if property}
        <!-- Breadcrumbs -->
        <nav class="mb-6 text-sm">
          <ol class="flex flex-wrap items-center space-x-2">
            <li>
              <a href="/" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">{$t('nav.home')}</a>
            </li>
            <li class="flex items-center">
              <span class="text-gray-400 mx-1">/</span>
              <a href="/properties" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">{$t('nav.properties')}</a>
            </li>
            <li class="flex items-center">
              <span class="text-gray-400 mx-1">/</span>
              <span class="text-gray-700 dark:text-gray-300 truncate">{property.title}</span>
            </li>
          </ol>
        </nav>
        
        <!-- Property header -->
        <div class="mb-8">
          <div class="flex flex-wrap items-start justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">{property.title}</h1>
              <p class="text-lg text-gray-600 dark:text-gray-300 mb-2">{property.address}, {property.city}, {property.state}</p>
              <div class="flex flex-wrap gap-2 mt-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                  {property.property_type_display}
                </span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium 
                  {property.status === 'available' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
                  property.status === 'auction' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 
                  property.status === 'sold' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : 
                  'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}"
                >
                  {property.status_display}
                </span>
                {#if property.is_featured}
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                    {$t('property.featured')}
                  </span>
                {/if}
              </div>
            </div>
            
            <div class="mt-4 md:mt-0">
              <div class="text-3xl font-bold text-gray-900 dark:text-white">${property.market_value.toLocaleString()}</div>
              <div class="text-sm text-gray-500 dark:text-gray-400">{property.size_sqm} {$t('property.sqm')}</div>
            </div>
          </div>
        </div>
        
        <!-- Property gallery -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          <div>
            <div class="bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden aspect-w-4 aspect-h-3 mb-4">
              {#if property.media && property.media.length > 0}
                <img 
                  src={property.media[activeImageIndex]?.file || '/images/property-placeholder.jpg'} 
                  alt={property.title}
                  class="w-full h-full object-cover"
                />
              {:else}
                <img 
                  src="/images/property-placeholder.jpg" 
                  alt={property.title}
                  class="w-full h-full object-cover"
                />
              {/if}
            </div>
            
            {#if property.media && property.media.length > 1}
              <div class="grid grid-cols-5 gap-2">
                {#each property.media as image, index}
                  {#if image.media_type === 'image'}
                    <button 
                      on:click={() => changeImage(index)}
                      class={`aspect-w-1 aspect-h-1 rounded-md overflow-hidden border-2 ${activeImageIndex === index ? 'border-primary-500' : 'border-transparent'}`}
                    >
                      <img src={image.file} alt={property.title} class="w-full h-full object-cover" />
                    </button>
                  {/if}
                {/each}
              </div>
            {/if}
          </div>
          
          <div>
            <!-- Property details -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{$t('property.propertyDetails')}</h2>
              
              <div class="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.propertyType')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">{property.property_type_display}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.buildingType')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">{property.building_type || '-'}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.size')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">{property.size_sqm} {$t('property.sqm')}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.yearBuilt')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">{property.year_built || '-'}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.floors')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">{property.floors || '-'}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.rooms')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">{property.rooms?.length || '0'}</p>
                </div>
              </div>
              
              {#if property.features && property.features.length > 0}
                <div class="mb-6">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">{$t('property.features')}</h3>
                  <TagList tags={property.features} readonly={true} />
                </div>
              {/if}
              
              {#if property.amenities && property.amenities.length > 0}
                <div>
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">{$t('property.amenities')}</h3>
                  <TagList tags={property.amenities} readonly={true} />
                </div>
              {/if}
            </div>
            
            <!-- Contact owner -->
            {#if property.owner && property.status === 'available'}
              <div class="bg-primary-50 dark:bg-primary-900/20 rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold text-primary-900 dark:text-primary-100 mb-4">{$t('property.contactOwner')}</h2>
                
                {#if $user}
                  <div class="mb-4">
                    <label for="message" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{$t('property.message')}</label>
                    <textarea 
                      id="message" 
                      rows="4" 
                      class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder={$t('property.messagePlaceholder')}
                    ></textarea>
                  </div>
                  
                  <button class="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                    {$t('property.sendMessage')}
                  </button>
                {:else}
                  <p class="text-gray-700 dark:text-gray-300 mb-4">{$t('property.loginToContact')}</p>
                  <a href="/login" class="block w-full text-center py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                    {$t('nav.login')}
                  </a>
                {/if}
              </div>
            {/if}
          </div>
        </div>
        
        <!-- Property description -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-12">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{$t('property.description')}</h2>
          <div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
            <p>{property.description}</p>
          </div>
        </div>
        
        <!-- Property location -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-12">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{$t('property.location')}</h2>
          <div class="h-96">
            <PropertyMap 
              latitude={property.latitude} 
              longitude={property.longitude} 
              title={property.title}
            />
          </div>
        </div>
        
        <!-- Room list -->
        {#if property.rooms && property.rooms.length > 0}
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-12">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{$t('property.roomList')}</h2>
            
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      {$t('property.roomType')}
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      {$t('property.name')}
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      {$t('property.floor')}
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      {$t('property.area')}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {#each property.rooms as room}
                    <tr>
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {room.room_type_display}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                        {room.name}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                        {room.floor}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                        {room.area_sqm || '-'} {room.area_sqm ? $t('property.sqm') : ''}
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </div>
        {/if}
        
        <!-- Related auctions -->
        <div class="mb-12">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">{$t('property.relatedAuctions')}</h2>
          
          {#if relatedAuctions.length === 0}
            <div class="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">{$t('property.noAuctions')}</h3>
            </div>
          {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {#each relatedAuctions as auction}
                <AuctionCard {auction} />
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>