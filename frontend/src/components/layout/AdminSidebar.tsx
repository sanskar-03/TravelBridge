"use client";
import React from 'react';

export default function AdminSidebar() {
  return (
    <aside className="w-64 bg-slate-950 text-slate-300 min-h-screen flex flex-col shrink-0 z-20">
      <div className="p-6 border-b border-slate-800 bg-black">
        <h2 className="text-xl font-bold text-white tracking-tight">Admin Operations</h2>
      </div>
      <nav className="flex-1 py-4 flex flex-col gap-1">
        <a href="/admin" className="px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white">📊 Dashboard</a>
        <a href="/admin/users" className="px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white">👥 Users</a>
        <a href="/admin/packages" className="px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white">📦 Packages & Trips</a>
        <a href="/admin/payments" className="px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white">💳 Payments Ledger</a>
        <a href="/admin/disputes" className="px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white">⚠️ Dispute Center</a>
        <a href="/admin/verification" className="px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white">✓ KYC Verification</a>
      </nav>
      <div className="p-6 border-t border-slate-800">
        <button onClick={() => { localStorage.clear(); window.location.href='/admin/login'; }} className="text-red-400 hover:text-red-300 w-full text-left font-medium px-4 py-2 hover:bg-slate-800 rounded">Secure Logout</button>
      </div>
    </aside>
  );
}
