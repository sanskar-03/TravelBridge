"use client";
import React from 'react';
export default function LandingPage() {
  return (
    <div className="bg-slate-50 min-h-[calc(100vh-73px)] flex flex-col items-center justify-center p-6 text-center">
      <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 mb-6 tracking-tight">Travel smarter. <span className="text-blue-600">Deliver easier.</span></h1>
      <p className="text-xl text-slate-600 mb-10 max-w-2xl">Connect with travelers who have extra baggage space. A practical, peer-to-peer way to get your packages delivered safely.</p>
      <div className="flex gap-4">
        <a href="/login" className="bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-700 shadow-md">Get Started</a>
        <a href="/admin/login" className="bg-slate-900 text-white px-8 py-4 rounded-lg font-semibold hover:bg-slate-800 shadow-md">Admin Portal</a>
      </div>
    </div>
  );
}
