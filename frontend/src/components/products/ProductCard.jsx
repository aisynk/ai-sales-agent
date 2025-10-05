import React from 'react';
import { ShoppingCart, Star, Heart } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import useStore from '../../store/useStore';
import { cartAPI } from '../../services/api';
import Button from '../common/Button';

const ProductCard = ({ product, compact = false }) => {
  const { sessionId, addToCart } = useStore();

  const addToCartMutation = useMutation({
    mutationFn: () => cartAPI.add({
      session_id: sessionId,
      product_id: product.product_id || product.id,
      quantity: 1,
    }),
    onSuccess: (data) => {
      if (data.success) {
        addToCart(product);
      }
    },
  });

  if (compact) {
    return (
      <div className="flex items-center space-x-3 p-3 bg-white rounded-lg border hover:shadow-md transition-shadow">
        <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center text-2xl">
          👗
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-sm truncate">{product.name}</h4>
          <p className="text-xs text-gray-500">{product.brand}</p>
          <div className="flex items-center justify-between mt-1">
            <span className="text-primary-600 font-bold">${product.price}</span>
            <button
              onClick={() => addToCartMutation.mutate()}
              disabled={addToCartMutation.isPending}
              className="p-1 text-primary-600 hover:bg-primary-50 rounded"
            >
              <ShoppingCart size={16} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 group">
      {/* Image */}
      <div className="relative h-64 bg-gradient-to-br from-primary-50 to-secondary-50 overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center text-7xl">
          👗
        </div>
        
        {/* Wishlist button */}
        <button className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity">
          <Heart size={20} className="text-gray-600 hover:text-red-500" />
        </button>

        {/* Badge */}
        {product.original_price && product.original_price > product.price && (
          <div className="absolute top-3 left-3 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
            {Math.round((1 - product.price / product.original_price) * 100)}% OFF
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Brand & Category */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            {product.brand}
          </span>
          {product.rating && (
            <div className="flex items-center space-x-1">
              <Star size={14} className="text-yellow-400 fill-current" />
              <span className="text-sm font-medium">{product.rating}</span>
            </div>
          )}
        </div>

        {/* Product name */}
        <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2 h-12">
          {product.name}
        </h3>

        {/* Reason/Description */}
        {product.reason && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {product.reason}
          </p>
        )}

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
            onClick={() => addToCartMutation.mutate()}
            loading={addToCartMutation.isPending}
            className="flex-1"
            size="sm"
          >
            <ShoppingCart size={16} className="mr-2" />
            Add to Cart
          </Button>
          <Button variant="outline" size="sm" className="px-4">
            View
          </Button>
        </div>

        {/* Stock status */}
        {product.in_stock !== undefined && (
          <div className="mt-3 text-center">
            {product.in_stock ? (
              <span className="text-xs text-green-600 font-medium">✓ In Stock</span>
            ) : (
              <span className="text-xs text-red-600 font-medium">Out of Stock</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductCard;