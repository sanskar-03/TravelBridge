import React from 'react';
export const Card = ({ children, className = '', title }: { children: React.ReactNode, className?: string, title?: string }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden ${className}`}>
    {title && <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 font-semibold text-slate-800">{title}</div>}
    <div className="p-6">{children}</div>
  </div>
);
