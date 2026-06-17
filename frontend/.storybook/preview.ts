import type { Preview } from "@storybook/react-vite";

// Load the Playful cream/ink base + token `@theme` + self-hosted fonts so every
// story renders on the real design surface (the preview iframe body picks up
// the cream background and Fredoka from `index.css`).
import "../src/index.css";

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
};

export default preview;
