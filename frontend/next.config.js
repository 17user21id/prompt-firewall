/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/query',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/v1/query`,
      },
      {
        source: '/api/tenants/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/v1/tenants/:path*`,
      },
      {
        source: '/api/rules/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/v1/rules/:path*`,
      },
      {
        source: '/api/logs/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/v1/logs/:path*`,
      },
      {
        source: '/api/prompts/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/v1/prompts/:path*`,
      },
      {
        source: '/api/stats/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/v1/stats/:path*`,
      },
    ];
  },
  images: {
    domains: ['localhost'],
  },
};

module.exports = nextConfig;
