import { loadJSON } from "../js/site.js";

export async function render() {
  return `
    <section class="page-shell">
      <h1>AI Kitchen Workflow Optimizer</h1>

      <div class="workflow-builder">
        <label for="stations">Station Layout</label>
        <textarea id="stations" placeholder="Example:\n- Garde Manger\n- Hot Line\n- Grill\n- Pastry"></textarea>

        <label for="prep">Prep List</label>
        <textarea id="prep" placeholder="Example:\n- Pickled shallots\n- Blanched asparagus\n- Reduced stock\n- Sous-vide lamb"></textarea>

        <label for="timing">Timing Constraints</label>
        <textarea id="timing" placeholder="Example:\n- Service at 6:00 PM\n- 2 cooks available\n- Grill station overloaded"></textarea>

        <button id="generate-workflow">Generate Workflow</button>

        <div id="workflow-output" class="workflow-output"></div>

        <button id="save-workflow" class="hidden">Save to Portfolio</button>
      </div>
    </section>
  `;
}

export function afterRender() {
  document.getElementById("generate-workflow").onclick = generateWorkflow;
  document.getElementById("save-workflow").onclick = saveWorkflow;
}

async function generateWorkflow() {
  const stations = document.getElementById("stations").value;
  const prep = document.getElementById("prep").value;
  const timing = document.getElementById("timing").value;
  const output = document.getElementById("workflow-output");
  const saveButton = document.getElementById("save-workflow");

  output.innerHTML = `<p class="status-text">Generating workflow...</p>`;
  saveButton.classList.add("hidden");

  const prompt = `
You are an expert kitchen operations consultant.
Create a complete workflow plan based on:

Stations:
${stations}

Prep List:
${prep}

Timing Constraints:
${timing}

Include:
- optimized prep order
- station flow
- timing chart
- mise en place checklist
- bottleneck analysis
- efficiency recommendations
`;

  const res = await fetch("/agents/ollama", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "gemma", prompt }),
  });

  if (!res.ok) {
    output.innerHTML = `<p class="status-text error">Failed to generate workflow.</p>`;
    return;
  }

  const data = await res.json();
  output.innerHTML = `<pre>${data.response || "No response received."}</pre>`;
  saveButton.classList.remove("hidden");
}

async function saveWorkflow() {
  const workflowText = document.getElementById("workflow-output").innerText;

  const newPortfolioItem = {
    project: "AI Kitchen Workflow",
    image: "/static/fallback.jpg",
    role: "Kitchen Ops",
    date: new Date().getFullYear(),
    notes: workflowText,
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
    alert("Failed to save workflow to portfolio.");
    return;
  }

  alert("Workflow saved to portfolio.");
}
