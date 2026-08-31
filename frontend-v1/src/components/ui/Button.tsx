import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'outline';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', isLoading, className = '', disabled, ...props }) => {
  const base = "px-6 py-2.5 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 shadow-sm",
    secondary: "bg-slate-900 text-white hover:bg-slate-800 shadow-sm",
    danger: "bg-red-600 text-white hover:bg-red-700 shadow-sm",
    outline: "bg-transparent border border-slate-300 text-slate-700 hover:bg-slate-50"
  };

  return (
    <button className={`${base} ${variants[variant]} ${className}`} disabled={isLoading || disabled} {...props}>
      {isLoading ? <span className="animate-spin mr-2 h-4 w-4 border-2 border-current border-t-transparent rounded-full" /> : null}
      {children}
    </button>
  );
};
