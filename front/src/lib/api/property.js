// src/lib/api/property.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';


const PROPERTY_URL = 'http://localhost:8000/api/properties';

// Fetch properties with filtering, pagination, and search
export async function fetchProperties(filters = {}) {
  let queryParams = new URLSearchParams();
  
  // Add filters to query params
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value);
    }
  });
  
  try {
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

export async function fetchPropertyById(id) {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await fetch(`${PROPERTY_URL}/${id}/`, {
      headers
    });
    
    if (response.status === 401 && token) {
      // Try to refresh token and retry
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
    
    const response = await fetch(`${PROPERTY_URL}/slug/${slug}/`, {
      headers
    });
    
    if (response.status === 401 && token) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${PROPERTY_URL}/slug/${slug}/`, {
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
// In front/src/lib/api/property.js
export async function createProperty(propertyData) {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    const response = await fetch('http://localhost:8000/api/properties/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(propertyData)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error?.message || data.error || 'Failed to create property');
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
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${PROPERTY_URL}/${id}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(propertyData)
      });
      
      if (!retryResponse.ok) {
        const errorData = await retryResponse.json();
        throw new Error(errorData.error?.message || 'Failed to update property');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'Failed to update property');
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
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${PROPERTY_URL}/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${newToken}`
        }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to delete property');
      }
      
      return true;
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



export async function uploadPropertyMedia(propertyId, mediaFile, mediaType = 'image') {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', mediaFile);
    formData.append('media_type', mediaType);
    formData.append('content_type', 'base.property'); 
    formData.append('object_id', propertyId);
    
    // Log what we're uploading
    console.log(`Uploading file for property ${propertyId}:`, {
      fileName: mediaFile.name,
      fileType: mediaFile.type,
      fileSize: mediaFile.size,
      mediaType: mediaType
    });
    
    // Use the correct API endpoint
    const response = await fetch('http://localhost:8000/api/media/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    // Get response data
    let data;
    const contentType = response.headers.get("content-type");
    
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      const text = await response.text();
      console.error("Non-JSON response from media upload:", text);
      throw new Error(`Server returned non-JSON response (${response.status})`);
    }
    
    // Handle error responses
    if (!response.ok) {
      console.error("Error uploading media:", data);
      
      if (data.error) {
        throw new Error(typeof data.error === 'object' ? JSON.stringify(data.error) : data.error.message || data.error);
      } else if (data.detail) {
        throw new Error(data.detail);
      } else {
        throw new Error('Failed to upload media');
      }
    }
    
    console.log("Media upload successful:", data);
    return data;
  } catch (error) {
    console.error('Error uploading media:', error);
    throw error;
  }
}