import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AnimatePresence } from 'framer-motion'; 
import WishlistPage from './pages/WishlistPage';
// Pages
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import ProductsPage from './pages/ProductsPage';
import CheckoutPage from './pages/CheckoutPage';

// Layout components
import Header from './components/common/Header';
import ChatWidget from './components/chat/ChatWidget';
import CartDrawer from './components/cart/CartDrawer'; // ✅ Added import

// Create query client for react-query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AnimatedRoutes() {
  const location = useLocation();
  
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/wishlist" element={<WishlistPage />} /> {/* ADD THIS */}
        <Route path="/checkout" element={<CheckoutPage />} />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main>
            <AnimatedRoutes />
          </main>
          <ChatWidget />
          <CartDrawer />
        </div>
      </Router>
    </QueryClientProvider>
  );
}
export default App;
