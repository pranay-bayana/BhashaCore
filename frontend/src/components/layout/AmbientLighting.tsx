import React from 'react';

export const AmbientLighting: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0 select-none" aria-hidden="true">
      {/* Central Luminous Research Beam */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[2px] h-[750px] bg-gradient-to-b from-accent-lime/40 via-accent-emerald/25 to-transparent blur-[1px] opacity-75 dark:opacity-100"
      />
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[340px] h-[650px] bg-gradient-to-b from-accent-lime/15 via-accent-emerald/08 to-transparent rounded-full blur-[90px] animate-pulse-subtle opacity-70 dark:opacity-100"
      />

      {/* Top Right Emerald Orb */}
      <div
        className="absolute -top-[120px] -right-[100px] w-[500px] h-[500px] bg-gradient-to-br from-accent-emerald/10 to-transparent rounded-full blur-[110px]"
      />

      {/* Bottom Left Lime Orb */}
      <div
        className="absolute bottom-[5%] -left-[100px] w-[550px] h-[550px] bg-gradient-to-tr from-accent-lime/10 to-transparent rounded-full blur-[120px]"
      />

      {/* Center-Left Workspace Ambient Glow (diffused through glass) */}
      <div
        className="absolute top-[35%] left-[25%] w-[480px] h-[480px] bg-gradient-to-br from-accent-lime/[0.07] via-accent-emerald/[0.05] to-transparent rounded-full blur-[110px]"
      />

      {/* Subtle India Contour & Language Matrix Motif (Ultra low opacity, behind glass) */}
      <div
        className="absolute top-1/4 right-[5%] w-[480px] h-[520px] opacity-[0.035] dark:opacity-[0.045] blur-[0.5px] text-accent-lime pointer-events-none"
      >
        <svg viewBox="0 0 400 450" fill="none" stroke="currentColor" className="w-full h-full">
          {/* Constellation nodes forming the subtle Indic subcontinent silhouette */}
          <path
            d="M190 40 L215 70 L240 85 L260 120 L270 160 L285 190 L260 230 L245 280 L220 330 L205 380 L195 410 L185 380 L160 330 L135 270 L125 210 L135 160 L145 120 L165 75 Z"
            strokeWidth="1.2"
            strokeDasharray="4 6"
            className="animate-pulse"
          />
          {/* Indic Glyph Cross-Nodes */}
          <circle cx="190" cy="40" r="3" fill="currentColor" />
          <circle cx="215" cy="70" r="2.5" fill="currentColor" />
          <circle cx="260" cy="120" r="3" fill="currentColor" />
          <circle cx="270" cy="160" r="2.5" fill="currentColor" />
          <circle cx="285" cy="190" r="3" fill="currentColor" />
          <circle cx="245" cy="280" r="3" fill="currentColor" />
          <circle cx="205" cy="380" r="3.5" fill="currentColor" />
          <circle cx="160" cy="330" r="2.5" fill="currentColor" />
          <circle cx="125" cy="210" r="3" fill="currentColor" />
          <circle cx="145" cy="120" r="2.5" fill="currentColor" />
          <circle cx="195" cy="230" r="4" fill="currentColor" opacity="0.6" />
          {/* Harmonic Indic Wave Coordinates */}
          <path d="M140 180 Q195 195 250 180" strokeWidth="0.8" strokeDasharray="3 4" opacity="0.5" />
          <path d="M150 230 Q195 245 240 230" strokeWidth="0.8" strokeDasharray="3 4" opacity="0.5" />
          <path d="M165 280 Q195 295 225 280" strokeWidth="0.8" strokeDasharray="3 4" opacity="0.5" />
        </svg>
      </div>

      {/* Dark mode center depth vignette (hidden in light mode) */}
      <div
        className="hidden dark:block absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[600px] bg-gradient-to-r from-[#0A100D]/40 via-[#10221A]/20 to-[#0A100D]/40 rounded-full blur-[130px]"
      />
    </div>
  );
};
