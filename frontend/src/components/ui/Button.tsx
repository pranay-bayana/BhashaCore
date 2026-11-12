import React, { forwardRef, ButtonHTMLAttributes } from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = '', variant = 'secondary', size = 'md', loading = false, disabled, children, ...props }, ref) => {
    let variantStyles = '';
    switch (variant) {
      case 'primary':
        variantStyles = 'btn-lime-glass';
        break;
      case 'secondary':
        variantStyles = 'btn-ghost-glass';
        break;
      case 'ghost':
        variantStyles = 'bg-transparent hover:bg-white/[0.06] text-text-primary border border-transparent hover:border-white/10 transition-all';
        break;
      case 'outline':
        variantStyles = 'bg-white/[0.03] border border-white/15 text-text-primary hover:bg-white/[0.08] hover:border-white/25 transition-all';
        break;
      case 'danger':
        variantStyles = 'bg-red-500/10 border border-red-500/20 text-red-300 hover:bg-red-500/20 hover:border-red-500/40 transition-all';
        break;
    }

    let sizeStyles = '';
    switch (size) {
      case 'sm':
        sizeStyles = 'px-3 py-1.5 text-xs rounded-xl gap-1.5';
        break;
      case 'md':
        sizeStyles = 'px-4 py-2 text-sm rounded-2xl gap-2';
        break;
      case 'lg':
        sizeStyles = 'px-6 py-3 text-base rounded-2xl gap-2.5';
        break;
      case 'icon':
        sizeStyles = 'p-2 rounded-xl aspect-square flex items-center justify-center';
        break;
    }

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`inline-flex items-center justify-center font-medium select-none outline-none focus-visible:ring-2 focus-visible:ring-accent-lime/50 disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles} ${sizeStyles} ${className}`}
        {...props}
      >
        {loading && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
