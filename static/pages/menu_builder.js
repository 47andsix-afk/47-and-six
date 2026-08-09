import { loadJSON } from "../js/site.js";

export async function render() {
  return `
    <section class="page-shell">
      <h1>AI Menu Builder</h1>

      <div class="menu-builder">
        <label for="cuisine">Cuisine</label>
        <select id="cuisine">
          <option value="Nordic">Nordic</option>
          <option value="Japanese">Japanese</option>
          <option value="French">French</option>
          <option value="Modern American">Modern American</option>
          <option value="Mediterranean">Mediterranean</option>
        </select>

        <label for="difficulty">Difficulty</label>
        <select id="difficulty">
          <option value="Beginner">Beginner</option>
          <option value="Intermediate">Intermediate</option>
          <option value="Advanced">Advanced</option>
        </select>

        <label for="courses">Number of Courses</label>
        <input id="courses" type="number" min="1" max="12" value="5" />

        <button id="generate-menu">Generate Menu</button>

        <div id="menu-output" class="menu-output"></div>

        <button id="save-menu" class="hidden">Save to Portfolio</button>
      </div>
    </section>
  `;
}

export function afterRender() {
  document.getElementById("generate-menu").onclick = generateMenu;
  document.getElementById("save-menu").onclick = saveMenu;
}

async function generateMenu() {
  const cuisine = document.getElementById("cuisine").value;
  const difficulty = document.getElementById("difficulty").value;
  const courses = document.getElementById("courses").value;
  const output = document.getElementById("menu-output");
  const saveButton = document.getElementById("save-menu");

  output.innerHTML = `<p class="status-text">Generating menu...</p>`;
  saveButton.classList.add("hidden");

  const prompt = `
Create a ${courses}-course tasting menu.
Cuisine: ${cuisine}
Difficulty: ${difficulty}
Include:
- course name
- short description
- plating style
- flavor profile
- mood
`;

  const res = await fetch("/agents/ollama", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "gemma", prompt }),
  });

  if (!res.ok) {
    output.innerHTML = `<p class="status-text error">Failed to generate menu.</p>`;
    return;
  }

  const data = await res.json();
  output.innerHTML = `<pre>${data.response || "No response received."}</pre>`;
  saveButton.classList.remove("hidden");
}

async function saveMenu() {
  const menuText = document.getElementById("menu-output").innerText;

  const newPortfolioItem = {
    project: "AI Generated Menu",
    image: "/static/fallback.jpg",
    role: "Menu Designer",
    date: `${new Date().getFullYear()}`,
    notes: menuText,
    tags: ["AI menu", "generated", "tasting menu"],
    caption: "An AI-generated tasting menu created by the 47-&-SIX chef assistant.",
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
    alert("Failed to save menu to portfolio.");
    return;
  }

  alert("Menu saved to portfolio.");
}
