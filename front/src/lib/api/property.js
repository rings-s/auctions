// src/lib/api/property.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const PROPERTY_URL = `${API_BASE_URL}/properties`;
const MEDIA_URL = `${API_BASE_URL}/media`;

// Fetch properties with filtering, pagination, and search
export async function fetchProperties(filters = {}) {
  try {
    let queryParams = new URLSearchParams();
    
    // Add filters to query params
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });
    
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await fetch(`${PROPERTY_URL}/?${queryParams.toString()}`, {
      headers
    });
    
    if (response.status === 401 && token) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${PROPERTY_URL}/?${queryParams.toString()}`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch properties');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch properties');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching properties:', error);
    throw error;
  }
}

// Fetch a single property by ID
export async function fetchPropertyById(id) {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await fetch(`${PROPERTY_URL}/${id}/`, {
      headers
    });
    
    if (response.status === 401 && token) {
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${PROPERTY_URL}/${id}/`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch property details');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch property details');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching property details:', error);
    throw error;
  }
}

// Fetch a property by slug
export async function fetchPropertyBySlug(slug) {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await fetch(`${PROPERTY_URL}/${slug}/`, {
      headers
    });
    
    if (response.status === 401 && token) {
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${PROPERTY_URL}/${slug}/`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch property details');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch property details');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching property details:', error);
    throw error;
  }
}

// Create a new property
export async function createProperty(propertyData) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      throw new Error('Authentication required');
    }

    // Format the data to match backend expectations
    const formattedData = {
      ...propertyData,
      property_type: propertyData.property_type?.id || propertyData.property_type,
      building_type: propertyData.building_type?.id || propertyData.building_type,
      rooms: Array.isArray(propertyData.rooms) ? propertyData.rooms.map(room => ({
        ...room,
        room_type: room.room_type?.id || room.room_type
      })) : [],
    };
    
    const response = await fetch(`${PROPERTY_URL}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(formattedData)
    });

    const data = await response.json();

    if (response.status === 401) {
      const newToken = await refreshToken();
      return createProperty(propertyData); // Retry with new token
    }

    if (!response.ok) {
      throw new Error(data.error?.message || 'Failed to create property');
    }

    return data;
  } catch (error) {
    console.error('Error creating property:', error);
    throw error;
  }
}

// Update a property
export async function updateProperty(id, propertyData) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      throw new Error('Authentication required');
    }

    const response = await fetch(`${PROPERTY_URL}/${id}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(propertyData)
    });

    if (response.status === 401) {
      const newToken = await refreshToken();
      return updateProperty(id, propertyData); // Retry with new token
    }

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error?.message || 'Failed to update property');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating property:', error);
    throw error;
  }
}

// Delete a property
export async function deleteProperty(id) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      throw new Error('Authentication required');
    }

    const response = await fetch(`${PROPERTY_URL}/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.status === 401) {
      const newToken = await refreshToken();
      return deleteProperty(id); // Retry with new token
    }

    if (!response.ok) {
      throw new Error('Failed to delete property');
    }

    return true;
  } catch (error) {
    console.error('Error deleting property:', error);
    throw error;
  }
}

// Upload property media
export async function uploadPropertyMedia(propertyId, file, isPrimary = false) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      throw new Error('Authentication required');
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('property', propertyId);
    formData.append('is_primary', isPrimary);
    formData.append('media_type', file.type.startsWith('image/') ? 'image' : 'document');

    const response = await fetch(`${MEDIA_URL}/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    if (response.status === 401) {
      const newToken = await refreshToken();
      return uploadPropertyMedia(propertyId, file, isPrimary); // Retry with new token
    }

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error?.message || 'Failed to upload media');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading media:', error);
    throw error;
  }
}

// Batch upload multiple media files
export async function uploadPropertyMediaBatch(propertyId, files, onProgress) {
  const results = [];
  let completed = 0;

  try {
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