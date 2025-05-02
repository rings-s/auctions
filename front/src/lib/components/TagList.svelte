<!-- src/lib/components/TagSelector.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  
  export let tags = [];
  export let selectedTags = [];
  export let title = '';
  export let readonly = false;
  
  const dispatch = createEventDispatcher();
  
  function toggleTag(tag) {
    if (readonly) return;
    
    if (selectedTags.includes(tag)) {
      selectedTags = selectedTags.filter(t => t !== tag);
    } else {
      selectedTags = [...selectedTags, tag];
    }
    
    dispatch('change', selectedTags);
  }
</script>

<div class="space-y-2">
  {#if title}
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{title}</label>
  {/if}
  
  <div class="flex flex-wrap gap-2">
    {#each tags as tag}
      <button
        type="button"
        on:click={() => toggleTag(tag)}
        disabled={readonly}
        class={`
          px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
          ${selectedTags.includes(tag) 
            ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 ring-2 ring-primary-300 dark:ring-primary-700'
            : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'}
          ${readonly ? 'cursor-default' : 'cursor-pointer'}
        `}
        aria-pressed={selectedTags.includes(tag)}
      >
        <span class="flex items-center">
          {#if selectedTags.includes(tag)}
            <svg class="w-4 h-4 mr-1.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          {/if}
          {tag}
        </span>
      </button>
    {/each}
  </div>
</div>