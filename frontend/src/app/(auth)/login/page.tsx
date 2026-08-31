"use client";
import React, { useState } from 'react';

export default function UserLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleRealLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok && (data.access || data.token)) {
        localStorage.setItem('accessToken', data.access || data.token);
        const targetRole = email.includes('traveler') ? 'traveler' : 'requester';
        window.location.href = `/${targetRole}`;
      } else {
        setError(data.detail || 'Invalid email or password.');
      }
    } catch {
      setError('Failed to connect to backend authentication server.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <form onSubmit={handleRealLogin} className="bg-white p-10 rounded-2xl shadow-sm border border-slate-200 w-full max-w-md">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">TravelBridge Login</h2>
          <p className="text-sm text-slate-500 mt-1">Real Backend JWT Authentication</p>
        </div>
        {error && <div className="mb-4 p-3 bg-red-50 text-red-700 text-xs rounded-xl font-bold text-center">{error}</div>}
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Email Address</label>
            <input required type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="traveler@example.com" className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none" />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Password</label>
            <input required type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none" />
          </div>
        </div>
        <button type="submit" className="w-full bg-slate-900 text-white py-3.5 rounded-xl font-bold hover:bg-slate-800 transition">Sign In via Backend</button>
      </form>
    </div>
  );
}
