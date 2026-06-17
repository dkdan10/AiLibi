import type { StorybookConfig } from "@storybook/react-vite";

// Story-per-component scaffold (DESIGN.md §6 "Anchors: Storybook"). Stories are
// co-located with their component (`src/ui/*.stories.tsx`) plus the design
// `src/stories/Tokens.stories.tsx` sheet. The react-vite framework reuses the
// app's vite.config.ts, so the Tailwind v4 plugin + token `@theme` apply here
// exactly as in the app.
const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(ts|tsx)"],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
};

export default config;
