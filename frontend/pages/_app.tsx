import React from 'react';
import type { AppProps } from 'next/app';
import { AuthProvider } from '../contexts/AuthContext';
import { TaskProvider } from '../contexts/TaskContext';
import '../styles/globals.css';

// Dynamic import for SessionProvider to handle potential runtime issues in Vercel
const AppWrapper = ({ Component, pageProps }: AppProps) => {
  const { session, ...restPageProps } = pageProps;

  // Dynamically import next-auth at runtime
  let SessionProvider: any;
  try {
    // Try to get SessionProvider from next-auth
    const NextAuthModule = require('next-auth/react');
    SessionProvider = NextAuthModule.SessionProvider;
  } catch (error) {
    // If next-auth is not available, use a fallback component
    SessionProvider = ({ children }: { children: React.ReactNode }) => <>{children}</>;
  }

  // If SessionProvider is not a function, use fallback
  if (typeof SessionProvider !== 'function') {
    SessionProvider = ({ children }: { children: React.ReactNode }) => <>{children}</>;
  }

  return (
    <SessionProvider session={session}>
      <AuthProvider>
        <TaskProvider>
          <Component {...restPageProps} />
        </TaskProvider>
      </AuthProvider>
    </SessionProvider>
  );
};

export default AppWrapper;