import { initDarkMode, loadJSON } from "../js/site.js";

export async function render() {
  return `
    <section class="page-shell">
      <h1>AI Inventory & Ordering Assistant</h1>

      <div class="inventory-builder">
        <label for="menu">Menu</label>
        <textarea id="menu" placeholder="Paste your menu here"></textarea>

        <label for="covers">Expected Covers</label>
        <input id="covers" type="number" min="1" value="40" />

        <label for="vendors">Vendor Notes</label>
        <textarea id="vendors" placeholder="Optional: preferred vendors, constraints"></textarea>

        <button id="generate-inventory">Generate Inventory Plan</button>

        <div id="inventory-output" class="inventory-output"></div>

        <button id="save-inventory" class="hidden">Save to Portfolio</button>
      </div>
    </section>
  `;
}

export function afterRender() {
  document.getElementById("generate-inventory").onclick = generateInventory;
  document.getElementById("save-inventory").onclick = saveInventory;
}

async function generateInventory() {
  const menu = document.getElementById("menu").value;
  const covers = document.getElementById("covers").value;
  const vendors = document.getElementById("vendors").value;
  const output = document.getElementById("inventory-output");
  const saveButton = document.getElementById("save-inventory");

  output.innerHTML = `<p class="status-text">Generating inventory plan...</p>`;
  saveButton.classList.add("hidden");

  const prompt = `
You are an expert chef and purchasing manager.
Create a complete inventory and ordering plan based on:

Menu:
${menu}

Expected Covers:
${covers}

Vendor Notes:
${vendors}

Provide:
- ingredient list
- ordering quantities
- vendor breakdown
- cost estimate
- waste minimization plan
- par levels
- storage requirements
`;

  const res = await fetch("/agents/ollama", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "gemma", prompt })
  });

  if (!res.ok) {
    output.innerHTML = `<p class="status-text error">Failed to generate inventory plan.</p>`;
    return;
  }

  const data = await res.json();
  output.innerHTML = `<pre>${data.response || "No response received."}</pre>`;
  saveButton.classList.remove("hidden");
}

async function saveInventory() {
  const invText = document.getElementById("inventory-output").innerText;

  const newPortfolioItem = {
    project: "AI Inventory Plan",
    image: "/static/fallback.jpg",
    role: "Kitchen Ops",
    date: new Date().getFullYear(),
    notes: invText
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
    alert('Failed to save inventory plan to portfolio.');
    return;
  }

  alert("Inventory plan saved to portfolio.");
}
