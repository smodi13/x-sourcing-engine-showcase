/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Pin the tracing root to this project (multiple lockfiles exist above it).
  outputFileTracingRoot: import.meta.dirname,
  // The demo is fully self-contained. It reads only local sanitized JSON and
  // never contacts the X API or any external host at build or run time.
};

export default nextConfig;
