const sourceText = document.querySelector('#source-text');
const wordCount = document.querySelector('#word-count');
const summaryOutput = document.querySelector('#summary-output');
const resultMeta = document.querySelector('#result-meta');
const errorMessage = document.querySelector('#error-message');
const summarizeButton = document.querySelector('#summarize-button');
const styleSelect = document.querySelector('#style-select');

function updateWordCount() {
  const count = sourceText.value.trim() ? sourceText.value.trim().split(/\s+/).length : 0;
  wordCount.textContent = `${count.toLocaleString()} words`;
}

sourceText.addEventListener('input', updateWordCount);
document.querySelector('#clear-button').addEventListener('click', () => {
  sourceText.value = '';
  updateWordCount();
  sourceText.focus();
});

document.querySelector('#copy-button').addEventListener('click', async () => {
  const text = summaryOutput.textContent.trim();
  if (!text || text === 'Your summary will appear here. Everything runs on your machine.') return;
  await navigator.clipboard.writeText(text);
  resultMeta.textContent = 'Copied to clipboard';
  setTimeout(() => { resultMeta.textContent = 'Summary ready'; }, 1600);
});

summarizeButton.addEventListener('click', async () => {
  const text = sourceText.value.trim();
  errorMessage.textContent = '';
  if (text.length < 80) {
    errorMessage.textContent = 'Add at least 80 characters so Qwen has enough context to work with.';
    sourceText.focus();
    return;
  }
  summarizeButton.disabled = true;
  summarizeButton.querySelector('span:first-child').textContent = 'Thinking...';
  resultMeta.textContent = 'Qwen is reading';
  summaryOutput.innerHTML = '<div class="empty-state"><span class="empty-icon">...</span><p>Finding the signal...</p><small>This may take a moment on first run.</small></div>';
  try {
    const response = await fetch('/api/summarize/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify({ text, style: styleSelect.value }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Something went wrong.');
    summaryOutput.textContent = data.summary;
    resultMeta.textContent = 'Summary ready';
  } catch (error) {
    summaryOutput.innerHTML = '<div class="empty-state"><span class="empty-icon">!</span><p>Could not create a summary.</p><small>See the message below for the next step.</small></div>';
    resultMeta.textContent = 'Needs attention';
    errorMessage.textContent = error.message;
  } finally {
    summarizeButton.disabled = false;
    summarizeButton.querySelector('span:first-child').textContent = 'Summarize text';
  }
});

function getCookie(name) {
  return document.cookie.split('; ').find(row => row.startsWith(`${name}=`))?.split('=')[1] || '';
}

updateWordCount();
