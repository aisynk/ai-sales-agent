import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import useStore from '../../store/useStore';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingCart, Menu, X, Home, ShoppingBag, MessageSquare, Heart } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const location = useLocation();
  const { cartCount, toggleChat, openCart } = useStore();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const { toggleCart, wishlistCount } = useStore();
  const navigate = useNavigate();

const navigation = [
  { name: 'Home', path: '/', icon: Home },
  { name: 'Products', path: '/products', icon: ShoppingBag },
  { name: 'Wishlist', path: '/wishlist', icon: Heart }, // ADD THIS
  { name: 'Chat', path: '/chat', icon: MessageSquare },
];
  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-2xl">🤖</div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">
              AI Sales Agent
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  px-3 py-2 rounded-md text-sm font-medium transition-colors
                  ${isActive(item.path)
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                  }
                `}
              >
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            {/* Chat button */}
            <button
              onClick={toggleChat}
              className="p-2 text-gray-600 hover:text-primary-600 hover:bg-gray-100 rounded-full transition-colors"
              aria-label="Open chat"
            >
              <MessageSquare size={24} />
            </button>

            {/* Wishlist */}
<button 
  onClick={() => navigate('/wishlist')}
  className="relative p-2 text-gray-700 hover:text-primary-600 transition-colors"
>
  <Heart size={24} />
  {wishlistCount > 0 && (
    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
      {wishlistCount}
    </span>
  )}
</button>

            {/* Cart button with badge */}
            <button
              onClick={openCart}
              className="relative p-2 text-gray-600 hover:text-primary-600 hover:bg-gray-100 rounded-full transition-colors"
              aria-label="View cart"
            >
              <ShoppingCart size={24} />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </button>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-gray-600 hover:text-primary-600 hover:bg-gray-100 rounded-md"
              aria-label="Toggle menu"
            >
              <Menu size={24} />
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
{/* Mobile Navigation */}
<AnimatePresence>
  {mobileMenuOpen && (
    <motion.div 
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
      className="md:hidden border-t bg-white"
    >
      <div className="py-2 space-y-1">
        {navigation.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            onClick={() => setMobileMenuOpen(false)}
            className={`
              block px-4 py-3 text-base font-medium transition-colors
              ${isActive(item.path)
                ? 'text-primary-600 bg-primary-50 border-l-4 border-primary-600'
                : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
              }
            `}
          >
            <div className="flex items-center space-x-3">
              <item.icon size={20} />
              <span>{item.name}</span>
            </div>
          </Link>
        ))}
      </div>
    </motion.div>
  )}
</AnimatePresence>
      </div>
    </header>
  );
};

export default Header;