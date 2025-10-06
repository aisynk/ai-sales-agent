import React from 'react';
import { motion } from 'framer-motion';
import { Heart, ShoppingCart, Trash2 } from 'lucide-react';
import useStore from '../store/useStore';
import Button from '../components/common/Button';
import EmptyState from '../components/common/EmptyState';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { cartAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import Toast from '../components/common/Toast';

const WishlistPage = () => {
  const navigate = useNavigate();
  const { wishlist, removeFromWishlist, sessionId, addToCart } = useStore();
  const { toast, showToast, hideToast } = useToast();

  const addToCartMutation = useMutation({
    mutationFn: (product) => cartAPI.add({
      session_id: sessionId,
      product_id: product.product_id || product.id,
      quantity: 1,
    }),
    onSuccess: (data, product) => {
      if (data.success) {
        addToCart(product);
        showToast('Added to cart!', 'success');
      }
    },
    onError: () => {
      showToast('Failed to add to cart', 'error');
    },
  });

  const handleRemove = (productId) => {
    removeFromWishlist(productId);
    showToast('Removed from wishlist', 'info');
  };

  const handleAddToCart = (product) => {
    addToCartMutation.mutate(product);
  };

  if (wishlist.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="container mx-auto px-4 py-8"
      >
        <EmptyState
          icon="💝"
          title="Your wishlist is empty"
          message="Start adding products you love to your wishlist!"
          actionLabel="Browse Products"
          onAction={() => navigate('/products')}
        />
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="container mx-auto px-4 py-8"
    >
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <Heart className="text-red-500 fill-red-500" size={32} />
          <h1 className="text-3xl font-bold text-gray-900">My Wishlist</h1>
        </div>
        <p className="text-gray-600">
          {wishlist.length} {wishlist.length === 1 ? 'item' : 'items'} saved
        </p>
      </div>

      {/* Wishlist Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {wishlist.map((product) => (
          <motion.div
            key={product.product_id || product.id}
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow"
          >
            {/* Product Image */}
            <div className="relative h-64 bg-gradient-to-br from-primary-50 to-secondary-50">
              <div className="absolute inset-0 flex items-center justify-center text-7xl">
                👗
              </div>

              {/* Remove button */}
              <button
                onClick={() => handleRemove(product.product_id || product.id)}
                className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
              >
                <Trash2 size={18} className="text-red-500" />
              </button>

              {/* Discount badge */}
              {product.original_price && product.original_price > product.price && (
                <div className="absolute top-3 left-3 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                  {Math.round((1 - product.price / product.original_price) * 100)}% OFF
                </div>
              )}
            </div>

            {/* Product Details */}
            <div className="p-4">
              {/* Brand */}
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                {product.brand}
              </span>

              {/* Name */}
              <h3 className="font-semibold text-gray-800 mt-1 mb-2 line-clamp-2 h-12">
                {product.name}
              </h3>

              {/* Price */}
              <div className="flex items-center space-x-2 mb-4">
                <span className="text-2xl font-bold text-primary-600">
                  ${product.price}
                </span>
                {product.original_price && product.original_price > product.price && (
                  <span className="text-sm text-gray-400 line-through">
                    ${product.original_price}
                  </span>
                )}
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <Button
                  onClick={() => handleAddToCart(product)}
                  loading={addToCartMutation.isPending}
                  className="flex-1"
                  size="sm"
                >
                  <ShoppingCart size={16} className="mr-2" />
                  Add to Cart
                </Button>
              </div>

              {/* Stock status */}
              {product.in_stock !== undefined && (
                <div className="mt-3 text-center">
                  {product.in_stock !== false ? (
                    <span className="text-xs text-green-600 font-medium">✓ In Stock</span>
                  ) : (
                    <span className="text-xs text-red-600 font-medium">Out of Stock</span>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mt-8 flex justify-center space-x-4">
        <Button
          variant="outline"
          onClick={() => navigate('/products')}
        >
          Continue Shopping
        </Button>
        <Button
          variant="primary"
          onClick={() => {
            wishlist.forEach(product => handleAddToCart(product));
          }}
          loading={addToCartMutation.isPending}
        >
          Add All to Cart
        </Button>
      </div>

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />
    </motion.div>
  );
};

export default WishlistPage;