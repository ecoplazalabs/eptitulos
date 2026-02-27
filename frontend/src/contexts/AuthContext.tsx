import { createContext, useCallback, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { TOKEN_KEY } from '@/services/api';
import { login, getMe } from '@/services/auth-service';
import type { User } from '@/types/auth';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount: restore session from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);

    if (!storedToken) {
      setIsLoading(false);
      return;
    }

    setToken(storedToken);
    getMe()
      .then((me) => {
        setUser(me);
      })
      .catch(() => {
        // Token invalid or expired — clear it
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const { token: newToken } = await login(email, password);
    localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
    const me = await getMe();
    setUser(me);
  }, []);

  const signOut = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: Boolean(user && token),
        signIn,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
