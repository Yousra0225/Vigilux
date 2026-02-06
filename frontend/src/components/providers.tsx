'use client';

import * as React from 'react';
import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { AuthProvider } from '@/context/AuthContext';
import { Toaster } from 'sonner';
import { NicheSelectionModal } from './NicheSelectionModal'; // Import the new component

export function Providers({ children, ...props }: React.ComponentProps<typeof NextThemesProvider>) {
  return (
    <NextThemesProvider {...props}>
      <AuthProvider>
        {children}
        <NicheSelectionModal /> {/* Add the NicheSelectionModal here */}
        <Toaster position="top-right" richColors closeButton />
      </AuthProvider>
    </NextThemesProvider>
  );
}
