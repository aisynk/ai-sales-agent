import axios from 'axios';

// ============================================
// CONFIGURATION
// ============================================

// Your backend server address
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default settings
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // Wait max 30 seconds for response
});

// ============================================
// INTERCEPTORS (Middleware)
// ============================================

// Runs BEFORE every request
api.interceptors.request.use(
  (config) => {
    // You could add authentication tokens here
    // config.headers.Authorization = `Bearer ${token}`;
    console.log('Making request to:', config.url);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Runs AFTER every response
api.interceptors.response.use(
  (response) => {
    // Return just the data part (not the full axios response)
    return response.data;
  },
  (error) => {
    console.error('Response error:', error);
    return Promise.reject(error);
  }
);

// ============================================
// SESSION API CALLS
// ============================================

export const sessionAPI = {
  // Create a new session
  create: (customerId, channel = 'web') => 
    api.post('/session/create', null, { 
      params: { customer_id: customerId, channel } 
    }),
  
  // Get session details
  get: (sessionId) => 
    api.get(`/session/${sessionId}`),
  
  // Switch to different channel (web -> whatsapp -> kiosk)
  switchChannel: (sessionId, newChannel) => 
    api.post('/session/switch-channel', null, { 
      params: { session_id: sessionId, new_channel: newChannel } 
    }),
};

// ============================================
// CHAT API CALLS
// ============================================

export const chatAPI = {
  // Send message to AI
  sendMessage: (data) => 
    api.post('/channel-chat', null, { params: data }),
};

// ============================================
// CART API CALLS
// ============================================

export const cartAPI = {
  // Get cart contents
  get: (sessionId) => 
    api.get(`/cart/${sessionId}`),
  
  // Add item to cart
  add: (data) => 
    api.post('/cart/add', data),
  
  // Remove item from cart
  remove: (sessionId, productId) => 
    api.post('/cart/remove', null, { 
      params: { session_id: sessionId, product_id: productId } 
    }),
};

// ============================================
// PRODUCTS API CALLS
// ============================================

export const productsAPI = {
  // Get all products
  getAll: () => 
    api.get('/products'),
  
  // Search products with filters
  search: (params) => 
    api.post('/products/search', params),
  
  // Get filter options (categories, brands, etc.)
  getFilters: () => 
    api.get('/products/filters'),
};

// ============================================
// RECOMMENDATIONS API CALLS
// ============================================

export const recommendationsAPI = {
  // Get AI product recommendations
  get: (params) => 
    api.post('/recommendations', null, { params }),
};

// ============================================
// CHECKOUT API CALLS
// ============================================

export const checkoutAPI = {
  // Process payment
  process: (data) => 
    api.post('/checkout', data),
};

// ============================================
// LOYALTY API CALLS
// ============================================

export const loyaltyAPI = {
  // Get loyalty info
  getInfo: (customerId) => 
    api.get(`/loyalty/${customerId}`),
  
  // Get personalized offers
  getOffers: (customerId) => 
    api.get(`/loyalty/${customerId}/offers`),
};

export default api;