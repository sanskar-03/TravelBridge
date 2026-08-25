import os
from pathlib import Path

# --- 1. DIRECTORY STRUCTURE ---
DIRECTORIES = [
    "frontend/src/components/ui",
    "frontend/src/components/layout",
    "frontend/src/lib",
]

# --- 2. FILE DEFINITIONS ---
FILES = {
    # -------------------------------------------------------------
    # FRONTEND CONFIGURATION & UTILS
    # -------------------------------------------------------------
    "frontend/tailwind.config.ts": """import type { Config } from 'tailwindcss'

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
""",

    "frontend/postcss.config.js": """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",

    "frontend/src/lib/utils.ts": """import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
""",

    "frontend/src/app/globals.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-background text-text-primary antialiased;
  }
  
  /* Focus rings for accessibility */
  *:focus-visible {
    @apply outline-none ring-2 ring-accent ring-offset-2 ring-offset-background;
  }
}
""",

    # -------------------------------------------------------------
    # UI COMPONENTS
    # -------------------------------------------------------------
    "frontend/src/components/ui/Button.tsx": """import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
    const variants = {
      primary: 'bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm',
      secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary-hover border border-border',
      outline: 'border border-border bg-transparent hover:bg-secondary text-text-primary',
      ghost: 'bg-transparent hover:bg-secondary text-text-primary',
      destructive: 'bg-status-error text-white hover:bg-red-700 shadow-sm',
    }

    const sizes = {
      sm: 'h-8 px-3 text-sm',
      md: 'h-10 px-4 py-2',
      lg: 'h-12 px-8 text-lg',
    }

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md font-medium transition-colors disabled:opacity-50 disabled:pointer-events-none",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"
""",

    "frontend/src/components/ui/Card.tsx": """import * as React from "react"
import { cn } from "@/lib/utils"

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-lg border border-border bg-surface shadow-sm", className)} {...props} />
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-lg font-semibold leading-none tracking-tight", className)} {...props} />
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6 pt-0 text-text-secondary", className)} {...props} />
}
""",

    "frontend/src/components/ui/Input.tsx": """import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        {label && <label className="text-sm font-medium text-text-primary">{label}</label>}
        <input
          type={type}
          className={cn(
            "flex h-10 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-text-primary placeholder:text-text-muted transition-colors",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:border-accent",
            "disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-status-error focus-visible:ring-status-error",
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <span className="text-xs text-status-error">{error}</span>}
      </div>
    )
  }
)
Input.displayName = "Input"
""",

    "frontend/src/components/ui/Badge.tsx": """import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variants = {
    default: 'bg-secondary text-text-secondary border-border',
    success: 'bg-green-50 text-status-success border-green-200',
    warning: 'bg-yellow-50 text-status-warning border-yellow-200',
    error: 'bg-red-50 text-status-error border-red-200',
    info: 'bg-blue-50 text-status-info border-blue-200',
  }

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}
""",

    # -------------------------------------------------------------
    # APPLICATION PAGES (Applying the Design System)
    # -------------------------------------------------------------
    "frontend/src/app/layout.tsx": """import type { ReactNode } from 'react';
import './globals.css';

export const metadata = {
  title: 'TravelBridge — Travel & Baggage Marketplace',
  description: 'Connect with travelers to send packages securely.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex flex-col">
          <header className="border-b border-border bg-surface px-6 py-4 flex items-center justify-between">
            <div className="font-bold text-xl text-primary tracking-tight">TravelBridge</div>
            <nav className="flex gap-4">
              <a href="#" className="text-sm font-medium text-text-secondary hover:text-primary transition-colors">Find a traveler</a>
              <a href="#" className="text-sm font-medium text-text-secondary hover:text-primary transition-colors">Sign in</a>
            </nav>
          </header>
          <main className="flex-1">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
""",

    "frontend/src/app/page.tsx": """import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";

export default function HomePage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-12">
      {/* Hero Section */}
      <section className="space-y-6 max-w-2xl">
        <h1 className="text-4xl font-bold text-primary tracking-tight">
          Send an item with someone already heading there.
        </h1>
        <p className="text-lg text-text-secondary leading-relaxed">
          Connect with travelers who have extra baggage space. A practical, peer-to-peer way to get your packages delivered safely.
        </p>
        <div className="flex items-center gap-4">
          <Button variant="primary" size="lg">Request a delivery</Button>
          <Button variant="outline" size="lg">Post your trip</Button>
        </div>
      </section>

      <hr className="border-border" />

      {/* Component Demo Section (Sample Data) */}
      <section className="space-y-8">
        <div>
          <h2 className="text-2xl font-semibold text-primary mb-2">Active Journeys (Sample)</h2>
          <p className="text-sm text-text-muted">Demonstrating Design System Components (Part 03)</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader className="flex flex-row justify-between items-start">
              <div>
                <CardTitle>London → New York</CardTitle>
                <p className="text-sm mt-1">Oct 24, 2026</p>
              </div>
              <Badge variant="success">Verified</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between text-sm">
                <span>Available Capacity:</span>
                <span className="font-medium text-text-primary">5 kg</span>
              </div>
              <Button variant="secondary" className="w-full">Message Traveler</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row justify-between items-start">
              <div>
                <CardTitle>Tokyo → Sydney</CardTitle>
                <p className="text-sm mt-1">Oct 28, 2026</p>
              </div>
              <Badge variant="info">Pending</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between text-sm">
                <span>Available Capacity:</span>
                <span className="font-medium text-text-primary">2 kg</span>
              </div>
              <Button variant="secondary" className="w-full">Message Traveler</Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
""",

    # -------------------------------------------------------------
    # DOCUMENTATION UPDATES
    # -------------------------------------------------------------
    "DESIGN_SYSTEM.md": """# TravelBridge Design System & Visual Identity

## 1. Design Philosophy
TravelBridge is a peer-to-peer platform connecting real journeys with real deliveries. The interface must communicate trust, practicality, clarity, and professionalism. 
**Anti-AI Rule:** We do not use generic AI SaaS tropes (neon gradients, floating 3D blobs, "Revolutionize your journey" marketing copy). Everything is built to be useful first.

## 2. Copywriting Rules
* **Short, specific, human.**
* Use "Post your trip" instead of "Unlock seamless trip posting."
* Use "Send a package" instead of "Experience next-generation transportation."

## 3. Color Tokens
* **Primary (Trust/Anchor):** Slate 900 (`#0f172a`)
* **Secondary (Background accents):** Slate 50 (`#f8fafc`)
* **Accent (Action/Highlight):** Orange 600 (`#ea580c`)
* **Background:** Zinc 100 (`#f4f4f5`)
* **Surface:** White (`#ffffff`)
* **Text:** Zinc 900 (Primary), Zinc 500 (Secondary), Zinc 400 (Muted)
* **Status:** Green (Success), Yellow (Warning), Red (Error), Blue (Info)

## 4. Typography
* System fonts (sans-serif) prioritizing readability.
* Clear hierarchy: H1 (Display), H2 (Section), H3 (Card Titles), Body, Small/Muted.

## 5. Spacing & Radius
* **Spacing:** Tailwind default 4-point grid (e.g., p-4 = 1rem, p-6 = 1.5rem).
* **Radius:** Controlled (`sm` for inputs, `md` for buttons, `lg` for cards). No excessive pill shapes unless specific to badges.

## 6. Components
* **Button:** Primary, Secondary, Outline, Ghost, Destructive. Clear hover/focus states.
* **Input:** Standardized with labels, validation rings, and error text states.
* **Card:** Structural container for journeys/requests. Avoid nesting cards inside cards.
* **Badge:** Status indicators that use both color and semantic text for accessibility.

## 7. Accessibility & Responsive
* **Focus States:** Every interactive element has a visible `ring-2 ring-accent` on keyboard focus.
* **Responsive:** Mobile-first grid layouts. Touch targets are a minimum of 40px high (`h-10`).
""",

    "HANDOFF_STATE.md": """# TravelBridge Handoff State

## Current Part
Part 03 of 22

## Current Status
Design System and Visual Identity established.

## Completed in Part 03
- Configured Tailwind CSS, PostCSS, and structural utility functions (`cn`, `clsx`, `tailwind-merge`).
- Created foundational UI components (`Button`, `Input`, `Card`, `Badge`).
- Implemented human-centered, anti-AI visual tokens (Colors, Typography, Spacing).
- Rewrote `page.tsx` landing UI using natural copy and new components.
- Updated `DESIGN_SYSTEM.md` with strict guidelines for future agents.

## Frontend Files Created/Modified
- `frontend/tailwind.config.ts`
- `frontend/postcss.config.js`
- `frontend/src/lib/utils.ts`
- `frontend/src/app/globals.css`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/components/ui/Button.tsx`
- `frontend/src/components/ui/Card.tsx`
- `frontend/src/components/ui/Input.tsx`
- `frontend/src/components/ui/Badge.tsx`

## Known Issues / Not Implemented
- Icons (Lucide React) are planned but not actively utilized in the demo cards yet.
- Forms are visually styled but lack client-side state/validation logic (Zod/React Hook Form to be added in feature phases).

## Next Part
Part 04 — Docker, PostgreSQL, Redis & Infrastructure Hardening
"""
}

def create_scaffold():
    print("🚀 Initializing TravelBridge Design System (Part 03)...\n")

    for directory in DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}/")

    for filename, content in FILES.items():
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 Created file:      {filename}")

    print("\n✅ Part 03 Setup complete!")
    print("\n👉 REQUIRED NEXT STEPS:")
    print("1. Open your terminal and navigate to the frontend folder:")
    print("   cd frontend")
    print("2. Install the new design dependencies by running:")
    print("   npm install tailwindcss postcss autoprefixer clsx tailwind-merge lucide-react")
    print("3. Start your Docker containers again to see the UI updates:")
    print("   docker-compose up --build")

if __name__ == "__main__":
    create_scaffold()