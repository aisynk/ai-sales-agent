import React, { useState } from 'react';
import { X, ShoppingCart, Star, Heart, Minus, Plus } from 'lucide-react';
import Button from '../common/Button';
import { useMutation } from '@tanstack/react-query';
import { cartAPI } from '../../services/api';
import useStore from '../../store/useStore';
import { useToast } from '../../hooks/useToast';
import Toast from '../common/Toast';

const ProductModal = ({ product, isOpen, onClose }) => {
  const { sessionId, addToCart, addToWishlist, wishlist } = useStore();
  const { toast, showToast, hideToast } = useToast();
  const [quantity, setQuantity] = useState(1);

  // Check if in wishlist
  const isInWishlist = wishlist.some(
    item => (item.product_id || item.id) === (product.product_id || product.id)
  );

  const addToCartMutation = useMutation({
    mutationFn: () => cartAPI.add({
      session_id: sessionId,
      product_id: product.id || product.product_id,
      quantity: quantity,
    }),
    onSuccess: (data) => {
      if (data.success) {
        for (let i = 0; i < quantity; i++) {
          addToCart(product);
        }
        onClose();
      }
    },
  });

  const handleWishlistToggle = () => {
    addToWishlist(product);
    if (isInWishlist) {
      showToast('Removed from wishlist', 'info');
    } else {
      showToast('Added to wishlist!', 'success');
    }
  };

  if (!isOpen || !product) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 z-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
            <h2 className="text-2xl font-bold">{product.name}</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X size={24} />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 grid md:grid-cols-2 gap-8">
            {/* Image */}
            <div className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl flex items-center justify-center h-96">
              <div className="text-9xl">👗</div>
            </div>

            {/* Details */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                  {product.brand}
                </span>
                {product.rating && (
                  <div className="flex items-center space-x-1">
                    <Star size={16} className="text-yellow-400 fill-current" />
                    <span className="font-medium">{product.rating}</span>
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-3 mb-6">
                <span className="text-4xl font-bold text-primary-600">
                  ${product.price}
                </span>
                {product.original_price && product.original_price > product.price && (
                  <>
                    <span className="text-xl text-gray-400 line-through">
                      ${product.original_price}
                    </span>
                    <span className="bg-red-500 text-white px-2 py-1 rounded-full text-sm font-bold">
                      {Math.round((1 - product.price / product.original_price) * 100)}% OFF
                    </span>
                  </>
                )}
              </div>

              <p className="text-gray-700 mb-6">
                {product.description || `${product.name} - Premium quality product designed for your comfort and style. Perfect for any occasion.`}
              </p>

              <div className="space-y-4 mb-6 bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between">
                  <span className="text-gray-600">Category:</span>
                  <span className="font-medium">{product.category}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Brand:</span>
                  <span className="font-medium">{product.brand}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Availability:</span>
                  <span className={`font-medium ${product.in_stock !== false ? 'text-green-600' : 'text-red-600'}`}>
                    {product.in_stock !== false ? 'In Stock' : 'Out of Stock'}
                  </span>
                </div>
              </div>

              {/* Quantity selector */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quantity
                </label>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    disabled={quantity <= 1}
                  >
                    <Minus size={20} />
                  </button>
                  <span className="text-2xl font-bold w-12 text-center">{quantity}</span>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    <Plus size={20} />
                  </button>
                </div>
              </div>

              <div className="flex space-x-3">
    <Button
      onClick={() => addToCartMutation.mutate()}
      loading={addToCartMutation.isPending}
      className="flex-1"
      size="lg"
    >
      <ShoppingCart size={20} className="mr-2" />
      Add to Cart
    </Button>
    <Button 
      variant={isInWishlist ? "primary" : "outline"}
      size="lg" 
      className="px-6"
      onClick={handleWishlistToggle}
    >
      <Heart 
        size={20} 
        className={isInWishlist ? "fill-current" : ""}
      />
    </Button>
  </div>
            </div>
          </div>
        </div>
      </div>
      <Toast
    message={toast.message}
    type={toast.type}
    isVisible={toast.isVisible}
    onClose={hideToast}
  />
    </>
  );
};

export default ProductModal;