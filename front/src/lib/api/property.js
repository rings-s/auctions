// src/lib/api/property.js
// import { PUBLIC_API_URL } from '$env/static/public';
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

// Define the PROPERTY_URL variable using API_BASE_URL
const PROPERTY_URL = `${API_BASE_URL}/properties`;


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

export async function createProperty(data) {
  try {
    const response = await fetch(`${PROPERTY_URL}/properties/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      },
      body: JSON.stringify(data)
    });

    const responseData = await response.json();

    if (!response.ok) {
      if (responseData.deed_number) {
        throw new Error(`Deed number: ${responseData.deed_number[0]}`);
      }
      const errors = Object.entries(responseData)
        .map(([key, value]) => `${key}: ${value.join(', ')}`)
        .join('; ');
      throw new Error(errors);
    }

    return { data: responseData };
  } catch (error) {
    console.error('Server error response:', error);
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


export async function uploadPropertyMedia(propertyId, file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('property', propertyId);

    const response = await fetch(`${MEDIA_URL}/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Failed to upload media');
    }

    return data;
  } catch (error) {
    console.error('Media upload error:', error);
    throw error;
  }
}

