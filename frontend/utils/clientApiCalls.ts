// utils/clientApiCalls.ts
// Client-side API call utilities that work with NextAuth session

import { Session } from "next-auth";

/**
 * Example function to make an authenticated call to your FastAPI backend from the client side
 * @param endpoint - The specific endpoint to call on your backend
 * @param options - Additional fetch options (method, body, etc.)
 * @param session - The NextAuth session containing the access token
 * @returns Response from the backend
 */
export async function callBackendAPIClient(
  endpoint: string, 
  options: RequestInit = {}, 
  session: Session | null
) {
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
 * Example function to make an authenticated call to your MCP server from the client side
 * @param endpoint - The specific endpoint to call on your MCP server
 * @param options - Additional fetch options (method, body, etc.)
 * @param session - The NextAuth session containing the access token
 * @returns Response from the MCP server
 */
export async function callMCPServerClient(
  endpoint: string, 
  options: RequestInit = {}, 
  session: Session | null
) {
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
 * Example function to make an authenticated call to your agent endpoints from the client side
 * @param endpoint - The specific endpoint to call on your agent service
 * @param options - Additional fetch options (method, body, etc.)
 * @param session - The NextAuth session containing the access token
 * @returns Response from the agent service
 */
export async function callAgentAPIClient(
  endpoint: string, 
  options: RequestInit = {}, 
  session: Session | null
) {
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