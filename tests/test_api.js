async function testAPI() {
  const endpoints = [
    "/homepage", "/gallery", "/menu", "/services", "/portfolio"
  ];

  for (const e of endpoints) {
    try {
      const res = await fetch(e);
      if (!res.ok) {
        console.error(e, 'HTTP', res.status);
        continue;
      }
      const json = await res.json();
      console.log(e, json ? 'OK' : 'FAIL');
    } catch (err) {
      console.error(e, 'ERROR', err);
    }
  }
}

if (typeof window !== 'undefined') testAPI();
else console.log('Run this file in a browser context (e.g., open in devtools).');
