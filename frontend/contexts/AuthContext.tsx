import React, { createContext, useContext, ReactNode, useEffect, useState } from 'react';
import { useRouter } from 'next/router';

// Define the user interface
interface User {
  id: string;
  email: string;
  name?: string;
  image?: string;
}

// Define the auth context type
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

// This AuthProvider is designed to work with NextAuth's SessionProvider
// It uses dynamic imports to access NextAuth functions without violating hook rules
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authState, setAuthState] = useState<{
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
  }>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const [authFunctions, setAuthFunctions] = useState<{
    signIn: any;
    signOut: any;
    getSession: any;
  } | null>(null);

  const router = useRouter();

  // Initialize NextAuth functions dynamically
  useEffect(() => {
    const initAuth = async () => {
      if (typeof window !== 'undefined') {
        const nextAuthModule: any = await import('next-auth/react');

        // Store the functions - using any to bypass TypeScript checking
        setAuthFunctions({
          signIn: nextAuthModule.default?.signIn || nextAuthModule.signIn,
          signOut: nextAuthModule.default?.signOut || nextAuthModule.signOut,
          getSession: nextAuthModule.default?.getSession || nextAuthModule.getSession,
        });
        
        // Update session immediately after loading the functions
        const session = await (nextAuthModule.default?.getSession || nextAuthModule.getSession)();
        setAuthState({
          user: session?.user ? {
            id: session.user.id as string,
            email: session.user.email!,
            name: session.user.name || undefined,
            image: session.user.image || undefined,
          } : null,
          isAuthenticated: !!session?.user,
          isLoading: false,
        });
      }
    };

    initAuth();
  }, []);

  // Set up a listener for session changes
  useEffect(() => {
    if (typeof window !== 'undefined' && authFunctions?.getSession) {
      // Listen for session updates
      const handleStorageChange = () => {
        const updateSession = async () => {
          const session = await authFunctions.getSession();
          setAuthState({
            user: session?.user ? {
              id: session.user.id as string,
              email: session.user.email!,
              name: session.user.name || undefined,
              image: session.user.image || undefined,
            } : null,
            isAuthenticated: !!session?.user,
            isLoading: false,
          });
        };
        updateSession();
      };

      window.addEventListener('storage', handleStorageChange);
      window.addEventListener('focus', handleStorageChange);

      return () => {
        window.removeEventListener('storage', handleStorageChange);
        window.removeEventListener('focus', handleStorageChange);
      };
    }
  }, [authFunctions]);

  const login = async (email: string, password: string) => {
    if (!authFunctions?.signIn) {
      throw new Error('Authentication functions not loaded');
    }

    const result = await authFunctions.signIn('credentials', {
      email,
      password,
      redirect: false,
    });

    if (result?.error) {
      throw new Error(result.error);
    }

    if (result?.ok) {
      router.push('/dashboard'); // ✅ Login redirects to dashboard
    }
  };

  const signup = async (email: string, password: string) => {
    if (!authFunctions?.signIn) {
      throw new Error('Authentication functions not loaded');
    }

    try {
      // Create the user account via backend API
      const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; // TODO: Replace with your actual backend URL
      const response = await fetch(`${BACKEND_API_URL}/api/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.message || 'Signup failed');
      }

      // After successful signup, log them in
      const result = await authFunctions.signIn('credentials', {
        email,
        password,
        redirect: false,
      });

      if (result?.error) {
        throw new Error('Account created but login failed. Please try logging in.');
      }

      if (result?.ok) {
        router.push('/dashboard'); // ✅ Signup also redirects to dashboard
      }
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  };

  const loginWithGoogle = async () => {
    if (!authFunctions?.signIn) {
      throw new Error('Authentication functions not loaded');
    }

    await authFunctions.signIn('google', { callbackUrl: '/dashboard' }); // ✅ Google login also goes to dashboard
  };

  const logout = async () => {
    if (!authFunctions?.signOut) {
      throw new Error('Authentication functions not loaded');
    }

    await authFunctions.signOut({ callbackUrl: '/login' });
  };

  const value = {
    user: authState.user,
    login,
    signup,
    loginWithGoogle,
    logout,
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};