import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0f172a', // Slate 900
          hover: '#1e293b',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#f8fafc', // Slate 50
          hover: '#f1f5f9',
          foreground: '#0f172a',
        },
        accent: {
          DEFAULT: '#ea580c', // Orange 600 (Travel/Package highlight)
          hover: '#c2410c',
          foreground: '#ffffff',
        },
        background: '#f4f4f5', // Zinc 100
        surface: {
          DEFAULT: '#ffffff',
          elevated: '#ffffff',
        },
        text: {
          primary: '#18181b', // Zinc 900
          secondary: '#52525b', // Zinc 500
          muted: '#a1a1aa', // Zinc 400
        },
        border: '#e4e4e7', // Zinc 200
        status: {
          success: '#16a34a',
          warning: '#ca8a04',
          error: '#dc2626',
          info: '#2563eb',
        }
      },
      borderRadius: {
        DEFAULT: '0.375rem', // sm
        md: '0.5rem',
        lg: '0.75rem',
        full: '9999px',
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
      }
    },
  },
  plugins: [],
}
export default config
