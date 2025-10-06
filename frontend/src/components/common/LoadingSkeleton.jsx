import React from 'react';

export const ProductCardSkeleton = () => (
  <div className="bg-white rounded-xl shadow-md overflow-hidden animate-pulse">
    <div className="bg-gray-200 h-64"></div>
    <div className="p-4">
      <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
      <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
      <div className="h-10 bg-gray-200 rounded"></div>
    </div>
  </div>
);

export const ChatMessageSkeleton = () => (
  <div className="flex justify-start animate-pulse">
    <div className="max-w-[80%]">
      <div className="flex items-center space-x-2 mb-2">
        <div className="w-8 h-8 rounded-full bg-gray-200"></div>
        <div className="h-4 bg-gray-200 rounded w-20"></div>
      </div>
      <div className="bg-gray-100 p-3 rounded-2xl rounded-tl-none">
        <div className="h-4 bg-gray-200 rounded w-48 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-36"></div>
      </div>
    </div>
  </div>
);

export const CartItemSkeleton = () => (
  <div className="flex space-x-4 p-4 bg-gray-50 rounded-lg animate-pulse">
    <div className="w-20 h-20 bg-gray-200 rounded-lg flex-shrink-0"></div>
    <div className="flex-1">
      <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
      <div className="h-6 bg-gray-200 rounded w-20"></div>
    </div>
  </div>
);