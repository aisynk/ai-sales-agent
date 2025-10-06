import React from 'react';
import Button from './Button';

const EmptyState = ({ 
  icon = '📦', 
  title, 
  message, 
  actionLabel, 
  onAction 
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="text-8xl mb-6">{icon}</div>
      <h3 className="text-2xl font-bold text-gray-800 mb-3">{title}</h3>
      <p className="text-gray-600 text-center max-w-md mb-8">{message}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} size="lg">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;