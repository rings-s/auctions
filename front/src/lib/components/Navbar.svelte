<!-- src/lib/components/Navbar.svelte -->
<script>
    import { page } from '$app/stores';
    import { user } from '$lib/stores/user';
    import { t } from '$lib/i18n/i18n';
    import ThemeToggle from './ThemeToggle.svelte';
    import LanguageSelector from './LanguageSelector.svelte';
    import { onMount } from 'svelte';
    
    let isOpen = false;
    let scrollY;
    let navbarSolid = false;
    
    // Toggle mobile menu
    function toggleMenu() {
      isOpen = !isOpen;
    }
    
    // Logout function
    async function logout() {
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (refreshToken) {
          const response = await fetch('http://localhost:8000/api/accounts/logout/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
          });
          
          if (response.ok) {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            user.set(null);
            window.location.href = '/';
          }
        }
      } catch (error) {
        console.error('Logout failed:', error);
      }
    }
    
    // Make navbar solid on scroll
    function handleScroll() {
      navbarSolid = scrollY > 10;
    }
    
    onMount(() => {
      return () => {
        window.removeEventListener('scroll', handleScroll);
      };
    });
  </script>
  
  <svelte:window bind:scrollY on:scroll={handleScroll} />
  
  <nav class={`fixed w-full z-30 transition-all duration-300 ${navbarSolid ? 'bg-white dark:bg-gray-900 shadow-md' : 'bg-transparent'}`}>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <a href="/" class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              RealEstate
            </a>
          </div>
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <a 
              href="/" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 ${$page.url.pathname === '/' ? 'border-primary-500 text-gray-900 dark:text-white' : 'border-transparent text-gray-500 dark:text-gray-300 hover:text-gray-700 dark:hover:text-gray-200'}`}
            >
              {$t('nav.home')}
            </a>
            <a 
              href="/properties" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 ${$page.url.pathname.startsWith('/properties') ? 'border-primary-500 text-gray-900 dark:text-white' : 'border-transparent text-gray-500 dark:text-gray-300 hover:text-gray-700 dark:hover:text-gray-200'}`}
            >
              {$t('nav.properties')}
            </a>
            <a 
              href="/auctions" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 ${$page.url.pathname.startsWith('/auctions') ? 'border-primary-500 text-gray-900 dark:text-white' : 'border-transparent text-gray-500 dark:text-gray-300 hover:text-gray-700 dark:hover:text-gray-200'}`}
            >
              {$t('nav.auctions')}
            </a>
          </div>
        </div>
        <div class="hidden sm:ml-6 sm:flex sm:items-center sm:space-x-4">
          <ThemeToggle />
          <LanguageSelector />
          
          {#if $user}
            <div class="relative">
              <button type="button" class="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                <span class="sr-only">Open user menu</span>
                {#if $user.avatar_url}
                  <img class="h-8 w-8 rounded-full" src={$user.avatar_url} alt={$user.first_name} />
                {:else}
                  <div class="h-8 w-8 rounded-full bg-primary-500 flex items-center justify-center text-white">
                    {$user.first_name[0]}{$user.last_name[0]}
                  </div>
                {/if}
              </button>
              <!-- Profile dropdown would go here -->
            </div>
            <a href="/profile" class="text-sm font-medium text-gray-700 dark:text-gray-200 hover:text-gray-800 dark:hover:text-white">
              {$user.first_name}
            </a>
            <button 
              on:click={logout} 
              class="ml-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {$t('nav.logout')}
            </button>
          {:else}
            <a href="/login" class="text-sm font-medium text-gray-700 dark:text-gray-200 hover:text-gray-800 dark:hover:text-white">
              {$t('nav.login')}
            </a>
            <a href="/register" class="ml-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
              {$t('nav.register')}
            </a>
          {/if}
        </div>
        
        <!-- Mobile menu button -->
        <div class="flex items-center sm:hidden">
          <ThemeToggle />
          <LanguageSelector />
          <button 
            type="button" 
            class="ml-2 inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
            on:click={toggleMenu}
          >
            <span class="sr-only">Open main menu</span>
            <svg class={isOpen ? 'hidden' : 'block'} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true" width="24" height="24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg class={isOpen ? 'block' : 'hidden'} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true" width="24" height="24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Mobile menu -->
    <div class={isOpen ? 'block sm:hidden' : 'hidden sm:hidden'}>
      <div class="pt-2 pb-3 space-y-1">
        <a href="/" class={`block pl-3 pr-4 py-2 border-l-4 ${$page.url.pathname === '/' ? 'border-primary-500 text-primary-700 dark:text-primary-400 bg-primary-50 dark:bg-gray-800' : 'border-transparent text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
          {$t('nav.home')}
        </a>
        <a href="/properties" class={`block pl-3 pr-4 py-2 border-l-4 ${$page.url.pathname.startsWith('/properties') ? 'border-primary-500 text-primary-700 dark:text-primary-400 bg-primary-50 dark:bg-gray-800' : 'border-transparent text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
          {$t('nav.properties')}
        </a>
        <a href="/auctions" class={`block pl-3 pr-4 py-2 border-l-4 ${$page.url.pathname.startsWith('/auctions') ? 'border-primary-500 text-primary-700 dark:text-primary-400 bg-primary-50 dark:bg-gray-800' : 'border-transparent text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
          {$t('nav.auctions')}
        </a>
      </div>
      <div class="pt-4 pb-3 border-t border-gray-200 dark:border-gray-700">
        {#if $user}
          <div class="flex items-center px-4">
            <div class="flex-shrink-0">
              {#if $user.avatar_url}
                <img class="h-10 w-10 rounded-full" src={$user.avatar_url} alt={$user.first_name} />
              {:else}
                <div class="h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-medium">
                  {$user.first_name[0]}{$user.last_name[0]}
                </div>
              {/if}
            </div>
            <div class="ml-3">
              <div class="text-base font-medium text-gray-800 dark:text-white">{$user.first_name} {$user.last_name}</div>
              <div class="text-sm font-medium text-gray-500 dark:text-gray-400">{$user.email}</div>
            </div>
          </div>
          <div class="mt-3 space-y-1">
            <a href="/profile" class="block px-4 py-2 text-base font-medium text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700">
              {$t('nav.profile')}
            </a>
            <button 
              on:click={logout}
              class="block w-full text-left px-4 py-2 text-base font-medium text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              {$t('nav.logout')}
            </button>
          </div>
        {:else}
          <div class="flex flex-col space-y-2 px-4">
            <a href="/login" class="block text-center py-2 text-base font-medium text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">
              {$t('nav.login')}
            </a>
            <a href="/register" class="block text-center py-2 text-base font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md">
              {$t('nav.register')}
            </a>
          </div>
        {/if}
      </div>
    </div>
  </nav>
  
  <!-- Add padding for fixed navbar -->
  <div class="h-16"></div>