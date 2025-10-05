import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { CreditCard, Lock, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import useStore from '../store/useStore';
import { checkoutAPI, cartAPI, loyaltyAPI } from '../services/api';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Card from '../components/common/Card';

const CheckoutPage = () => {
  const navigate = useNavigate();
  const { sessionId, customerId, cart, clearCart } = useStore();
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [applyLoyalty, setApplyLoyalty] = useState(true);
  const [couponCode, setCouponCode] = useState('');
  const [orderComplete, setOrderComplete] = useState(false);
  const [orderData, setOrderData] = useState(null);

  // Fetch cart data
  const { data: cartData } = useQuery({
    queryKey: ['cart', sessionId],
    queryFn: () => cartAPI.get(sessionId),
    enabled: !!sessionId,
  });

  // Fetch loyalty info
  const { data: loyaltyData } = useQuery({
    queryKey: ['loyalty', customerId],
    queryFn: () => loyaltyAPI.getInfo(customerId),
    enabled: !!customerId,
  });

  // Checkout mutation
  const checkoutMutation = useMutation({
    mutationFn: (data) => checkoutAPI.process(data),
    onSuccess: (data) => {
      if (data.success) {
        setOrderData(data);
        setOrderComplete(true);
        clearCart();
      }
    },
  });

  const handleCheckout = (e) => {
    e.preventDefault();
    
    checkoutMutation.mutate({
      cart_items: cart.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
      })),
      customer_id: customerId,
      payment_method: paymentMethod,
      apply_loyalty: applyLoyalty,
      coupon_code: couponCode || undefined,
    });
  };

  if (orderComplete && orderData) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Confirmed!</h1>
          <p className="text-gray-600 mb-6">Thank you for your purchase</p>
          
          {orderData.order && (
            <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">Order ID:</span>
                <span className="font-mono font-semibold">{orderData.order.order_id}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">Total:</span>
                <span className="font-bold text-xl text-primary-600">
                  ${orderData.order.pricing.total}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Estimated Delivery:</span>
                <span className="font-medium">{orderData.order.estimated_delivery}</span>
              </div>
            </div>
          )}
          
          <div className="space-y-3">
            <Button onClick={() => navigate('/products')} className="w-full">
              Continue Shopping
            </Button>
            <Button variant="outline" onClick={() => navigate('/')} className="w-full">
              Back to Home
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!cart || cart.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="text-6xl mb-4">🛒</div>
        <h2 className="text-2xl font-bold mb-4">Your cart is empty</h2>
        <Button onClick={() => navigate('/products')}>
          Browse Products
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Checkout</h1>
      
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Checkout Form */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <h2 className="text-xl font-bold mb-4">Payment Method</h2>
            <div className="space-y-3">
              {[
                { id: 'card', label: 'Credit / Debit Card', icon: CreditCard },
                { id: 'paypal', label: 'PayPal' },
                { id: 'apple_pay', label: 'Apple Pay' },
              ].map((method) => (
                <label
                  key={method.id}
                  className={`
                    flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors
                    ${paymentMethod === method.id ? 'border-primary-500 bg-primary-50' : 'border-gray-200 hover:border-gray-300'}
                  `}
                >
                  <input
                    type="radio"
                    name="payment"
                    value={method.id}
                    checked={paymentMethod === method.id}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="mr-3"
                  />
                  {method.icon && <method.icon className="mr-2" size={20} />}
                  <span className="font-medium">{method.label}</span>
                </label>
              ))}
            </div>
          </Card>

          <Card>
            <h2 className="text-xl font-bold mb-4">Loyalty & Discounts</h2>
            
            {loyaltyData?.success && (
              <div className="mb-4 p-4 bg-primary-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold">Your Loyalty Points:</span>
                  <span className="text-2xl font-bold text-primary-600">
                    {loyaltyData.loyalty_points}
                  </span>
                </div>
                <label className="flex items-center mt-3">
                  <input
                    type="checkbox"
                    checked={applyLoyalty}
                    onChange={(e) => setApplyLoyalty(e.target.checked)}
                    className="mr-2"
                  />
                  <span className="text-sm">Use loyalty points (${loyaltyData.points_value} discount)</span>
                </label>
              </div>
            )}
            
            <Input
              placeholder="Enter coupon code"
              value={couponCode}
              onChange={(e) => setCouponCode(e.target.value)}
              label="Coupon Code"
            />
          </Card>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <Card className="sticky top-24">
            <h2 className="text-xl font-bold mb-4">Order Summary</h2>
            
            <div className="space-y-3 mb-4">
              {cartData?.success && cartData.cart.map((item) => (
                <div key={item.product_id} className="flex justify-between text-sm">
                  <span className="text-gray-600">{item.name} x{item.quantity}</span>
                  <span className="font-medium">${item.subtotal}</span>
                </div>
              ))}
            </div>
            
            <div className="border-t pt-4 space-y-2 mb-6">
              <div className="flex justify-between text-sm">
                <span>Subtotal:</span>
                <span>${cartData?.subtotal || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Tax:</span>
                <span>Calculated at checkout</span>
              </div>
              <div className="flex justify-between text-lg font-bold pt-2 border-t">
                <span>Total:</span>
                <span className="text-primary-600">${cartData?.subtotal || 0}</span>
              </div>
            </div>
            
            <Button
              onClick={handleCheckout}
              loading={checkoutMutation.isPending}
              className="w-full"
              size="lg"
            >
              <Lock size={20} className="mr-2" />
              Place Order
            </Button>
            
            <p className="text-xs text-center text-gray-500 mt-4">
              Your payment information is secure and encrypted
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;