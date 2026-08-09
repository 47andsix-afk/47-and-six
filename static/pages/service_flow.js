import { initDarkMode, loadJSON } from "../js/site.js";

export async function render() {
  return `
    <section class="page-shell">
      <h1>AI Service Flow Planner</h1>

      <div class="service-flow">
        <label for="menu">Menu</label>
        <textarea id="menu" placeholder="Paste your menu here"></textarea>

        <label for="stations">Station Layout</label>
        <textarea id="stations" placeholder="Example:\nGarde Manger\nHot Line\nGrill\nPastry"></textarea>

        <label>Service Window</label>
        <div style="display:flex; gap:8px; align-items:center;">
          <input id="service-start" type="time" value="18:00" />
          <input id="service-end" type="time" value="21:00" />
        </div>

        <button id="generate-flow">Generate Service Flow</button>

        <div id="flow-output" class="flow-output"></div>

        <button id="save-flow" class="hidden">Save to Portfolio</button>
      </div>
    </section>
  `;
}

export function afterRender() {
  document.getElementById("generate-flow").onclick = generateFlow;
  document.getElementById("save-flow").onclick = saveFlow;
}

async function generateFlow() {
  const menu = document.getElementById("menu").value;
  const stations = document.getElementById("stations").value;
  const start = document.getElementById("service-start").value;
  const end = document.getElementById("service-end").value;
  const output = document.getElementById("flow-output");
  const saveButton = document.getElementById("save-flow");

  output.innerHTML = `<p class="status-text">Generating service flow...</p>`;
  saveButton.classList.add("hidden");

  const prompt = `
You are an expert chef and kitchen operations consultant.
Create a complete service flow plan based on:

Menu:
${menu}

Stations:
${stations}

Service Window:
${start} to ${end}

Provide:
- ticket pacing
- station coordination
- plating rhythm
- recovery windows
- bottleneck mitigation
- service flow timeline
- chef-de-partie communication plan
`;

  const res = await fetch("/agents/ollama", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "gemma", prompt })
  });

  if (!res.ok) {
    output.innerHTML = `<p class="status-text error">Failed to generate service flow.</p>`;
    return;
  }

  const data = await res.json();
  output.innerHTML = `<pre>${data.response || "No response received."}</pre>`;
  saveButton.classList.remove("hidden");
}

async function saveFlow() {
  const flowText = document.getElementById("flow-output").innerText;

  const newPortfolioItem = {
    project: "AI Service Flow",
    image: "/static/fallback.jpg",
    role: "Kitchen Ops",
    date: new Date().getFullYear(),
    notes: flowText
  };

  const res = await fetch("/admin/portfolio/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      token: localStorage.getItem("admin_token")
    },
    body: JSON.stringify(newPortfolioItem)
  });

  if (!res.ok) {
    alert('Failed to save service flow to portfolio.');
    return;
  }

  alert("Service flow saved to portfolio.");
}
