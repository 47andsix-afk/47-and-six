async function testAI() {
  try {
    const res = await fetch('/agents/ollama', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'gemma', prompt: 'Hello' })
    });
    if (!res.ok) {
      console.error('AI endpoint HTTP', res.status);
      return;
    }
    const data = await res.json();
    console.log('AI Test:', data.response || data);
  } catch (e) {
    console.error('AI Test Error:', e);
  }
}

if (typeof window !== 'undefined') testAI();
else console.log('Run this file in a browser context (e.g., open in devtools).');
