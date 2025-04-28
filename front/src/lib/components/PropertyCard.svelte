<!-- src/lib/components/PropertyCard.svelte -->
<script>
    import { t } from '$lib/i18n/i18n';
    
    export let property;
  </script>
  
  <a 
    href={`/properties/${property.slug}`} 
    class="block h-full group"
  >
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-shadow duration-300 hover:shadow-lg h-full flex flex-col">
      <div class="relative h-56">
        <img 
          src={property.main_image || '/images/property-placeholder.jpg'} 
          alt={property.title}
          class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div class="absolute top-0 right-0 m-2">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
            {property.status_display}
          </span>
        </div>
        {#if property.is_featured}
          <div class="absolute top-0 left-0 m-2">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
              {$t('property.featured')}
            </span>
          </div>
        {/if}
        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
          <h3 class="text-lg font-semibold text-white truncate">{property.title}</h3>
          <p class="text-sm text-gray-200">{property.city}, {property.state}</p>
        </div>
      </div>
      
      <div class="p-4 flex-grow">
        <div class="mb-3">
          <span class="inline-block bg-gray-100 dark:bg-gray-700 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 dark:text-gray-300">
            {property.property_type_display}
          </span>
          <span class="ml-2 text-xl font-bold text-gray-900 dark:text-white">
            ${property.market_value.toLocaleString()}
          </span>
        </div>
        
        <p class="text-gray-600 dark:text-gray-300 line-clamp-2 text-sm mb-3">{property.description}</p>
        
        <div class="grid grid-cols-2 gap-2 text-sm text-gray-500 dark:text-gray-400">
          <div class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5" />
            </svg>
            {property.size_sqm} m²
          </div>
          <div class="flex items-center">
            <!-- src/lib/components/PropertyCard.svelte (continued) -->
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            {property.rooms_count} {$t('property.rooms')}
            </div>
        </div>
        </div>
        
        <div class="border-t border-gray-200 dark:border-gray-700 p-4">
        <div class="flex items-center justify-between">
            <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {new Date(property.created_at).toLocaleDateString()}
            </div>
            <span class="inline-flex items-center text-sm text-primary-600 dark:text-primary-400 font-medium">
            {$t('property.viewDetails')}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            </span>
        </div>
        </div>
    </div>
</a>
