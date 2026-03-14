import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, 'src/agent-chat.ts'),
      formats: ['es'],
      fileName: 'agent-chat',
    },
    rollupOptions: {
      output: {
        // Preserve custom element definitions — avoid treeshaking them away
        preserveModules: false,
      },
    },
    target: 'es2022',
    sourcemap: true,
    minify: 'esbuild',
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
});
