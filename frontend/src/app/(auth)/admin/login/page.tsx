"use client";
import React, { useState } from 'react';

export default function AdminLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: username, password })
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('accessToken', data.access || data.token);
        window.location.href = '/admin';
      } else {
        setError('Admin authorization failed. Superuser required.');
      }
    } catch {
      setError('Backend connection error.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4">
      <form onSubmit={handleAdminLogin} className="bg-slate-800 p-10 rounded-2xl shadow-2xl border border-slate-700 w-full max-w-md">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-white tracking-tight">Admin Operations</h2>
          <p className="text-xs text-blue-400 mt-1 uppercase tracking-widest font-bold">Django Superuser Login</p>
        </div>
        {error && <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl font-medium text-center">{error}</div>}
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Superuser Email / Username</label>
            <input required type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="admin@example.com" className="w-full px-4 py-3 bg-slate-900 border border-slate-700 text-white rounded-xl outline-none" />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Password</label>
            <input required type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" className="w-full px-4 py-3 bg-slate-900 border border-slate-700 text-white rounded-xl outline-none" />
          </div>
        </div>
        <button type="submit" className="w-full bg-blue-600 text-white py-3.5 rounded-xl font-bold hover:bg-blue-700 transition shadow-lg">Authenticate Superuser</button>
      </form>
    </div>
  );
}
