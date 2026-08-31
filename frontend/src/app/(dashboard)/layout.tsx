"use client";
import React, { useEffect, useState } from 'react';
import { AppSidebar } from '@/components/layout/AppSidebar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [title, setTitle] = useState('Portal');
  useEffect(() => {
    if (window.location.pathname.includes('/requester')) setTitle('Requester Portal');
    else setTitle('Traveler Portal');
  }, []);

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <AppSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center px-8 justify-between shrink-0 shadow-sm z-10">
            <div className="font-bold text-slate-800 tracking-tight">{title}</div>
            <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold shadow-sm">U</div>
        </header>
        <main className="flex-1 overflow-y-auto p-8 relative">{children}</main>
      </div>
    </div>
  );
}
