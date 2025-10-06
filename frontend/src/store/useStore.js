import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useStore = create(
  persist(
    (set, get) => ({
      // Session
      sessionId: null,
      customerId: 1,
      currentChannel: 'web',
      
      // Cart
      cart: [],
      cartCount: 0,
      cartSubtotal: 0,
      isCartOpen: false,
      
      // Chat
      isChatOpen: false,
      
      // Wishlist
      wishlist: [],
      wishlistCount: 0,
      
      // Conversation
      conversationHistory: [],
conversationContext: {
  lastIntent: null,
  mentionedProducts: [],
  preferences: {},
},
      
      // Session actions
      setSessionId: (id) => set({ sessionId: id }),
      setSession: (sessionId, channel) => set({ 
        sessionId, 
        currentChannel: channel 
      }),
      
      // Chat actions
      openChat: () => set({ isChatOpen: true }),
      closeChat: () => set({ isChatOpen: false }),
      toggleChat: () => set((state) => ({ isChatOpen: !state.isChatOpen })),
      
      // Conversation actions
      addMessage: (message) => set((state) => ({
  conversationHistory: [...state.conversationHistory, {
    ...message,
    timestamp: new Date().toISOString()
  }]
})),
      
      clearConversation: () => set({
  conversationHistory: [],
  conversationContext: {
    lastIntent: null,
    mentionedProducts: [],
    preferences: {},
  }
}),
      
      updateContext: (context) => set((state) => ({
  conversationContext: {
    ...state.conversationContext,
    ...context
  }
})),
      
      // Wishlist actions
      addToWishlist: (product) => set((state) => {
        const productId = product.product_id || product.id;
        const exists = state.wishlist.find(
          item => (item.product_id || item.id) === productId
        );
        
        if (exists) {
          return {
            wishlist: state.wishlist.filter(
              item => (item.product_id || item.id) !== productId
            ),
            wishlistCount: state.wishlistCount - 1
          };
        } else {
          return {
            wishlist: [...state.wishlist, product],
            wishlistCount: state.wishlistCount + 1
          };
        }
      }),
      
      removeFromWishlist: (productId) => set((state) => ({
        wishlist: state.wishlist.filter(
          item => (item.product_id || item.id) !== productId
        ),
        wishlistCount: Math.max(0, state.wishlistCount - 1)
      })),
      
      // Cart actions
      addToCart: (productToAdd) => {
        set((state) => {
          const productId = productToAdd.product_id || productToAdd.id;
          const existingItem = state.cart.find(
            (item) => (item.product_id || item.id) === productId
          );

          let updatedCart;

          if (existingItem) {
            updatedCart = state.cart.map((item) =>
              (item.product_id || item.id) === productId
                ? { ...item, quantity: item.quantity + 1 }
                : item
            );
          } else {
            updatedCart = [...state.cart, { 
              ...productToAdd, 
              product_id: productId,
              id: productId,
              quantity: 1 
            }];
          }

          const newCount = updatedCart.length;
          const newSubtotal = updatedCart.reduce((sum, item) => 
            sum + (item.price * item.quantity), 0
          );

          return { 
            cart: updatedCart, 
            cartCount: newCount,
            cartSubtotal: newSubtotal
          };
        });
      },
      
      removeFromCart: (productId) => set((state) => {
        const newCart = state.cart.filter(
          item => (item.product_id || item.id) !== productId
        );
        return {
          cart: newCart,
          cartCount: newCart.length,
          cartSubtotal: newCart.reduce((sum, item) => 
            sum + (item.price * item.quantity), 0
          )
        };
      }),
      
      setCart: (cartData) => {
        const items = cartData.items || cartData.cart || [];
        const count = items.length;
        const subtotal = items.reduce((sum, item) => 
          sum + (item.price * item.quantity), 0
        );
        
        set({
          cart: items,
          cartCount: count,
          cartSubtotal: subtotal,
        });
      },
      
      clearCart: () => set({ 
        cart: [], 
        cartCount: 0, 
        cartSubtotal: 0 
      }),
      
      // Cart drawer
      openCart: () => set({ isCartOpen: true }),
      closeCart: () => set({ isCartOpen: false }),
      toggleCart: () => set((state) => ({ isCartOpen: !state.isCartOpen })),
    }),
    {
      name: 'ai-sales-agent-storage',
      partialize: (state) => ({
        sessionId: state.sessionId,
        customerId: state.customerId,
        cart: state.cart,
        cartCount: state.cartCount,
        cartSubtotal: state.cartSubtotal,
        wishlist: state.wishlist,
        wishlistCount: state.wishlistCount,
        conversationHistory: state.conversationHistory,
        conversationContext: state.conversationContext,
      }),
    }
  )
);

export default useStore;