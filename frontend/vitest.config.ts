import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    globals: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      include: ["lib/**", "components/**", "types/**"],
      exclude: [
        "node_modules",
        ".next",
        "**/*.config.*",
        // Auth SDK wrappers — just re-exports, no logic to test
        "lib/auth.ts",
        "lib/auth-server.ts",
        // Navigation components — depend on Next.js router/session hooks
        "components/shared/**",
        // Coming-soon file upload forms (501 endpoints)
        "components/scanner/ImageScanForm.tsx",
        "components/scanner/QrScanForm.tsx",
        "components/scanner/PhoneScanForm.tsx",
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "."),
    },
  },
});
