import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.resolve.alias["@clerk/nextjs"] = path.resolve(__dirname, "lib/mock-clerk.tsx");
    return config;
  },
  turbopack: {
    resolveAlias: {
      "@clerk/nextjs": "./lib/mock-clerk.tsx"
    }
  }
};

export default nextConfig;
