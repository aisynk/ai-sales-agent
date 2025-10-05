import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useStore = create(
  persist(
    (set, get) => ({
      // Session state
      sessionId: null,
      currentChannel: 'web',
      customerId: 1, // Demo customer
      
      setSession: (sessionId, channel = 'web') => 
        set({ sessionId, currentChannel: channel }),
      
      setChannel: (channel) => 
        set({ currentChannel: channel }),
      
      // Cart state
      cart: [],
      cartCount: 0,
      cartSubtotal: 0,
      
      setCart: (cartData) => 
        set({
          cart: cartData.cart || [],
          cartCount: cartData.cart_count || 0,
          cartSubtotal: cartData.subtotal || 0,
        }),
      
      addToCart: (productToAdd) => {
    set((state) => {
      const existingItem = state.cart.find(
        (item) => item.product_id === productToAdd.product_id
      );

      let updatedCart;

      if (existingItem) {
        // If item exists, map over the cart and update the quantity of the matching item
        updatedCart = state.cart.map((item) =>
          item.product_id === productToAdd.product_id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        // If item does not exist, add it to the cart with quantity 1
        updatedCart = [...state.cart, { ...productToAdd, quantity: 1 }];
      }

      return { cart: updatedCart };
    });
  },
      
      removeFromCart: (productId) => 
        set((state) => ({
          cart: state.cart.filter(item => item.product_id !== productId),
          cartCount: Math.max(0, state.cartCount - 1),
        })),
      
      clearCart: () => 
        set({ cart: [], cartCount: 0, cartSubtotal: 0 }),
      
      // Customer info
      customerInfo: null,
      
      setCustomerInfo: (info) => 
        set({ customerInfo: info }),
      
      // UI state
      isChatOpen: false,
      isCartOpen: false,
      
      toggleChat: () => 
        set((state) => ({ isChatOpen: !state.isChatOpen })),
      
      toggleCart: () => 
        set((state) => ({ isCartOpen: !state.isCartOpen })),
      
      openChat: () => 
        set({ isChatOpen: true }),
      
      closeChat: () => 
        set({ isChatOpen: false }),
      
      openCart: () => 
        set({ isCartOpen: true }),
      
      closeCart: () => 
        set({ isCartOpen: false }),
    }),
    {
      name: 'ai-sales-agent-storage', // LocalStorage key
      partialize: (state) => ({
        sessionId: state.sessionId,
        customerId: state.customerId,
        cart: state.cart,
      }),
    }
  )
);

export default useStore;