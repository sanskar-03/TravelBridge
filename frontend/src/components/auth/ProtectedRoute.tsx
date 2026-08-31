"use client";
import React, { useEffect, useState } from 'react';

export const ProtectedRoute = ({ children, requireAdmin = false }: { children: React.ReactNode, requireAdmin?: boolean }) => {
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    if (!token) {
      window.location.href = requireAdmin ? '/admin/login' : '/login';
      return;
    }

    if (requireAdmin && role !== 'admin') {
      window.location.href = '/login';
      return;
    }

    setIsAuthorized(true);
  }, [requireAdmin]);

  if (!isAuthorized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-600"></div>
      </div>
    );
  }

  return <>{children}</>;
};
