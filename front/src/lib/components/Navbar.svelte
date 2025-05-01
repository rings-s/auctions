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
  
  <nav class={`fixed w-full z-30 transition-all duration-300 ${navbarSolid ? 'bg-white/90 dark:bg-gray-900/90 shadow-lg backdrop-blur' : 'bg-transparent'}`}>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <a href="/" class="text-2xl font-bold text-primary-700 dark:text-primary-300">
              RealEstate
            </a>
          </div>
          <!-- Desktop links, hidden on md and below -->
          <div class="hidden lg:ml-6 lg:flex lg:space-x-8">
            <slot name="nav-links">
              <a href="/" class={`inline-flex items-center px-1 pt-1 border-b-2 ${$page.url.pathname === '/' ? 'border-primary-500 text-primary-700 dark:text-primary-300' : 'border-transparent text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400'}`}>{$t('nav.home')}</a>
              <a href="/properties" class={`inline-flex items-center px-1 pt-1 border-b-2 ${$page.url.pathname.startsWith('/properties') ? 'border-secondary-500 text-secondary-700 dark:text-secondary-300' : 'border-transparent text-gray-600 dark:text-gray-300 hover:text-secondary-600 dark:hover:text-secondary-400'}`}>{$t('nav.properties')}</a>
              <a href="/auctions" class={`inline-flex items-center px-1 pt-1 border-b-2 ${$page.url.pathname.startsWith('/auctions') ? 'border-success-500 text-success-700 dark:text-success-300' : 'border-transparent text-gray-600 dark:text-gray-300 hover:text-success-600 dark:hover:text-success-400'}`}>{$t('nav.auctions')}</a>
            </slot>
          </div>
        </div>
        <!-- Right side: Theme, Language, Auth -->
        <div class="hidden lg:ml-6 lg:flex lg:items-center lg:space-x-4">
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
            </div>
            <button 
              on:click={logout}
              class="block w-full text-left px-4 py-2 text-base font-semibold rounded transition-all focus:outline-none focus:ring-2 focus:ring-danger-400 focus:ring-offset-2 bg-danger-600 hover:bg-danger-700 dark:bg-danger-500 dark:hover:bg-danger-600 text-white dark:text-gray-900"
            >
              {$t('nav.logout')}
            </button>
          {:else}
            <a href="/login" class="px-4 py-2 text-sm font-semibold rounded transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 bg-primary-600 hover:bg-primary-700 dark:bg-primary-400 dark:hover:bg-primary-500 text-white dark:text-gray-900">{$t('nav.login')}</a>
            <a href="/register" class="px-4 py-2 text-sm font-semibold rounded transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-secondary-400 focus:ring-offset-2 bg-secondary-600 hover:bg-secondary-700 dark:bg-secondary-400 dark:hover:bg-secondary-500 text-white dark:text-gray-900">{$t('nav.register')}</a>
          {/if}
        </div>
        <!-- Mobile menu toggle, visible on xs, sm, md -->
        <div class="flex flex-row items-center gap-4 lg:hidden">
          <ThemeToggle />
          <LanguageSelector />
          <button 
            type="button" 
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
            on:click={toggleMenu}
            aria-label="Toggle navigation menu"
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
    <!-- Mobile menu, visible on xs, sm, md only -->
    <div class={isOpen ? 'block lg:hidden' : 'hidden lg:hidden'}>
      <div class="pt-2 pb-3 space-y-1">
        <slot name="mobile-nav-links">
          <a href="/" class={`block pl-3 pr-4 py-2 border-l-4 ${$page.url.pathname === '/' ? 'border-primary-500 text-primary-700 dark:text-primary-300 bg-primary-50 dark:bg-gray-900/70' : 'border-transparent text-gray-700 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-gray-800'}`}>{$t('nav.home')}</a>
          <a href="/properties" class={`block pl-3 pr-4 py-2 border-l-4 ${$page.url.pathname.startsWith('/properties') ? 'border-secondary-500 text-secondary-700 dark:text-secondary-300 bg-secondary-50 dark:bg-gray-900/70' : 'border-transparent text-gray-700 dark:text-gray-300 hover:bg-secondary-50 dark:hover:bg-gray-800'}`}>{$t('nav.properties')}</a>
          <a href="/auctions" class={`block pl-3 pr-4 py-2 border-l-4 ${$page.url.pathname.startsWith('/auctions') ? 'border-success-500 text-success-700 dark:text-success-300 bg-success-50 dark:bg-gray-900/70' : 'border-transparent text-gray-700 dark:text-gray-300 hover:bg-success-50 dark:hover:bg-gray-800'}`}>{$t('nav.auctions')}</a>
        </slot>
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
            <a href="/profile" class="block px-4 py-2 text-base font-semibold rounded transition-all focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 text-primary-700 dark:text-primary-200 hover:bg-primary-50 dark:hover:bg-primary-800">{$t('nav.profile')}</a>
            <button 
              on:click={logout}
              class="block w-full text-left px-4 py-2 text-base font-semibold rounded transition-all focus:outline-none focus:ring-2 focus:ring-danger-400 focus:ring-offset-2 bg-danger-600 hover:bg-danger-700 dark:bg-danger-500 dark:hover:bg-danger-600 text-white dark:text-gray-900"
            >
              {$t('nav.logout')}
            </button>
          </div>
        {:else}
          <div class="flex flex-col space-y-2 px-4">
            <a href="/login" class="block text-center py-2 text-base font-semibold rounded transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 bg-primary-600 hover:bg-primary-700 dark:bg-primary-400 dark:hover:bg-primary-500 text-white dark:text-gray-900">{$t('nav.login')}</a>
            <a href="/register" class="block text-center py-2 text-base font-semibold rounded transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-secondary-400 focus:ring-offset-2 bg-secondary-600 hover:bg-secondary-700 dark:bg-secondary-400 dark:hover:bg-secondary-500 text-white dark:text-gray-900">{$t('nav.register')}</a>
          </div>
        {/if}
      </div>
    </div>
  </nav>
  <!-- Add padding for fixed navbar -->
  <div class="h-16"></div>