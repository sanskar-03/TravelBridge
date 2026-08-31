"use client";
import React from 'react';

export default function AppSidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shadow-xl z-20 shrink-0 h-full">
      <div className="p-6 border-b border-slate-800 bg-slate-950">
        <h2 className="text-2xl font-black text-white tracking-tight">TravelBridge</h2>
        <span className="text-xs font-bold uppercase tracking-wider text-blue-400 mt-1 block">Portal Workspace</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-4 space-y-1">
        <a href="/dashboard" className="block px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white font-medium">📊 Dashboard Hub</a>
        <a href="/traveler" className="block px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white font-medium">✈️ Traveler Portal</a>
        <a href="/traveler/trips" className="block px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white font-medium">🛣️ My Trips</a>
        <a href="/requester" className="block px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white font-medium">📦 Requester Portal</a>
        <a href="/requester/requests" className="block px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white font-medium">📋 Package Requests</a>
      </nav>
      <div className="p-4 border-t border-slate-800">
        <button onClick={() => { localStorage.clear(); window.location.href='/login'; }} className="w-full text-left px-4 py-2 text-red-400 hover:bg-slate-800 rounded font-medium">Logout</button>
      </div>
    </aside>
  );
}
