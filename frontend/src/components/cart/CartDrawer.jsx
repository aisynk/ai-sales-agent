import React, { useEffect } from 'react';
import { X, ShoppingCart, Trash2, Plus, Minus } from 'lucide-react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import useStore from '../../store/useStore';
import { cartAPI } from '../../services/api';
import Button from '../common/Button';
import EmptyState from '../common/EmptyState';

const CartDrawer = () => {
  const navigate = useNavigate();
  const { 
    isCartOpen, 
    closeCart, 
    sessionId, 
    cart,
    cartCount,
    cartSubtotal,
    setCart,
    removeFromCart 
  } = useStore();

  // Fetch cart data
  const { data: cartData, refetch } = useQuery({
    queryKey: ['cart', sessionId],
    queryFn: () => cartAPI.get(sessionId),
    enabled: !!sessionId && isCartOpen,
  });

  useEffect(() => {
    if (cartData?.success) {
      setCart(cartData);
    }
  }, [cartData, setCart]);

  // Remove from cart mutation
  const removeItemMutation = useMutation({
    mutationFn: (productId) => cartAPI.remove(sessionId, productId),
    onSuccess: () => {
      refetch();
    },
  });

  // ✅ NEW: Update quantity mutation
  const updateQuantityMutation = useMutation({
    mutationFn: async ({ productId, newQuantity }) => {
      // Remove item first
      await cartAPI.remove(sessionId, productId);
      
      // Re-add with new quantity if > 0
      if (newQuantity > 0) {
        await cartAPI.add({
          session_id: sessionId,
          product_id: productId,
          quantity: newQuantity
        });
      }
    },
    onSuccess: () => {
      refetch(); // Refresh cart data
    },
  });

  // ✅ NEW: Handle quantity updates
  const handleUpdateQuantity = (productId, currentQuantity, change) => {
    const newQuantity = currentQuantity + change;
    if (newQuantity < 1) return;
    
    updateQuantityMutation.mutate({ productId, newQuantity });
  };

  const handleCheckout = () => {
    closeCart();
    navigate('/checkout');
  };

  if (!isCartOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 z-40 transition-opacity"
        onClick={closeCart}
      />

      {/* Drawer */}
      <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <ShoppingCart className="text-primary-600" size={24} />
            <h2 className="text-xl font-bold">Shopping Cart</h2>
            {cartCount > 0 && (
              <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded-full text-sm font-semibold">
                {cartCount}
              </span>
            )}
          </div>
          <button
            onClick={closeCart}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Cart items */}
        <div className="flex-1 overflow-y-auto p-6">
          {!cart || cart.length === 0 ? (
            <EmptyState
    icon="🛒"
    title="Your cart is empty"
    message="Add some products to get started!"
    actionLabel="Continue Shopping"
    onAction={closeCart}
  />
          ) : (
            <div className="space-y-4">
              {cart.map((item) => (
                <div key={item.product_id} className="flex space-x-4 p-4 bg-gray-50 rounded-lg">
                  {/* Product image */}
                  <div className="w-20 h-20 bg-gradient-to-br from-primary-50 to-secondary-50 rounded-lg flex items-center justify-center text-3xl flex-shrink-0">
                    👗
                  </div>

                  {/* Product details */}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-gray-800 truncate">
                      {item.name}
                    </h4>
                    <p className="text-sm text-gray-500">{item.brand}</p>
                    
                    {/* ✅ FIXED: Quantity controls now work */}
                    <div className="flex items-center space-x-2 mt-2">
                      <button 
                        onClick={() => handleUpdateQuantity(item.product_id, item.quantity, -1)}
                        className="p-1 hover:bg-gray-200 rounded disabled:opacity-50"
                        disabled={item.quantity <= 1 || updateQuantityMutation.isPending}
                      >
                        <Minus size={14} />
                      </button>
                      <span className="font-medium">{item.quantity}</span>
                      <button 
                        onClick={() => handleUpdateQuantity(item.product_id, item.quantity, 1)}
                        className="p-1 hover:bg-gray-200 rounded disabled:opacity-50"
                        disabled={updateQuantityMutation.isPending}
                      >
                        <Plus size={14} />
                      </button>
                    </div>
                  </div>

                  {/* Price & remove */}
                  <div className="flex flex-col items-end justify-between">
                    <button
                      onClick={() => {
                        removeFromCart(item.product_id);
                        removeItemMutation.mutate(item.product_id);
                      }}
                      className="text-red-500 hover:bg-red-50 p-1 rounded"
                    >
                      <Trash2 size={18} />
                    </button>
                    <div className="text-right">
                      <div className="font-bold text-primary-600">
                        ${item.subtotal || (item.price * item.quantity)}
                      </div>
                      <div className="text-xs text-gray-500">
                        ${item.price} each
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {cart && cart.length > 0 && (
          <div className="border-t p-6 space-y-4">
            {/* Subtotal */}
            <div className="flex justify-between items-center text-lg">
              <span className="font-semibold">Subtotal:</span>
              <span className="font-bold text-2xl text-primary-600">
                ${cartSubtotal.toFixed(2)}
              </span>
            </div>

            {/* Checkout button */}
            <Button 
              onClick={handleCheckout}
              className="w-full"
              size="lg"
            >
              Proceed to Checkout
            </Button>

            {/* Continue shopping */}
            <button
              onClick={closeCart}
              className="w-full text-center text-gray-600 hover:text-gray-800 text-sm"
            >
              Continue Shopping
            </button>
          </div>
        )}
      </div>
    </>
  );
};

export default CartDrawer;