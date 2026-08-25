import type { ReactNode } from 'react';
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
