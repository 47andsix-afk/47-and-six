import { loadJSON } from "../js/site.js";

export async function render() {
  return `
    <section class="page-shell">
      <h1>AI Mise en Place Generator</h1>

      <div class="mep-builder">
        <label for="menu">Menu Description</label>
        <textarea id="menu" placeholder="Paste your menu here, e.g.:\n\n1. Pickled Shallots, Dill Oil, Compressed Cucumber\n2. Blanched Asparagus, Lemon Hollandaise\n3. Sous-vide Lamb, Reduced Stock, Charred Onion"></textarea>

        <label for="service-time">Service Time</label>
        <input id="service-time" type="time" value="18:00" />

        <label for="cook-count">Number of Cooks</label>
        <input id="cook-count" type="number" min="1" max="12" value="3" />

        <button id="generate-mep">Generate Mise en Place</button>

        <div id="mep-output" class="mep-output"></div>

        <button id="save-mep" class="hidden">Save to Portfolio</button>
      </div>
    </section>
  `;
}

export function afterRender() {
  document.getElementById("generate-mep").onclick = generateMEP;
  document.getElementById("save-mep").onclick = saveMEP;
}

async function generateMEP() {
  const menu = document.getElementById("menu").value;
  const serviceTime = document.getElementById("service-time").value;
  const cookCount = document.getElementById("cook-count").value;
  const output = document.getElementById("mep-output");
  const saveButton = document.getElementById("save-mep");

  output.innerHTML = `<p class="status-text">Generating mise en place plan...</p>`;
  saveButton.classList.add("hidden");

  const prompt = `
You are an expert chef and kitchen operations consultant.
Generate a complete mise en place plan based on:

Menu:
${menu}

Service Time:
${serviceTime}

Number of Cooks:
${cookCount}

Provide:
- mise en place checklist
- quantities
- storage instructions
- station assignments
- timing
- equipment notes
- prep dependencies
- service alignment
`;

  const res = await fetch("/agents/ollama", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "gemma", prompt }),
  });

  if (!res.ok) {
    output.innerHTML = `<p class="status-text error">Failed to generate mise en place plan.</p>`;
    return;
  }

  const data = await res.json();
  output.innerHTML = `<pre>${data.response || "No response received."}</pre>`;
  saveButton.classList.remove("hidden");
}

async function saveMEP() {
  const mepText = document.getElementById("mep-output").innerText;

  const newPortfolioItem = {
    project: "AI Mise en Place",
    image: "/static/fallback.jpg",
    role: "Kitchen Ops",
    date: new Date().getFullYear(),
    notes: mepText,
  };

  const res = await fetch("/admin/portfolio/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      token: localStorage.getItem("admin_token"),
    },
    body: JSON.stringify(newPortfolioItem),
  });

  if (!res.ok) {
    alert("Failed to save mise en place to portfolio.");
    return;
  }

  alert("Mise en place saved to portfolio.");
}
