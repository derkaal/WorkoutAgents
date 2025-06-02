import React, { createContext, useState, ReactNode } from 'react';

// Define the shape of the context value
interface BriefingContextType {
  briefing: object | string | null;
  setBriefing: (briefing: object | string | null) => void;
}

// Create the context with a default value
export const BriefingContext = createContext<BriefingContextType>({
  briefing: null,
  setBriefing: () => {},
});

// Props for the BriefingProvider component
interface BriefingProviderProps {
  children: ReactNode;
}

// Create the BriefingProvider component
export const BriefingProvider: React.FC<BriefingProviderProps> = ({ children }) => {
  // State to hold the briefing
  const [briefing, setBriefing] = useState<object | string | null>(null);

  // Value to be provided by the context
  const value = {
    briefing,
    setBriefing,
  };

  return (
    <BriefingContext.Provider value={value}>
      {children}
    </BriefingContext.Provider>
  );
};