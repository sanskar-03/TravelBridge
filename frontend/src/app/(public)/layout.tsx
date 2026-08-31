import React from 'react';
export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center sticky top-0 z-50 shadow-sm">
        <a href="/" className="text-2xl font-black text-blue-600 tracking-tight">TravelBridge</a>
        <div className="flex gap-4">
          <a href="/login" className="px-4 py-2 font-medium text-slate-700 hover:text-slate-900">Sign In</a>
          <a href="/register" className="px-4 py-2 bg-slate-900 text-white rounded-md font-medium hover:bg-slate-800">Register</a>
        </div>
      </header>
      <main className="flex-grow">{children}</main>
    </div>
  );
}
