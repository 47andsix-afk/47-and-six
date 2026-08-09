async function testSPA() {
  const routes = [
    "/", "/pic", "/class_menu", "/services", "/portfolio",
    "/ollama", "/menu_builder", "/workflow", "/load_balancer",
    "/prep_timing", "/mise_en_place", "/service_flow", "/inventory"
  ];

  for (const r of routes) {
    try {
      const res = await fetch(r);
      console.log(r, res.status);
    } catch (e) {
      console.error(r, 'ERROR', e);
    }
  }
}

if (typeof window !== 'undefined') testSPA();
else console.log('Run this file in a browser context (e.g., open in devtools).');
