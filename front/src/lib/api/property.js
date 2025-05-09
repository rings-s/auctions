// src/lib/api/property.js

import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

// API endpoints with trailing slashes
const ENDPOINTS = {
  PROPERTIES: `${API_BASE_URL}/properties/`,
  MEDIA: `${API_BASE_URL}/media/`
};

// Helper Functions
function ensureTrailingSlash(url) {
  const [baseUrl, queryString] = url.split('?');
  const urlWithSlash = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
  return queryString ? `${urlWithSlash}?${queryString}` : urlWithSlash;
}

function getHeaders(token = null) {
  const headers = {
    'Content-Type': 'application/json'
  };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  return headers;
}

async function handleApiError(response) {
  try {
    const data = await response.json();
    throw new Error(data.error?.message || data.detail || 'API request failed');
  } catch (error) {
    throw new Error(error.message || 'API request failed');
  }
}

function formatPropertyData(propertyData) {
  return {
    ...propertyData,
    // Handle nested IDs
    property_type: propertyData.property_type?.id || propertyData.property_type,
    building_type: propertyData.building_type?.id || propertyData.building_type,
    // Format rooms data if present
    rooms: Array.isArray(propertyData.rooms) 
      ? propertyData.rooms.map(room => ({
          ...room,
          room_type: room.room_type?.id || room.room_type
        }))
      : [],
    // Convert number strings to numbers
    size_sqm: Number(propertyData.size_sqm) || 0,
    market_value: Number(propertyData.market_value) || 0,
    minimum_bid: propertyData.minimum_bid ? Number(propertyData.minimum_bid) : null,
    floors: propertyData.floors ? Number(propertyData.floors) : null,
    year_built: propertyData.year_built ? Number(propertyData.year_built) : null,
    latitude: propertyData.latitude ? Number(propertyData.latitude) : null,
    longitude: propertyData.longitude ? Number(propertyData.longitude) : null
  };
}

/**
 * Fetch properties with filtering, pagination, and search
 */
export async function fetchProperties(filters = {}) {
  try {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const url = `${ENDPOINTS.PROPERTIES}?${queryParams.toString()}`;
    
    let response = await fetch(
      ensureTrailingSlash(url),
      {
        headers,
        credentials: 'include'
      }
    );

    if (response.status === 401 && token) {
      const newToken = await refreshToken();
      response = await fetch(
        ensureTrailingSlash(url),
        {
          headers: { ...headers, 'Authorization': `Bearer ${newToken}` },
          credentials: 'include'
        }
      );
    }

    if (!response.ok) {
      throw await handleApiError(response);
    }

    const data = await response.json();
    if (!data.results) {
      throw new Error('Invalid response format');
    }

    return data;

  } catch (error) {
    console.error('Error fetching properties:', error);
    throw error;
  }
}

/**
 * Fetch a single property by ID
 */
export async function fetchPropertyById(id) {
  try {
    const token = localStorage.getItem('accessToken');
    const url = `${ENDPOINTS.PROPERTIES}${id}/`;
    
    let response = await fetch(
      ensureTrailingSlash(url),
      {
        headers: getHeaders(token),
        credentials: 'include'
      }
    );

    if (response.status === 401 && token) {
      const newToken = await refreshToken();
      response = await fetch(
        ensureTrailingSlash(url),
        {
          headers: getHeaders(newToken),
          credentials: 'include'
        }
      );
    }

    if (!response.ok) {
      throw await handleApiError(response);
    }

    return await response.json();

  } catch (error) {
    console.error('Error fetching property details:', error);
    throw error;
  }
}

/**
 * Fetch a property by slug
 */
export async function fetchPropertyBySlug(slug) {
  try {
    const token = localStorage.getItem('accessToken');
    const url = `${ENDPOINTS.PROPERTIES}${slug}/`;
    
    let response = await fetch(
      ensureTrailingSlash(url),
      {
        headers: getHeaders(token),
        credentials: 'include'
      }
    );

    if (response.status === 401 && token) {
      const newToken = await refreshToken();
      response = await fetch(
        ensureTrailingSlash(url),
        {
          headers: getHeaders(newToken),
          credentials: 'include'
        }
      );
    }

    if (!response.ok) {
      throw await handleApiError(response);
    }

    return await response.json();

  } catch (error) {
    console.error('Error fetching property details:', error);
    throw error;
  }
}

