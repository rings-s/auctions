<!-- src/lib/components/MediaUploader.svelte -->
<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { t } from '$lib/i18n/i18n';
    
    export let mediaFiles = [];
    export let maxFiles = 10;
    export let maxSize = 10 * 1024 * 1024; // 10MB
    export let allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    export let disabled = false;
    
    const dispatch = createEventDispatcher();
    
    let dragActive = false;
    let errors = [];
    
    function handleFileInput(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        addFiles(Array.from(files));
      }
    }
  
    function handleDrop(event) {
      event.preventDefault();
      dragActive = false;
      
      const files = event.dataTransfer.files;
      if (files && files.length > 0) {
        addFiles(Array.from(files));
      }
    }
  
    function handleDragOver(event) {
      event.preventDefault();
      dragActive = true;
    }
    
    function handleDragLeave() {
      dragActive = false;
    }
    
    function addFiles(newFiles) {
      errors = [];
      
      const validFiles = newFiles.filter(file => {
        // Check file type
        if (!allowedTypes.includes(file.type)) {
          errors.push(`${file.name}: ${$t('mediaUploader.invalidType')}`);
          return false;
        }
        
        // Check file size
        if (file.size > maxSize) {
          errors.push(`${file.name}: ${$t('mediaUploader.fileTooLarge')}`);
          return false;
        }
        
        return true;
      });
      
      // Check maximum number of files
      if (mediaFiles.length + validFiles.length > maxFiles) {
        errors.push($t('mediaUploader.tooManyFiles', { max: maxFiles }));
        mediaFiles = [...mediaFiles, ...validFiles.slice(0, maxFiles - mediaFiles.length)];
      } else {
        mediaFiles = [...mediaFiles, ...validFiles];
      }
      
      // Notify parent component
      dispatch('change', mediaFiles);
    }
  
    function removeFile(index) {
      mediaFiles = mediaFiles.filter((_, i) => i !== index);
      dispatch('change', mediaFiles);
    }
  </script>
  
  <div class="space-y-4">
    <label for="media-upload" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      {$t('property.mediaFiles')}
    </label>
    
    <!-- Drag & Drop Area -->
    <div 
      class={`mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-md transition-colors
        ${dragActive ? 'border-primary-400 bg-primary-50 dark:border-primary-500 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      on:drop={handleDrop}
      on:dragover={handleDragOver}
      on:dragleave={handleDragLeave}
    >
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
              accept={allowedTypes.join(',')}
              multiple 
              class="sr-only" 
              on:change={handleFileInput}
              disabled={disabled || mediaFiles.length >= maxFiles}
            />
          </label>
          <p class="pl-1">{$t('property.dragDrop')}</p>
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          {$t('property.fileTypes')} ({Math.round(maxSize / 1024 / 1024)}MB max)
        </p>
      </div>
    </div>
    
    <!-- Error messages -->
    {#if errors.length > 0}
      <div class="mt-2 text-sm text-red-600 dark:text-red-400 space-y-1">
        {#each errors as error}
          <p>{error}</p>
        {/each}
      </div>
    {/if}
    
    <!-- Selected files preview -->
    {#if mediaFiles.length > 0}
      <div class="mt-4">
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {$t('property.selectedFiles')} ({mediaFiles.length}/{maxFiles})
        </h4>
        <ul class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {#each mediaFiles as file, index}
            <li class="relative border border-gray-200 dark:border-gray-700 rounded-md overflow-hidden h-32 group">
              <img src={URL.createObjectURL(file)} alt={file.name} class="w-full h-full object-cover" />
              <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity flex items-center justify-center opacity-0 group-hover:opacity-100">
                <button 
                  type="button" 
                  class="bg-red-500 text-white rounded-full p-2 transform scale-75 hover:scale-100 transition-transform"
                  on:click={() => removeFile(index)}
                  aria-label={`Remove file ${file.name}`}
                  disabled={disabled}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs px-2 py-1 truncate">
                {file.name}
              </div>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>
