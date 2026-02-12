import { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const { email, password, name } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: "Email and password required" });
    }

    if (password.length < 6) {
      return res.status(400).json({ error: "Password must be at least 6 characters" });
    }

    // Forward the signup request to the backend API
    const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://localhost:8001";
    const response = await fetch(`${BACKEND_API_URL}/api/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
        name: name || email.split('@')[0],
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return res.status(response.status).json({ error: errorData.detail || "Signup failed" });
    }

    const userData = await response.json();

    return res.status(201).json({
      message: "User created successfully",
      userId: userData.id || userData.user_id,
      access_token: userData.access_token,
      refresh_token: userData.refresh_token,
    });
  } catch (error: any) {
    console.error("Signup error:", error);
    return res.status(500).json({
      error: "Internal server error",
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
}