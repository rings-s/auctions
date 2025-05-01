<script>
  import { theme } from '$lib/stores/theme';
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';

  // Ensure dark class is applied to <html>
  function applyTheme(t) {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', t === 'dark');
    }
  }

  onMount(() => {
    const saved = localStorage.getItem('theme');
    let initial;
    if (saved === 'dark' || saved === 'light') {
      initial = saved;
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      initial = 'dark';
    } else {
      initial = 'light';
    }
    theme.set(initial);
    applyTheme(initial);

    // Reactively update <html> class on theme change
    const unsubscribe = theme.subscribe(t => {
      applyTheme(t);
    });
    return unsubscribe;
  });

  function toggleTheme() {
    theme.update(t => {
      const next = t === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', next);
      applyTheme(next);
      return next;
    });
  }
</script>

<button
  class="p-2.5 rounded-full bg-white dark:bg-gray-800 shadow-md hover:shadow-lg border border-gray-200 dark:border-gray-700 transition-all duration-300 hover:scale-105"
  on:click={toggleTheme}
  aria-label="Toggle theme"
>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="18"
    height="18"
    fill="none"
    viewBox="0 0 24 24"
    class={$theme === 'dark' ? 'text-blue-500' : 'text-yellow-400'}
  >
    {#if $theme === 'dark'}
      <!-- Moon icon -->
      <path d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" fill="currentColor"/>
      <circle cx="18" cy="6" r="1" fill="currentColor"/>
      <circle cx="20.5" cy="10" r="0.5" fill="currentColor"/>
      <circle cx="15.5" cy="3.5" r="0.5" fill="currentColor"/>
    {:else}
      <!-- Sun icon -->
      <circle cx="12" cy="12" r="4" fill="currentColor"/>
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    {/if}
  </svg>
</button>