import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

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

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/checkout" element={<CheckoutPage />} />
            </Routes>
          </main>
          <ChatWidget />
          <CartDrawer /> {/* ✅ Added CartDrawer after ChatWidget */}
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
