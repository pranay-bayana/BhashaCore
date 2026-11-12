import React, { ReactNode } from 'react';

export interface BadgeProps {
  variant?: 'lime' | 'emerald' | 'glass' | 'subtle';
  children: ReactNode;
  className?: string;
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'glass',
  children,
  className = '',
  dot = false,
}) => {
  let variantStyles = '';
  let dotColor = '';

  switch (variant) {
    case 'lime':
      variantStyles = 'bg-accent-lime/10 border-accent-lime/30 text-accent-lime';
      dotColor = 'bg-accent-lime shadow-[0_0_8px_rgba(183,255,114,0.6)]';
      break;
    case 'emerald':
      variantStyles = 'bg-accent-emerald/10 border-accent-emerald/30 text-accent-emerald';
      dotColor = 'bg-accent-emerald shadow-[0_0_8px_rgba(54,214,154,0.6)]';
      break;
    case 'glass':
      variantStyles = 'bg-white/[0.06] border-white/15 text-text-primary backdrop-blur-md';
      dotColor = 'bg-accent-lime';
      break;
    case 'subtle':
      variantStyles = 'bg-white/[0.03] border-white/10 text-text-secondary';
      dotColor = 'bg-text-secondary';
      break;
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${variantStyles} ${className}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotColor}`} />}
      {children}
    </span>
  );
};
