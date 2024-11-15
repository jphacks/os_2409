import type { NextConfig } from "next";

const isDevelopment = process.env.NODE_ENV !== 'production'

const nextConfig: NextConfig = {
  /* config options here */

  output: 'export',
  images: {
    unoptimized: true
  },
  assetPrefix: isDevelopment ? '' : '',
};

export default nextConfig;
