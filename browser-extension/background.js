const CONTENT_FILES = ['core.js', 'content.js'];

async function inject(tabId) {
  await chrome.scripting.executeScript({ target: { tabId }, files: CONTENT_FILES });
}

async function sendToTab(tabId, message) {
  await inject(tabId);
  const { floating } = await chrome.storage.local.get({ floating: false });
  if (floating) await chrome.tabs.sendMessage(tabId, { type: 'floating', enabled: true });
  return chrome.tabs.sendMessage(tabId, message);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== 'translator-command') return;
  const tabId = message.tabId || sender.tab?.id;
  if (!tabId) { sendResponse({ ok: false, error: 'No active tab.' }); return; }
  sendToTab(tabId, message.command)
    .then((result) => sendResponse({ ok: true, result }))
    .catch((error) => sendResponse({ ok: false, error: error.message || 'Unable to reach this page.' }));
  return true;
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo) => {
  if (changeInfo.status !== 'complete') return;
  const { autoTranslate, targetLang } = await chrome.storage.local.get({ autoTranslate: false, targetLang: 'hi' });
  if (!autoTranslate) return;
  try {
    await sendToTab(tabId, { type: 'translate', targetLang, automatic: true });
  } catch (_) {
    // Browser-internal and restricted pages cannot host content scripts.
  }
});
