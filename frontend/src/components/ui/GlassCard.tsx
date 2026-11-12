import React, { forwardRef, HTMLAttributes } from 'react';

export interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  tier?: 'surface' | 'elevated' | 'subtle';
  interactive?: boolean;
}

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className = '', tier = 'surface', interactive = false, children, ...props }, ref) => {
    let tierClass = 'glass-panel';
    if (tier === 'elevated') tierClass = 'glass-elevated';
    if (tier === 'subtle') tierClass = 'glass-subtle';

    const interactiveClass = interactive
      ? 'transition-all duration-300 hover:border-white/25 hover:translate-y-[-2px] hover:shadow-glass-lg cursor-pointer'
      : '';

    return (
      <div
        ref={ref}
        className={`${tierClass} rounded-2xl ${interactiveClass} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

GlassCard.displayName = 'GlassCard';
