import React, { useState, useEffect } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { AmbientLighting } from '@/components/layout/AmbientLighting';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { HomePage } from '@/pages/HomePage';
import { ChatPage } from '@/pages/ChatPage';
import { ResearchPage } from '@/pages/ResearchPage';
import { AboutPage } from '@/pages/AboutPage';
import { AuthModal } from '@/pages/AuthModal';
import { fetchUserSession, authLogout } from '@/services/api';

function getRouteFromPath(pathname: string): string {
  if (pathname === '/chat') return 'chat';
  if (pathname === '/dashboard') return 'dashboard';
  if (pathname === '/language-comparison') return 'comparison';
  if (pathname === '/failure-analysis') return 'failures';
  if (pathname === '/about') return 'about';
  return 'home';
}

function getPathFromRoute(route: string): string {
  switch (route) {
    case 'chat': return '/chat';
    case 'dashboard': return '/dashboard';
    case 'comparison': return '/language-comparison';
    case 'failures': return '/failure-analysis';
    case 'about': return '/about';
    default: return '/';
  }
}

export const App: React.FC = () => {
  const [currentRoute, setCurrentRoute] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return getRouteFromPath(window.location.pathname);
    }
    return 'home';
  });

  const [user, setUser] = useState<{ name: string; email: string } | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  useEffect(() => {
    // Check user session
    fetchUserSession().then((session) => {
      if (session.authenticated && session.user) {
        setUser(session.user);
      }
    });

    // Listen to browser navigation (back/forward)
    const handlePopState = () => {
      setCurrentRoute(getRouteFromPath(window.location.pathname));
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleNavigate = (route: string) => {
    setCurrentRoute(route);
    const newPath = getPathFromRoute(route);
    if (window.location.pathname !== newPath) {
      window.history.pushState({}, '', newPath);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLogout = async () => {
    await authLogout();
    setUser(null);
  };

  const isChatRoute = currentRoute === 'chat';

  return (
    <div className="min-h-screen bg-bg text-text-primary flex flex-col relative selection:bg-accent-lime/20 selection:text-accent-lime transition-colors duration-200 overflow-x-hidden">
      {/* 1. Global Ambient Lighting Mesh */}
      <AmbientLighting />

      {/* 2. Top Glass Header */}
      <Navbar
        currentRoute={currentRoute}
        onNavigate={handleNavigate}
        onOpenAuthModal={() => setAuthModalOpen(true)}
        user={user}
        onLogout={handleLogout}
      />

      {/* 3. Main Workspace Destination Canvas */}
      <div className="flex-1 flex flex-col relative z-10">
        {currentRoute === 'home' && (
          <HomePage onNavigate={handleNavigate} />
        )}

        {currentRoute === 'chat' && (
          <ChatPage
            onNavigate={handleNavigate}
            user={user}
            onOpenAuthModal={() => setAuthModalOpen(true)}
          />
        )}

        {['dashboard', 'comparison', 'failures'].includes(currentRoute) && (
          <ResearchPage
            subRoute={currentRoute as 'dashboard' | 'comparison' | 'failures'}
            onNavigateSubRoute={handleNavigate}
          />
        )}

        {currentRoute === 'about' && (
          <AboutPage onNavigate={handleNavigate} />
        )}
      </div>

      {/* 4. Footer (Full-width pages) */}
      {!isChatRoute && <Footer />}

      {/* 5. Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={(u) => setUser(u)}
      />
    </div>
  );
};
