import { initDarkMode } from "./site.js";

// Global router error logging
window.onerror = (msg, url, line, col, err) => {
  console.error("Router Error:", msg, url, line, col, err);
};

const routes = {
  "/": "/static/pages/home.js",
  "/pic": "/static/pages/gallery.js",
  "/class_menu": "/static/pages/menu.js",
  "/services": "/static/pages/services.js",
  "/portfolio": "/static/pages/portfolio.js",
  "/ollama": "/static/pages/ollama.js",
  "/menu_builder": "/static/pages/menu_builder.js",
  "/workflow": "/static/pages/workflow.js",
  "/load_balancer": "/static/pages/load_balancer.js",
  "/prep_timing": "/static/pages/prep_timing.js",
  "/mise_en_place": "/static/pages/mise_en_place.js",
  "/service_flow": "/static/pages/service_flow.js",
  "/inventory": "/static/pages/inventory.js",
};

async function loadRoute(path) {
  const modulePath = routes[path] || routes["/"];
  let pageModule;
  try {
    pageModule = await import(modulePath);
  } catch (e) {
    console.error('Failed to load module', modulePath, e);
    // Fallback to home
    pageModule = await import(routes["/"]);
  }
  const app = document.getElementById("app");
  if (!app) return;
  app.classList.remove("loaded");
  app.innerHTML = await pageModule.render();
  if (pageModule.afterRender) pageModule.afterRender();
  setTimeout(() => app.classList.add("loaded"), 10);
}

function navigate(path) {
  history.pushState({}, "", path);
  loadRoute(path);
}

window.onpopstate = () => loadRoute(location.pathname);

document.addEventListener("DOMContentLoaded", () => {
  initDarkMode();
  loadRoute(location.pathname);
});

window.navigate = navigate;
