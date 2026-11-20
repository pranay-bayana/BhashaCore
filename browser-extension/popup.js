const $ = (id) => document.getElementById(id);
let tabId;

const labels = { original: 'Original', translating: 'Translating…', translated: 'Translated', partial: 'Partially translated', failed: 'Translation failed' };
function setStatus(status, error) { $('status').textContent = error || labels[status] || status; }
async function command(command) {
  return chrome.runtime.sendMessage({ type: 'translator-command', tabId, command });
}
async function refresh() {
  const response = await command({ type: 'status' });
  if (response.ok) setStatus(response.result.status);
}

(async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  tabId = tab?.id;
  try { $('domain').textContent = new URL(tab.url).hostname || 'Current website'; } catch (_) { $('domain').textContent = 'Restricted page'; }
  const prefs = await chrome.storage.local.get({ targetLang: 'hi', autoTranslate: false, floating: false });
  $('language').value = prefs.targetLang; $('auto').checked = prefs.autoTranslate; $('floating').checked = prefs.floating;
  $('language').addEventListener('change', () => chrome.storage.local.set({ targetLang: $('language').value }));
  $('auto').addEventListener('change', async () => {
    if ($('auto').checked) {
      // Active-tab access is enough for a manual click. Auto-translation needs
      // an explicit, user-approved optional host permission for future pages.
      const granted = await chrome.permissions.request({ origins: ['http://*/*', 'https://*/*'] });
      if (!granted) {
        $('auto').checked = false;
        setStatus('failed', 'Allow site access to enable auto-translate.');
      }
    }
    await chrome.storage.local.set({ autoTranslate: $('auto').checked });
  });
  $('floating').addEventListener('change', async () => { await chrome.storage.local.set({ floating: $('floating').checked }); await command({ type: 'floating', enabled: $('floating').checked }); });
  $('translate').addEventListener('click', async () => {
    $('translate').disabled = true; setStatus('translating');
    const response = await command({ type: 'translate', targetLang: $('language').value });
    $('translate').disabled = false; setStatus(response.result?.status || 'failed', response.result?.error || response.error);
  });
  $('restore').addEventListener('click', async () => { const response = await command({ type: 'restore' }); setStatus(response.result?.status || 'failed', response.error); });
  if (tabId) refresh().catch(() => setStatus('failed', 'This page cannot be translated.'));
})();