/**
 * Create a new property
 */

// In the createProperty function:
export async function createProperty(propertyData) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) throw new Error('Authentication required');

    console.log('Creating property with data:', propertyData);
    
    // Extract location data to create a location first if needed
    const locationData = {};
    if (propertyData.city) {
      locationData.city = propertyData.city;
      delete propertyData.city;
    }
    if (propertyData.state) {
      locationData.state = propertyData.state;
      delete propertyData.state;
    }
    if (propertyData.country) {
      locationData.country = propertyData.country;
      delete propertyData.country;
    }
    if (propertyData.postal_code) {
      locationData.postal_code = propertyData.postal_code;
      delete propertyData.postal_code;
    }
    if (propertyData.latitude) {
      locationData.latitude = propertyData.latitude;
      delete propertyData.latitude;
    }
    if (propertyData.longitude) {
      locationData.longitude = propertyData.longitude;
      delete propertyData.longitude;
    }
    
    // Create location if we have enough data
    let locationId = null;
    if (locationData.city && locationData.state) {
      try {
        const locationResponse = await fetch(`http://localhost:8000/api/locations/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(locationData)
        });
        
        if (locationResponse.ok) {
          const locationResult = await locationResponse.json();
          locationId = locationResult.id;
          console.log('Created location with ID:', locationId);
        }
      } catch (locationError) {
        console.error('Error creating location:', locationError);
        // Continue with property creation anyway
      }
    }
    
    // If we have a location ID, use it
    if (locationId) {
      propertyData.location = locationId;
    }
    
    // Make sure property_type is a number
    if (propertyData.property_type && typeof propertyData.property_type === 'string') {
      if (!isNaN(parseInt(propertyData.property_type))) {
        propertyData.property_type = parseInt(propertyData.property_type);
      }
    }
    
    // Make sure building_type is a number if provided
    if (propertyData.building_type && propertyData.building_type !== null) {
      if (typeof propertyData.building_type === 'string' && !isNaN(parseInt(propertyData.building_type))) {
        propertyData.building_type = parseInt(propertyData.building_type);
      }
    }
    
    console.log('Sending final property data:', propertyData);
    
    let response = await fetch(`${ENDPOINTS.PROPERTIES}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(propertyData)
    });

    // Log the raw response for debugging
    console.log('Server response status:', response.status);
    
    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      if (response.status === 500) {
        throw new Error('Server error occurred. Please try again.');
      }
      const text = await response.text();
      console.error('Non-JSON response:', text);
      throw new Error(`Server error: ${text}`);
    }

    const data = await response.json();
    console.log('Response data:', data);

    if (!response.ok) {
      // Format validation errors in a user-friendly way
      if (response.status === 400 && typeof data === 'object') {
        const errorMessages = [];
        for (const [field, errors] of Object.entries(data)) {
          if (Array.isArray(errors)) {
            errorMessages.push(`${field}: ${errors.join(', ')}`);
          } else if (typeof errors === 'string') {
            errorMessages.push(`${field}: ${errors}`);
          } else if (typeof errors === 'object') {
            // Handle nested errors
            for (const [nestedField, nestedErrors] of Object.entries(errors)) {
              errorMessages.push(`${field}.${nestedField}: ${nestedErrors}`);
            }
          }
        }
        
        if (errorMessages.length > 0) {
          throw new Error(`Validation errors: ${errorMessages.join('; ')}`);
        }
      }
      
      if (response.status === 401) {
        // Try token refresh
        console.log('Attempting token refresh...');
        const newToken = await refreshToken();
        console.log('Token refreshed, retrying request...');
        
        response = await fetch(`${ENDPOINTS.PROPERTIES}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${newToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(propertyData)
        });
        
        console.log('Retry response status:', response.status);
        const retryData = await response.json();
        console.log('Retry response data:', retryData);

        if (!response.ok) {
          const errorMsg = retryData.detail || 
                         (typeof retryData === 'string' ? retryData : 'Failed to create property');
          throw new Error(errorMsg);
        }
        
        return {
          data: retryData,
          status: response.status
        };
      } else {
        const errorMsg = data.detail || 
                       (typeof data === 'string' ? data : 'Failed to create property');
        throw new Error(errorMsg);
      }
    }

    return {
      data: data,
      status: response.status
    };

  } catch (error) {
    console.error('Error creating property:', error);
    throw error;
  }
}

/**
 * Update an existing property
 */
export async function updateProperty(id, propertyData) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) throw new Error('Authentication required');

    const formattedData = formatPropertyData(propertyData);
    const url = `${ENDPOINTS.PROPERTIES}${id}/`;

    let response = await fetch(
      ensureTrailingSlash(url),
      {
        method: 'PATCH',
        headers: getHeaders(token),
        credentials: 'include',
        body: JSON.stringify(formattedData)
      }
    );

    if (response.status === 401) {
      const newToken = await refreshToken();
      response = await fetch(
        ensureTrailingSlash(url),
        {
          method: 'PATCH',
          headers: getHeaders(newToken),
          credentials: 'include',
          body: JSON.stringify(formattedData)
        }
      );
    }

    if (!response.ok) {
      throw await handleApiError(response);
    }

    return await response.json();

  } catch (error) {
    console.error('Error updating property:', error);
    throw error;
  }
}

/**
 * Delete a property
 */
export async function deleteProperty(id) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) throw new Error('Authentication required');

    const url = `${ENDPOINTS.PROPERTIES}${id}/`;

    let response = await fetch(
      ensureTrailingSlash(url),
      {
        method: 'DELETE',
        headers: getHeaders(token),
        credentials: 'include'
      }
    );

    if (response.status === 401) {
      const newToken = await refreshToken();
      response = await fetch(
        ensureTrailingSlash(url),
        {
          method: 'DELETE',
          headers: getHeaders(newToken),
          credentials: 'include'
        }
      );
    }

    if (!response.ok) {
      throw await handleApiError(response);
    }

    return true;

  } catch (error) {
    console.error('Error deleting property:', error);
    throw error;
  }
}

/**
 * Upload media file for a property
 */
export async function uploadPropertyMedia(propertyId, file, isPrimary = false) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) throw new Error('Authentication required');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('property', propertyId);
    formData.append('is_primary', isPrimary);
    formData.append('media_type', file.type.startsWith('image/') ? 'image' : 'document');

    let response = await fetch(
      ENDPOINTS.MEDIA,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        credentials: 'include',
        body: formData
      }
    );

    if (response.status === 401) {
      const newToken = await refreshToken();
      response = await fetch(
        ENDPOINTS.MEDIA,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${newToken}`
          },
          credentials: 'include',
          body: formData
        }
      );
    }

    if (!response.ok) {
      throw await handleApiError(response);
    }

    return await response.json();

  } catch (error) {
    console.error('Error uploading media:', error);
    throw error;
  }
}

/**
 * Upload multiple media files for a property
 */
export async function uploadPropertyMediaBatch(propertyId, files, onProgress) {
  try {
    const results = [];
    let completed = 0;

    // Upload first image as primary
    const firstImage = files.find(f => f.type.startsWith('image/'));
    if (firstImage) {
      const primaryResult = await uploadPropertyMedia(propertyId, firstImage, true);
      results.push(primaryResult);
      completed++;
      onProgress?.(completed, files.length);
    }

    // Upload remaining files
    for (const file of files) {
      if (file === firstImage) continue;

      const result = await uploadPropertyMedia(propertyId, file, false);
      results.push(result);
      completed++;
      onProgress?.(completed, files.length);
    }

    return results;

  } catch (error) {
    console.error('Error uploading multiple files:', error);
    throw error;
  }
}