const test = require('node:test');
const assert = require('node:assert/strict');
const Core = require('../core.js');
const manifest = require('../manifest.json');

test('manifest uses minimal defaults with opt-in access for auto translation', () => {
  assert.deepEqual(manifest.permissions, ['activeTab', 'scripting', 'storage']);
  assert.deepEqual(manifest.optional_host_permissions, ['http://*/*', 'https://*/*']);
  assert.equal(manifest.manifest_version, 3);
});

test('only safe visible-text candidates qualify', () => {
  assert.equal(Core.isEligibleText(' Hello ', 'p', false), true);
  assert.equal(Core.isEligibleText('const x = 1', 'code', false), false);
  assert.equal(Core.isEligibleText('x', 'input', false), false);
  assert.equal(Core.isEligibleText(' ', 'p', false), false);
});

test('batching observes both count and payload limits', () => {
  const items = Array.from({ length: 45 }, (_, i) => ({ id: String(i), text: 'x'.repeat(300) }));
  const groups = Core.batch(items, 40, 12000);
  assert.deepEqual(groups.map((group) => group.length), [40, 5]);
});

test('response mapping rejects duplicate, missing, and unexpected ids', () => {
  const expected = new Set(['a', 'b']);
  assert.deepEqual([...Core.validateResponse({ translations: [{ id: 'b', text: 'B' }, { id: 'a', text: 'A' }] }, expected)], [['b', 'B'], ['a', 'A']]);
  assert.throws(() => Core.validateResponse({ translations: [{ id: 'a', text: 'A' }, { id: 'a', text: 'Again' }] }, expected));
  assert.throws(() => Core.validateResponse({ translations: [{ id: 'a', text: 'A' }] }, expected));
});
