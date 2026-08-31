import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, className = '', ...props }) => (
  <div className={`flex flex-col gap-1.5 mb-4 ${className}`}>
    <label className="text-sm font-medium text-slate-700">{label}</label>
    <input 
      className={`px-4 py-2.5 bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 transition-shadow ${
        error ? 'border-red-500 focus:ring-red-200' : 'border-slate-200 focus:ring-blue-200 focus:border-blue-500'
      }`}
      {...props}
    />
    {error && <span className="text-xs text-red-500 font-medium">{error}</span>}
  </div>
);
