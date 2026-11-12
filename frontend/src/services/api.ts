import {
  ChatStreamEvent,
  ChatHistoryItem,
  DashboardData,
  ComparisonData,
  FailuresResponse,
  UserSession,
  GuestStatus,
} from '@/types/api';

let cachedCsrfToken: string | null = null;
let mustRefreshCsrfToken = false;

/** A login/logout rotates the Flask session, so its old CSRF token is invalid. */
export function clearCsrfToken(): void {
  cachedCsrfToken = null;
  mustRefreshCsrfToken = true;
}

export async function getCsrfToken(forceRefresh = false): Promise<string> {
  if (!forceRefresh && !mustRefreshCsrfToken && cachedCsrfToken) return cachedCsrfToken;

  // The rendered token belongs to the session that served the page.  Never
  // reuse it after sign-in/sign-out rotates the Flask session.
  if (!forceRefresh && !mustRefreshCsrfToken && typeof document !== 'undefined') {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) {
      const content = meta.getAttribute('content');
      if (content) {
        cachedCsrfToken = content;
        return content;
      }
    }
  }

  // 2. Fetch from backend endpoint
  try {
    const res = await fetch('/api/csrf-token', { credentials: 'same-origin' });
    if (res.ok) {
      const data = await res.json();
      if (data.csrf_token) {
        cachedCsrfToken = data.csrf_token;
        mustRefreshCsrfToken = false;
        return data.csrf_token;
      }
    }
  } catch (_) {}

  return '';
}

export interface StreamChatParams {
  question: string;
  session_id: string;
  input_lang?: string;
  input_style?: string;
  answer_lang?: string;
  answer_script?: string;
  mode?: string;
  eval_mode?: boolean;
}

export async function streamChat(
  params: StreamChatParams,
  onEvent: (event: ChatStreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const sendRequest = (csrfToken: string) => fetch('/api/chat', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({
      question: params.question,
      session_id: params.session_id,
      input_lang: params.input_lang || 'auto',
      input_style: params.input_style || 'auto',
      answer_lang: params.answer_lang === 'auto' ? null : (params.answer_lang || null),
      answer_script: params.answer_script || 'native',
      mode: params.mode || 'rag',
      eval_mode: params.eval_mode || false,
    }),
    signal,
  });

  let res = await sendRequest(await getCsrfToken());

  // A CSRF rejection happens before Flask enters the chat handler, therefore
  // no provider request or guest reservation exists yet. One fresh-token
  // retry is safe and prevents a session rotation from stranding the composer.
  if (res.status === 400) {
    const csrfError = await res.clone().json().catch(() => null);
    if (csrfError?.error === 'csrf_invalid') {
      res = await sendRequest(await getCsrfToken(true));
    }
  }

  if (!res.ok) {
    let errMessage = `Error: ${res.statusText} (${res.status})`;
    let code = 'request_failed';
    let retryable = false;
    try {
      const errJson = await res.json();
      if (errJson && errJson.error) {
        code = errJson.error;
        errMessage = errJson.message || errJson.error;
        retryable = Boolean(errJson.retryable);
      }
    } catch (_) {}
    onEvent({ type: 'error', error: code, message: errMessage, retryable });
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    onEvent({ type: 'error', error: 'Streaming response body is unavailable' });
    return;
  }

  const decoder = new TextDecoder('utf-8');
  let buffer = '';
  let terminalEventReceived = false;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        const event = JSON.parse(trimmed) as ChatStreamEvent;
        if (event.type === 'done' || event.type === 'error') terminalEventReceived = true;
        onEvent(event);
      } catch (e) {
        console.warn('Failed to parse NDJSON line:', trimmed, e);
      }
    }
  }

  if (buffer.trim()) {
    try {
      const event = JSON.parse(buffer.trim()) as ChatStreamEvent;
      if (event.type === 'done' || event.type === 'error') terminalEventReceived = true;
      onEvent(event);
    } catch (_) {}
  }

  if (!terminalEventReceived) {
    onEvent({
      type: 'error',
      error: 'provider_incomplete_stream',
      message: 'The AI response ended before completion. Please retry once.',
      retryable: true,
    });
  }
}

export async function stopChat(sessionId: string): Promise<void> {
  const csrfToken = await getCsrfToken();
  await fetch('/api/stop', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function newChat(sessionId?: string): Promise<{ session_id: string }> {
  try {
    const csrfToken = await getCsrfToken();
    const res = await fetch('/api/new-chat', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ session_id: sessionId }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.session_id) return data;
    }
  } catch (err) {
    console.warn('API new-chat call error, using fallback ID:', err);
  }
  return { session_id: sessionId || `sess-${Date.now()}` };
}

export async function fetchHistory(): Promise<ChatHistoryItem[]> {
  try {
    const res = await fetch('/api/history', { credentials: 'same-origin' });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.histories || []).map((h: any) => ({
      id: h.session_id || h.id,
      session_id: h.session_id || h.id,
      title: h.title || 'Untitled',
      created: h.created || Date.now() / 1000,
      updated_at: h.updated_at || h.created,
    }));
  } catch (_) {
    return [];
  }
}

export async function renameConversation(conversationId: string, title: string): Promise<boolean> {
  const csrfToken = await getCsrfToken();
  const res = await fetch(`/api/conversations/${conversationId}`, {
    method: 'PATCH',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ title }),
  });
  return res.ok;
}

export async function deleteConversation(conversationId: string): Promise<boolean> {
  const csrfToken = await getCsrfToken();
  const res = await fetch(`/api/conversations/${conversationId}`, {
    method: 'DELETE',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
  });
  return res.ok;
}

export async function loadChat(sessionId: string): Promise<any> {
  const csrfToken = await getCsrfToken();
  const res = await fetch('/api/load-chat', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) return null;
  return res.json();
}

export async function fetchDashboard(): Promise<DashboardData | null> {
  try {
    const res = await fetch('/api/dashboard', { credentials: 'same-origin' });
    if (!res.ok) return null;
    return res.json();
  } catch (_) {
    return null;
  }
}

export async function fetchComparison(): Promise<ComparisonData | null> {
  try {
    const res = await fetch('/api/comparison', { credentials: 'same-origin' });
    if (!res.ok) return null;
    return res.json();
  } catch (_) {
    return null;
  }
}

export async function fetchFailures(lang?: string, mode?: string, limit = 50): Promise<FailuresResponse | null> {
  try {
    const params = new URLSearchParams();
    if (lang && lang !== 'all') params.set('lang', lang);
    if (mode && mode !== 'all') params.set('mode', mode);
    params.set('limit', String(limit));
    const res = await fetch(`/api/failures?${params.toString()}`, { credentials: 'same-origin' });
    if (!res.ok) return null;
    return res.json();
  } catch (_) {
    return null;
  }
}

export async function fetchUserSession(): Promise<UserSession> {
  try {
    const res = await fetch('/api/auth/me', { credentials: 'same-origin' });
    if (res.ok) {
      return res.json();
    }
  } catch (_) {}
  return { authenticated: false, user: null };
}

export async function fetchGuestStatus(): Promise<GuestStatus> {
  try {
    const res = await fetch('/api/guest-status', { credentials: 'same-origin' });
    if (res.ok) {
      return res.json();
    }
  } catch (_) {}
  return {
    authenticated: false,
    guest_message_count: 0,
    guest_limit: 3,
    guest_remaining: 3,
    guest_quota_reached: false,
  };
}

export async function authLogout(): Promise<void> {
  const csrfToken = await getCsrfToken();
  try {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
    });
    clearCsrfToken();
  } catch (_) {}
}
