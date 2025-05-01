<!-- src/routes/properties/create/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n/i18n';
    import { user } from '$lib/stores/user';
    import { createProperty, uploadPropertyMedia } from '$lib/api/property';
    import PropertyForm from '$lib/components/PropertyForm.svelte';
  
    let property;
    let rooms = [];
    let activeTab = 'basic';
    let loading = false;
    let error = '';
    let success = '';
    let mediaFiles = [];
    let uploadingMedia = false;
    let propertyId = null;
  
    onMount(() => {
      // Check if user is logged in
      if (!$user) {
        goto('/login?redirect=/properties/create');
      }
    });
  
    async function handleSubmit() {
      try {
        loading = true;
        error = '';
        success = '';
  
        // Basic validation
        if (!property.title) {
          error = $t('property.titleRequired');
          return;
        }
  
        if (!property.deed_number) {
          error = $t('property.deedNumberRequired');
          return;
        }
  
        if (!property.market_value) {
          error = $t('property.marketValueRequired');
          return;
        }
  
        // Get prepared data from the form component
        const { property: preparedProperty, rooms: preparedRooms } = property.prepareDataForSubmission();
  
        // Create property
        const response = await createProperty(preparedProperty);
        
        if (response && response.id) {
          propertyId = response.id;
          
          // If we have rooms, create them
          if (preparedRooms.length > 0) {
            // Add rooms logic here (would need a separate API endpoint)
            // For now, we'll just log this
            console.log('Would create rooms:', preparedRooms);
          }
          
          // If we have media files, upload them
          if (mediaFiles.length > 0) {
            uploadingMedia = true;
            
            for (const file of mediaFiles) {
              await uploadPropertyMedia(propertyId, file);
            }
            
            uploadingMedia = false;
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
  
    function handleFileInput(event) {
      const files = event.target.files;
      mediaFiles = Array.from(files);
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
  
      <form on:submit|preventDefault={handleSubmit}>
        <div class="space-y-8">
          <!-- Property Information Form -->
          <PropertyForm bind:this={property} {rooms} {activeTab} {error} {loading} />
  
          <!-- Media Upload -->
          <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <div>
                <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('property.mediaUpload')}</h3>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('property.mediaUploadDesc')}</p>
              </div>
  
              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {$t('property.mediaFiles')}
                </label>
                <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-md">
                  <div class="space-y-1 text-center">
                    <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <div class="flex text-sm text-gray-600 dark:text-gray-400">
                      <label for="media-upload" class="relative cursor-pointer bg-white dark:bg-gray-800 rounded-md font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
                        <span>{$t('property.uploadFiles')}</span>
                        <input 
                          id="media-upload" 
                          name="media-upload" 
                          type="file" 
                          accept="image/*" 
                          multiple 
                          class="sr-only" 
                          on:change={handleFileInput}
                        />
                      </label>
                      <p class="pl-1">{$t('property.dragDrop')}</p>
                    </div>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                      {$t('property.fileTypes')}
                    </p>
                  </div>
                </div>
              </div>
  
              {#if mediaFiles.length > 0}
                <div class="mt-4">
                  <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{$t('property.selectedFiles')}</h4>
                  <ul class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    {#each mediaFiles as file, index}
                      <li class="relative border border-gray-200 dark:border-gray-700 rounded-md overflow-hidden h-32">
                        <img src={URL.createObjectURL(file)} alt={file.name} class="w-full h-full object-cover" />
                        <button 
                          type="button" 
                          class="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1"
                          on:click={() => {
                            mediaFiles = mediaFiles.filter((_, i) => i !== index);
                          }}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </li>
                    {/each}
                  </ul>
                </div>
              {/if}
            </div>
          </div>
  
          <!-- Submit Buttons -->
          <div class="flex justify-end">
            <button
              type="button"
              on:click={() => goto('/properties')}
              class="bg-white dark:bg-gray-800 py-2 px-4 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {$t('property.cancel')}
            </button>
            <button
              type="submit"
              disabled={loading || uploadingMedia}
              class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {#if loading || uploadingMedia}
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              {/if}
              {$t('property.create')}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>