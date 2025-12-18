// src/services/api.js
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://api.render.com/deploy/srv-d51kc6npm1nc73aj25b0?key=aWuLhp1Gg4g';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      await AsyncStorage.removeItem('token');
      await AsyncStorage.removeItem('user');
      // Redirect to login
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  verifyToken: () => api.get('/auth/verify'),
};

// Products API
export const productsAPI = {
  getAllProducts: (params) => api.get('/products', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
  createProduct: (productData) => api.post('/products', productData),
  updateProduct: (id, productData) => api.put(`/products/${id}`, productData),
  deleteProduct: (id) => api.delete(`/products/${id}`),
  searchProducts: (query) => api.get('/products/search', { params: { q: query } }),
};

// Orders API
export const ordersAPI = {
  createOrder: (orderData) => api.post('/orders', orderData),
  getOrders: (params) => api.get('/orders', { params }),
  getOrder: (id) => api.get(`/orders/${id}`),
  updateOrderStatus: (id, status) => api.patch(`/orders/${id}/status`, { status }),
  cancelOrder: (id) => api.post(`/orders/${id}/cancel`),
  rateOrder: (id, rating) => api.post(`/orders/${id}/rate`, { rating }),
};

// Cart API
export const cartAPI = {
  getCart: () => api.get('/cart'),
  addToCart: (productId, quantity) => api.post('/cart/items', { productId, quantity }),
  updateCartItem: (itemId, quantity) => api.put(`/cart/items/${itemId}`, { quantity }),
  removeFromCart: (itemId) => api.delete(`/cart/items/${itemId}`),
  clearCart: () => api.delete('/cart/clear'),
};

// Wallet API
export const walletAPI = {
  getBalance: () => api.get('/wallet/balance'),
  getTransactions: () => api.get('/wallet/transactions'),
  topup: (amount, method) => api.post('/wallet/topup', { amount, method }),
  withdraw: (amount, walletData) => api.post('/wallet/withdraw', { amount, ...walletData }),
  transfer: (amount, phone) => api.post('/wallet/transfer', { amount, phone }),
};

// Admin API
export const adminAPI = {
  // Users
  getUsers: (params) => api.get('/admin/users', { params }),
  getUser: (id) => api.get(`/admin/users/${id}`),
  updateUser: (id, userData) => api.put(`/admin/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
  
  // Markets
  getMarkets: () => api.get('/admin/markets'),
  createMarket: (marketData) => api.post('/admin/markets', marketData),
  updateMarket: (id, marketData) => api.put(`/admin/markets/${id}`, marketData),
  deleteMarket: (id) => api.delete(`/admin/markets/${id}`),
  
  // Washing Shops
  getWashingShops: () => api.get('/admin/washing-shops'),
  createWashingShop: (shopData) => api.post('/admin/washing-shops', shopData),
  
  // Drivers
  getDrivers: () => api.get('/admin/drivers'),
  createDriver: (driverData) => api.post('/admin/drivers', driverData),
  
  // Ads
  getAds: () => api.get('/admin/ads'),
  createAd: (adData) => api.post('/admin/ads', adData),
  
  // Statistics
  getStats: () => api.get('/admin/stats'),
  getReports: (params) => api.get('/admin/reports', { params }),
};

// Notifications API
export const notificationsAPI = {
  getNotifications: () => api.get('/notifications'),
  markAsRead: (id) => api.post(`/notifications/${id}/read`),
  sendNotification: (data) => api.post('/notifications/send', data),
};

export default api;
