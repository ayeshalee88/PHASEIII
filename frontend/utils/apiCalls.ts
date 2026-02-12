// utils/apiCalls.ts
// This file contains example functions showing how to make authenticated calls
// to your backend services using the JWT token from NextAuth

import { getServerSession } from "next-auth/next";
import { authOptions } from "../app/api/auth/[...nextauth]/route"; // Adjust path as needed

/**
 * Example function to make an authenticated call to your FastAPI backend
 * @param endpoint - The specific endpoint to call on your backend
 * @param options - Additional fetch options (method, body, etc.)
 * @returns Response from the backend
 */
export async function callBackendAPI(endpoint: string, options: RequestInit = {}) {
  // For server-side calls, get the session using getServerSession
  const session = await getServerSession(authOptions);
  
  if (!session || !session.accessToken) {
    throw new Error("User not authenticated");
  }

  // TODO: Replace with your actual backend URL
  const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  const response = await fetch(`${BACKEND_API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": `Bearer ${session.accessToken}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Backend API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Example function to make an authenticated call to your MCP server
 * @param endpoint - The specific endpoint to call on your MCP server
 * @param options - Additional fetch options (method, body, etc.)
 * @returns Response from the MCP server
 */
export async function callMCPServer(endpoint: string, options: RequestInit = {}) {
  // For server-side calls, get the session using getServerSession
  const session = await getServerSession(authOptions);
  
  if (!session || !session.accessToken) {
    throw new Error("User not authenticated");
  }

  // TODO: Replace with your actual MCP server URL
  const MCP_SERVER_URL = process.env.MCP_SERVER_URL || "http://localhost:8001";
  
  const response = await fetch(`${MCP_SERVER_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": `Bearer ${session.accessToken}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`MCP Server API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Example function to make an authenticated call to your agent endpoints
 * @param endpoint - The specific endpoint to call on your agent service
 * @param options - Additional fetch options (method, body, etc.)
 * @returns Response from the agent service
 */
export async function callAgentAPI(endpoint: string, options: RequestInit = {}) {
  // For server-side calls, get the session using getServerSession
  const session = await getServerSession(authOptions);
  
  if (!session || !session.accessToken) {
    throw new Error("User not authenticated");
  }

  // TODO: Replace with your actual agent service URL
  const AGENT_API_URL = process.env.AGENT_API_URL || "http://localhost:8002";
  
  const response = await fetch(`${AGENT_API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": `Bearer ${session.accessToken}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Agent API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Client-side helper to get the access token from NextAuth session
 * Note: This only works in client components or client-side code
 */
export async function getAccessToken() {
  // This requires importing next-auth/client functions in the component where it's used
  // import {getSession} from 'next-auth/react';
  // const session = await getSession();
  // return session?.accessToken;
  
  // For demonstration purposes only - actual implementation depends on where it's used
  console.warn("getAccessToken() is a client-side function that requires importing getSession from next-auth/react");
  return null;
}