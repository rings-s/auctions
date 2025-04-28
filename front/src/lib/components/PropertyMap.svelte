<!-- src/lib/components/PropertyMap.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { t } from '$lib/i18n/i18n';
    
    export let latitude;
    export let longitude;
    export let title = '';
    export let zoom = 14;
    export let interactive = true;
    
    let mapElement;
    let map;
    let marker;
    
    onMount(() => {
      if (!latitude || !longitude) return;
      
      // Load Leaflet from CDN if not already loaded
      if (!window.L) {
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css';
        document.head.appendChild(cssLink);
        
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js';
        script.onload = initializeMap;
        document.head.appendChild(script);
      } else {
        initializeMap();
      }
      
      return () => {
        if (map) map.remove();
      };
    });
    
    function initializeMap() {
      if (!window.L) return;
      
      // Create map
      map = window.L.map(mapElement, {
        center: [latitude, longitude],
        zoom,
        scrollWheelZoom: interactive,
        dragging: interactive,
        tap: interactive,
        zoomControl: interactive
      });
      
      // Add tile layer
      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      
      // Add marker
      marker = window.L.marker([latitude, longitude]).addTo(map);
      if (title) {
        marker.bindPopup(title).openPopup();
      }
      
      // Refresh map size after render
      setTimeout(() => {
        map.invalidateSize();
      }, 100);
    }
    
    onDestroy(() => {
      if (map) map.remove();
    });
  </script>
  
  <div 
    bind:this={mapElement} 
    class="w-full h-full min-h-[300px] rounded-lg overflow-hidden shadow-inner"
  ></div>
  
  {#if !latitude || !longitude}
    <div class="flex justify-center items-center bg-gray-100 dark:bg-gray-700 w-full h-full min-h-[300px] rounded-lg">
      <p class="text-gray-500 dark:text-gray-400">{$t('property.noLocationData')}</p>
    </div>
  {/if}