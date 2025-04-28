<!-- src/lib/components/TagList.svelte -->
<script>
    export let tags = [];
    export let selectedTags = [];
    export let readonly = false;
    
    import { createEventDispatcher } from 'svelte';
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
  
<div class="flex flex-wrap gap-2">
  {#each tags as tag}
    <button
      type="button"
      class={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors ${
        selectedTags.includes(tag)
          ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
      } ${readonly ? 'cursor-default' : 'cursor-pointer'}`}
      on:click={() => toggleTag(tag)}
      disabled={readonly}
    >
      {tag}
      {#if !readonly && selectedTags.includes(tag)}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      {/if}
    </button>
  {/each}
</div>