import React, { useState } from 'react';
import { useLanguage } from '@/localization/LanguageContext';
import { clearCsrfToken, getCsrfToken } from '@/services/api';
import { X, Lock, Mail, User, Loader2, Sparkles, AlertCircle } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: { name: string; email: string }) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { t } = useLanguage();
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const csrfToken = await getCsrfToken();
      const endpoint = mode === 'signin' ? '/api/auth/signin' : '/api/auth/signup';
      const payload: Record<string, string> = { email, password };

      if (mode === 'signup') {
        if (password !== confirmPassword) {
          setError(t('auth_password_mismatch') || 'Passwords do not match');
          setLoading(false);
          return;
        }
        payload.name = name;
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const body = await res.json();
        if (!body?.user?.name || !body?.user?.email) {
          throw new Error('Authentication response was incomplete.');
        }
        clearCsrfToken();
        // Fetch against the new session before chat can issue a mutation.
        await getCsrfToken(true);
        onSuccess(body.user);
        onClose();
      } else {
        const body = await res.json().catch(() => null);
        setError(body?.error || (mode === 'signin' ? (t('auth_invalid_credentials') || 'Invalid email or password.') : (t('auth_error_create') || 'Could not create account. Please try again.')));
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during authentication.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div id="authModal" className="relative w-full max-w-md glass-elevated rounded-3xl border border-border-subtle p-6 sm:p-8 shadow-glass-lg z-10 animate-in fade-in zoom-in-95 duration-200">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-xl glass-subtle hover:bg-black/05 dark:hover:bg-white/10 text-text-muted hover:text-text-primary transition-colors border border-border-subtle"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="text-center space-y-2 mb-6">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#B7FF72] to-[#36D69A] flex items-center justify-center text-[#050706] font-extrabold mx-auto shadow-sm">
            B
          </div>
          <h3 className="text-xl font-bold text-text-primary tracking-tight">
            {mode === 'signin' ? (t('auth_sign_in') || 'Sign In') : (t('auth_sign_up') || 'Create Account')}
          </h3>
          <p className="text-xs text-text-secondary">
            {t('auth_workspace') || 'Sign in to sync conversation history across devices.'}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'signup' && (
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">
                {t('auth_full_name') || 'Full Name'}
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t('auth_name_placeholder') || 'Your Name'}
                  className="w-full bg-black/05 dark:bg-white/[0.04] border border-border-subtle rounded-xl pl-9 pr-3 py-2 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent-lime"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">
              {t('auth_email') || 'Email Address'}
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t('auth_email_placeholder') || 'researcher@example.com'}
                className="w-full bg-black/05 dark:bg-white/[0.04] border border-border-subtle rounded-xl pl-9 pr-3 py-2 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent-lime"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">
              {t('auth_password') || 'Password'}
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                type="password"
                required
                minLength={12}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t('auth_password_placeholder') || 'At least 12 characters'}
                className="w-full bg-black/05 dark:bg-white/[0.04] border border-border-subtle rounded-xl pl-9 pr-3 py-2 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent-lime"
              />
            </div>
          </div>

          {mode === 'signup' && (
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">
                {t('auth_confirm_password') || 'Confirm Password'}
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                <input
                  type="password"
                  required
                  minLength={12}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder={t('auth_confirm_password') || 'Repeat password'}
                  className="w-full bg-black/05 dark:bg-white/[0.04] border border-border-subtle rounded-xl pl-9 pr-3 py-2 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent-lime"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-lime-glass py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 mt-2 shadow-sm"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>{mode === 'signin' ? (t('auth_sign_in') || 'Sign In to Workspace') : (t('auth_create_account') || 'Create Free Account')}</span>
          </button>
        </form>

        <div className="mt-5 text-center text-xs text-text-secondary">
          {mode === 'signin' ? (
            <p>
              {t('auth_dont_have_account') || t('auth_no_account') || "Don't have an account?"}{' '}
              <button
                type="button"
                onClick={() => { setMode('signup'); setError(null); }}
                className="text-accent-lime hover:underline font-semibold"
              >
                {t('auth_sign_up') || 'Sign up'}
              </button>
            </p>
          ) : (
            <p>
              {t('auth_already_have_account') || t('auth_have_account') || 'Already have an account?'}{' '}
              <button
                type="button"
                onClick={() => { setMode('signin'); setError(null); }}
                className="text-accent-lime hover:underline font-semibold"
              >
                {t('auth_sign_in') || 'Sign in'}
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
