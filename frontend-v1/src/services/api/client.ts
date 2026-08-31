export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = async (endpoint: string, options: RequestInit = {}) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `API Error: ${response.status}`);
  }

  return response.status === 204 ? null : response.json();
};

export const api = {
  get: (url: string) => apiClient(url, { method: 'GET' }),
  post: (url: string, data: any) => apiClient(url, { method: 'POST', body: JSON.stringify(data) }),
  put: (url: string, data: any) => apiClient(url, { method: 'PUT', body: JSON.stringify(data) }),
  patch: (url: string, data: any) => apiClient(url, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (url: string) => apiClient(url, { method: 'DELETE' }),
};
