import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('Making request to:', config.url);
    console.log('Request data:', config.data);
    console.log('Request params:', config.params);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('Response error:', error);
    console.error('Error details:', error.response?.data);
    return Promise.reject(error);
  }
);

// ============================================
// API ENDPOINTS
// ============================================

// SESSION API
export const sessionAPI = {
  create: (customerId, channel = 'web') => 
    api.post('/session/create', null, { 
      params: { customer_id: customerId, channel } 
    }),
  
  get: (sessionId) => 
    api.get(`/session/${sessionId}`),
};

// CHAT API - Query params format (what your backend expects)
export const chatAPI = {
  sendMessage: (sessionId, message, channel = 'web') => {
    console.log('=== CHAT API DEBUG ===');
    console.log('SessionID:', sessionId);
    console.log('Message:', message);
    console.log('Channel:', channel);
    
    // Send as query parameters, NOT body
    return api.post('/channel-chat', null, {
      params: {
        message: message,
        channel: channel,
        session_id: sessionId,
      }
    });
  },
};

// CART API
export const cartAPI = {
  get: (sessionId) => 
    api.get(`/cart/${sessionId}`),
  
  add: (data) => 
    api.post('/cart/add', data),
  
  remove: (sessionId, productId) => 
    api.post('/cart/remove', null, { 
      params: { session_id: sessionId, product_id: productId } 
    }),
};

// PRODUCTS API
export const productsAPI = {
  getAll: () => 
    api.get('/products'),
  
  search: (params) => 
    api.post('/products/search', params),
  
  getFilters: () => 
    api.get('/products/filters'),
};

// RECOMMENDATIONS API
export const recommendationsAPI = {
  get: (params) => 
    api.post('/recommendations', null, { params }),
};

// CHECKOUT API
export const checkoutAPI = {
  process: (data) => 
    api.post('/checkout', data),
};

// LOYALTY API
export const loyaltyAPI = {
  getInfo: (customerId) => 
    api.get(`/loyalty/${customerId}`),
  
  getOffers: (customerId) => 
    api.get(`/loyalty/${customerId}/offers`),
};

export default api;