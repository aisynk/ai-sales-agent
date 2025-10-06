import { useEffect } from 'react';

export const useKeyboardShortcut = (keys, callback) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      const keyMatch = keys.every(key => {
        if (key === 'ctrl') return event.ctrlKey || event.metaKey;
        if (key === 'shift') return event.shiftKey;
        if (key === 'alt') return event.altKey;
        return event.key.toLowerCase() === key.toLowerCase();
      });

      if (keyMatch) {
        event.preventDefault();
        callback(event);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [keys, callback]);
};