import { AuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";

// Define the User interface to match your backend response
interface BackendUserResponse {
  id: string;
  email: string;
  name?: string | null;
  access_token: string;
  refresh_token: string;
}

// Define the NextAuth options
export const authOptions: AuthOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          console.error("Missing email or password in credentials");
          return null;
        }

        try {
          // Authenticate against the backend API - REPLACE WITH YOUR ACTUAL BACKEND URL
          const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; // TODO: Replace with your actual backend URL
          console.log(`Attempting to authenticate user: ${credentials.email} at ${BACKEND_API_URL}/api/login`);

          const response = await fetch(`${BACKEND_API_URL}/api/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          });

          console.log(`Backend response status: ${response.status}`);

          if (!response.ok) {
            const errorText = await response.text(); // Get the raw error response
            console.error("Backend authentication failed:", errorText);

            // Try to parse as JSON if possible, otherwise log as text
            try {
              const errorData = JSON.parse(errorText);
              console.error("Parsed error data:", errorData);
            } catch (parseError) {
              console.error("Could not parse error as JSON:", errorText);
            }

            return null;
          }

          const userData: BackendUserResponse = await response.json();
          console.log("Successfully authenticated user:", userData.email);

          // Return user data for the session, including the access and refresh tokens
          return {
            id: userData.id,
            email: userData.email,
            name: userData.name || userData.email.split('@')[0],
            accessToken: userData.access_token,
            refreshToken: userData.refresh_token,
          };
        } catch (error) {
          console.error("Authentication error:", error);
          console.error("Full error details:", error);
          return null;
        }
      },
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async jwt({ token, user, account, profile }) {
      if (user) {
        // Add user info and tokens to the JWT token when initially signing in
        token.id = user.id;
        token.email = user.email;
        token.name = user.name;

        // Add tokens from the user object (set in authorize for Credentials)
        if ((user as any).accessToken) {
          token.accessToken = (user as any).accessToken;
          token.refreshToken = (user as any).refreshToken;
          // Set access token expiry to 14 minutes (just before backend token expires at 15 mins)
          token.accessTokenExpires = Date.now() + 14 * 60 * 1000;
        }
        // Handle different property names for tokens
        else if ((user as any).access_token) {
          token.accessToken = (user as any).access_token;
          token.refreshToken = (user as any).refresh_token;
          // Set access token expiry to 14 minutes (just before backend token expires at 15 mins)
          token.accessTokenExpires = Date.now() + 14 * 60 * 1000;
        }
      }

      // Handle Google OAuth callback
      if (account && profile) {
        // This is a Google OAuth sign-in, need to exchange Google info with backend
        if (account.provider === "google") {
          try {
            const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            
            const response = await fetch(`${BACKEND_API_URL}/api/google-signin`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                email: profile.email,
                name: profile.name,
                google_id: profile.sub || (profile as any).id || '', // Google's user ID
              }),
            });

            if (response.ok) {
              const userData: BackendUserResponse = await response.json();
              
              // Add user data to token
              token.id = userData.id;
              token.email = userData.email;
              token.name = userData.name || profile.name;
              token.accessToken = userData.access_token;
              token.refreshToken = userData.refresh_token;
              token.accessTokenExpires = Date.now() + 14 * 60 * 1000;
            } else {
              console.error("Google sign-in failed at backend:", await response.text());
            }
          } catch (error) {
            console.error("Error during Google OAuth callback:", error);
          }
        }
      }

      // If token is expired, try to refresh it
      if (Date.now() >= (token.accessTokenExpires as number || 0)) {
        console.log("Access token expired, attempting refresh");
        return await refreshAccessToken(token);
      }

      return token;
    },
    async session({ session, token }) {
      // Add the access token and user info to the session object
      session.user = {
        ...session.user,
        id: token.id as string,
        email: token.email as string,
        name: token.name as string,
      };

      if (token.accessToken) {
        session.accessToken = token.accessToken as string;
      }
      // Handle different property names for access token
      else if (token.access_token) {
        session.accessToken = token.access_token as string;
      }

      if (token.refreshToken) {
        // Optionally include refresh token in session if needed (but usually not recommended for security)
        (session as any).refreshToken = token.refreshToken as string;
      }
      // Handle different property names for refresh token
      else if (token.refresh_token) {
        (session as any).refreshToken = token.refresh_token as string;
      }

      return session;
    },
  },
  pages: {
    signIn: "/login",
    error: "/login",
  },
  secret: process.env.NEXTAUTH_SECRET,
  debug: process.env.NODE_ENV === "development",
};

// Function to refresh access token
async function refreshAccessToken(token: any) {
  try {
    // Use the same API URL that was used for login - REPLACE WITH YOUR ACTUAL BACKEND URL
    const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; // TODO: Replace with your actual backend URL

    // Add timeout handling and better error reporting
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

    const response = await fetch(`${BACKEND_API_URL}/api/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        refresh_token: token.refreshToken,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text().catch(() => '');
      console.error("Token refresh failed:", response.status, errorText);

      // Return the token as-is, which will cause the user to be logged out
      return {
        ...token,
        error: "RefreshAccessTokenError",
      };
    }

    const refreshedTokens = await response.json();

    return {
      ...token,
      accessToken: refreshedTokens.access_token || refreshedTokens.accessToken,
      refreshToken: refreshedTokens.refresh_token || refreshedTokens.refreshToken,
      accessTokenExpires: Date.now() + 14 * 60 * 1000, // 14 minutes from now
    };
  } catch (error: any) {
    console.error("Error during token refresh:", error);

    // If it's a timeout or network error, return the old token to allow retry later
    if (error.name === 'AbortError' || error.code === 'UND_ERR_HEADERS_TIMEOUT') {
      console.warn("Token refresh timed out, keeping old token temporarily");
      // Extend the expiry time slightly to allow for retry
      return {
        ...token,
        accessTokenExpires: Date.now() + 5 * 60 * 1000, // 5 minutes from now
      };
    }

    return {
      ...token,
      error: "RefreshAccessTokenError",
    };
  }
}