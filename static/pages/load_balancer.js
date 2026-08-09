import { loadJSON } from "../js/site.js";

export async function render() {
  return `
    <section class="page-shell">
      <h1>AI Station Load Balancer</h1>

      <div class="load-balancer">
        <label for="stations">Station Layout</label>
        <textarea id="stations" placeholder="Example:\n- Garde Manger\n- Hot Line\n- Grill\n- Pastry"></textarea>

        <label for="tasks">Prep Tasks with Assigned Stations</label>
        <textarea id="tasks" placeholder="Example:\nPickled shallots — Garde Manger\nBlanched asparagus — Hot Line\nReduced stock — Hot Line\nSous-vide lamb — Grill"></textarea>

        <label for="timing">Timing Constraints</label>
        <textarea id="timing" placeholder="Example:\nService at 6:00 PM\nGrill station overloaded\nPastry understaffed"></textarea>

        <button id="balance-stations">Balance Stations</button>

        <div id="balance-output" class="balance-output"></div>

        <button id="save-balance" class="hidden">Save to Portfolio</button>
      </div>
    </section>
  `;
}

export function afterRender() {
  document.getElementById("balance-stations").onclick = balanceStations;
  document.getElementById("save-balance").onclick = saveBalance;
}

async function balanceStations() {
  const stations = document.getElementById("stations").value;
  const tasks = document.getElementById("tasks").value;
  const timing = document.getElementById("timing").value;
  const output = document.getElementById("balance-output");
  const saveButton = document.getElementById("save-balance");

  output.innerHTML = `<p class="status-text">Analyzing station loads...</p>`;
  saveButton.classList.add("hidden");

  const prompt = `
You are an expert kitchen operations consultant.
Analyze the following station layout, assigned tasks, and timing constraints.
Identify overloaded stations, underutilized stations, bottlenecks, and inefficiencies.

Stations:
${stations}

Tasks:
${tasks}

Timing Constraints:
${timing}

Provide:
- station load analysis
- bottleneck identification
- redistribution of tasks
- staffing recommendations
- equipment reallocation
- timing adjustments
- final optimized station plan
`;

  const res = await fetch("/agents/ollama", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "gemma", prompt }),
  });

  if (!res.ok) {
    output.innerHTML = `<p class="status-text error">Failed to balance stations.</p>`;
    return;
  }

  const data = await res.json();
  output.innerHTML = `<pre>${data.response || "No response received."}</pre>`;
  saveButton.classList.remove("hidden");
}

async function saveBalance() {
  const balanceText = document.getElementById("balance-output").innerText;

  const newPortfolioItem = {
    project: "AI Station Load Balance",
    image: "/static/fallback.jpg",
    role: "Kitchen Ops",
    date: new Date().getFullYear(),
    notes: balanceText,
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
    alert("Failed to save station balance to portfolio.");
    return;
  }

  alert("Station balance saved to portfolio.");
}
