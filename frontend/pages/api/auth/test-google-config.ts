import { NextApiRequest, NextApiResponse } from "next";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const config = {
    hasGoogleClientId: !!process.env.GOOGLE_CLIENT_ID,
    hasGoogleClientSecret: !!process.env.GOOGLE_CLIENT_SECRET,
    hasNextAuthUrl: !!process.env.NEXTAUTH_URL,
    hasNextAuthSecret: !!process.env.NEXTAUTH_SECRET,
    googleClientIdPrefix: process.env.GOOGLE_CLIENT_ID?.substring(0, 20) || "MISSING",
    nextAuthUrl: process.env.NEXTAUTH_URL || "MISSING",
  };

  return res.status(200).json(config);
}