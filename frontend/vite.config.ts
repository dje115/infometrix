import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    hmr: {
      clientPort: 3000
    },
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // Remove the host header to avoid validation issues
            proxyReq.removeHeader('host');
            // Ensure custom headers are forwarded (X-Tenant-ID, etc.)
            // Headers should already be forwarded by default, but we ensure it
          });
          proxy.on('error', (err, req, res) => {
            // Suppress proxy errors for version endpoint during startup
            // These are expected when backend is still starting
            if (req.url?.includes('/version')) {
              return; // Don't log version endpoint errors
            }
            console.error('Proxy error:', err);
          });
        }
      },
      '/enforcesense': {
        target: 'http://enforcement-api:8001',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/enforcesense/, '/enforcesense'),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // Remove the host header to avoid validation issues
            proxyReq.removeHeader('host');
          });
        }
      }
    }
  },
  build: {
    outDir: 'build',
    sourcemap: false,  // SECURITY: Disable source maps in production to prevent information disclosure
    minify: 'esbuild',  // esbuild provides fast, secure minification
    rollupOptions: {
      output: {
        // SECURITY: Obfuscate chunk names to prevent information disclosure
        chunkFileNames: 'assets/js/[hash].js',
        entryFileNames: 'assets/js/[hash].js',
        assetFileNames: 'assets/[ext]/[hash].[ext]',
        manualChunks: (id) => {
          // Optimize chunking for faster parallel loading
          if (id.includes('node_modules')) {
            // React core - small, load first
            if (id.includes('react') && !id.includes('react-dom')) {
              return 'react-core';
            }
            // React DOM - separate from core
            if (id.includes('react-dom')) {
              return 'react-dom';
            }
            // React Router - separate
            if (id.includes('react-router')) {
              return 'react-router';
            }
            // MUI icons - large bundle, separate chunk (only loads when needed)
            if (id.includes('@mui/icons-material')) {
              return 'mui-icons';
            }
            // MUI core - keep together for better tree-shaking
            if (id.includes('@mui/material') || id.includes('@mui/system') || id.includes('@mui/utils')) {
              return 'mui-core';
            }
            // MUI X components - separate
            if (id.includes('@mui/x-')) {
              return 'mui-x';
            }
            // Chart libraries - separate
            if (id.includes('chart.js') || id.includes('react-chartjs')) {
              return 'chart-vendor';
            }
            // Other vendor libraries
            return 'vendor';
          }
        },
        // Optimize for parallel loading
        maxParallelFileOps: 5,
      }
    },
    // SECURITY: Set chunk size warning limit to prevent large bundles
    chunkSizeWarningLimit: 500,
  },
  // Optimize dependencies for faster dev server
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      // Fix dev-time ESM/CJS interop: @mui/utils deepmerge imports named exports from react-is
      // Ensure react-is is pre-bundled so named exports like `isValidElementType` work in the browser.
      'react-is',
      // Fix dev-time ESM/CJS interop: MUI imports default from prop-types
      'prop-types',
      // Fix dev-time ESM/CJS interop: emotion imports default from hoist-non-react-statics (CJS)
      'hoist-non-react-statics',
      '@mui/material',
      '@mui/system',
    ],
    exclude: [
      '@mui/icons-material', // Exclude icons from pre-bundling (large, not needed on login)
    ],
  },
  resolve: {
    alias: {
      '@': '/src'
    },
    // Ensure single instances across nested node_modules (prevents subtle runtime issues)
    dedupe: ['react', 'react-dom', 'react-is', 'prop-types', 'hoist-non-react-statics']
  }
})




