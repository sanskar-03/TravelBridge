"use client";
import React from 'react';

export default function DashboardHub() {
  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-4">Dashboard Hub</h1>
      <p className="text-slate-600 mb-6">Select your portal workspace below:</p>
      <div className="flex gap-4">
        <a href="/traveler" className="px-6 py-3 bg-blue-600 text-white rounded-xl font-bold shadow-sm">Traveler Portal</a>
        <a href="/requester" className="px-6 py-3 bg-slate-900 text-white rounded-xl font-bold shadow-sm">Requester Portal</a>
      </div>
    </div>
  );
}
