import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variants = {
    default: 'bg-secondary text-text-secondary border-border',
    success: 'bg-green-50 text-status-success border-green-200',
    warning: 'bg-yellow-50 text-status-warning border-yellow-200',
    error: 'bg-red-50 text-status-error border-red-200',
    info: 'bg-blue-50 text-status-info border-blue-200',
  }

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}
