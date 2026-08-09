async function testAdmin() {
  const token = localStorage.getItem('admin_token') || 'YOUR_ADMIN_TOKEN';

  try {
    const res = await fetch('/admin/gallery', {
      headers: { token }
    });
    console.log('Admin Test:', res.status);
    if (res.ok) console.log(await res.text());
  } catch (e) {
    console.error('Admin Test Error:', e);
  }
}

if (typeof window !== 'undefined') testAdmin();
else console.log('Run this file in a browser context (e.g., open in devtools).');
