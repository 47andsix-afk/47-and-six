import { loadJSON } from "../js/site.js";

export async function render() {
  return `
    <section class="page-shell">
      <h1>AI Prep Timing Calculator</h1>

      <div class="prep-timing">
        <label for="prep">Prep List</label>
        <textarea id="prep" placeholder="Example:\nPickled shallots\nBlanched asparagus\nReduced stock\nSous-vide lamb"></textarea>

        <label for="skill">Cook Skill Level</label>
        <select id="skill">
          <option value="Beginner">Beginner</option>
          <option value="Intermediate">Intermediate</option>
          <option value="Advanced">Advanced</option>
        </select>

        <label for="equipment">Equipment Available</label>
        <textarea id="equipment" placeholder="Example:\nSous-vide machine\nBlast chiller\nOne induction burner\nTwo ovens"></textarea>

        <label for="service-time">Service Time</label>
        <input id="service-time" type="time" value="18:00" />

        <button id="calculate-prep">Calculate Prep Timeline</button>

        <div id="prep-output" class="prep-output"></div>

        <button id="save-prep" class="hidden">Save to Portfolio</button>
      </div>
    </section>
  `;
}

export function afterRender() {
  document.getElementById("calculate-prep").onclick = calculatePrep;
  document.getElementById("save-prep").onclick = savePrep;
}

async function calculatePrep() {
  const prep = document.getElementById("prep").value;
  const skill = document.getElementById("skill").value;
  const equipment = document.getElementById("equipment").value;
  const serviceTime = document.getElementById("service-time").value;
  const output = document.getElementById("prep-output");
  const saveButton = document.getElementById("save-prep");

  output.innerHTML = `<p class="status-text">Calculating prep timeline...</p>`;
  saveButton.classList.add("hidden");

  const prompt = `
You are an expert kitchen operations consultant.
Calculate a complete prep timeline based on:

Prep List:
${prep}

Cook Skill Level:
${skill}

Equipment Available:
${equipment}

Service Time:
${serviceTime}

Provide:
- estimated prep durations for each item
- parallelizable tasks
- critical path
- slack time
- optimized prep timeline
- equipment constraints
- efficiency recommendations
`;

  const res = await fetch("/agents/ollama", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "gemma", prompt }),
  });

  if (!res.ok) {
    output.innerHTML = `<p class="status-text error">Failed to calculate prep timeline.</p>`;
    return;
  }

  const data = await res.json();
  output.innerHTML = `<pre>${data.response || "No response received."}</pre>`;
  saveButton.classList.remove("hidden");
}

async function savePrep() {
  const prepText = document.getElementById("prep-output").innerText;

  const newPortfolioItem = {
    project: "AI Prep Timing",
    image: "/static/fallback.jpg",
    role: "Kitchen Ops",
    date: new Date().getFullYear(),
    notes: prepText,
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
    alert("Failed to save prep timing to portfolio.");
    return;
  }

  alert("Prep timing saved to portfolio.");
}
