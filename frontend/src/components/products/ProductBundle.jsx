import React from 'react';
import { ShoppingCart, Tag } from 'lucide-react';
import Button from '../common/Button';
import { useMutation } from '@tanstack/react-query';
import { cartAPI } from '../../services/api';
import useStore from '../../store/useStore';
import { motion } from 'framer-motion';

const ProductBundle = ({ products, discount = 10 }) => {
  const { sessionId, addToCart } = useStore();

  const totalPrice = products.reduce((sum, p) => sum + p.price, 0);
  const bundlePrice = totalPrice * (1 - discount / 100);
  const savings = totalPrice - bundlePrice;

  const addBundleMutation = useMutation({
    mutationFn: async () => {
      const promises = products.map(product =>
        cartAPI.add({
          session_id: sessionId,
          product_id: product.product_id || product.id,
          quantity: 1,
        })
      );
      return Promise.all(promises);
    },
    onSuccess: () => {
      products.forEach(product => addToCart(product));
    },
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-4 my-4"
    >
      <div className="flex items-center space-x-2 mb-3">
        <Tag className="text-green-600" size={20} />
        <h3 className="font-bold text-green-800">Bundle Deal - Save {discount}%!</h3>
      </div>

      <div className="space-y-2 mb-4">
        {products.map((product, index) => (
          <div key={index} className="flex items-center justify-between text-sm">
            <span className="text-gray-700">{product.name}</span>
            <span className="text-gray-500 line-through">${product.price}</span>
          </div>
        ))}
      </div>

      <div className="border-t border-green-200 pt-3 mt-3">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-sm text-gray-600">
              Regular: <span className="line-through">${totalPrice.toFixed(2)}</span>
            </div>
            <div className="text-lg font-bold text-green-600">
              Bundle: ${bundlePrice.toFixed(2)}
            </div>
            <div className="text-xs text-green-600">
              You save ${savings.toFixed(2)}!
            </div>
          </div>
        </div>

        <Button
          onClick={() => addBundleMutation.mutate()}
          loading={addBundleMutation.isPending}
          className="w-full bg-green-600 hover:bg-green-700"
        >
          <ShoppingCart size={16} className="mr-2" />
          Add Bundle to Cart
        </Button>
      </div>
    </motion.div>
  );
};

export default ProductBundle;