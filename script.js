// ===============================
// 47-and-SIX Frontend API Layer
// ===============================

const DEFAULT_API_BASE = "http://127.0.0.1:8000";

let apiBase = DEFAULT_API_BASE;

if (typeof window !== "undefined") {
    const runtimeBase = window.__API_BASE__;
    const storedBase = window.localStorage ? window.localStorage.getItem("api_base_url") : null;
    apiBase = runtimeBase || storedBase || DEFAULT_API_BASE;
}

export function setApiBase(url) {
    const next = (url || "").trim();
    if (!next) return apiBase;
    apiBase = next;
    if (typeof window !== "undefined" && window.localStorage) {
        window.localStorage.setItem("api_base_url", next);
    }
    return apiBase;
}

export function getApiBase() {
    return apiBase;
}

let authToken = "";

export function setAuthToken(token) {
    authToken = token || "";
}

export function clearAuthToken() {
    authToken = "";
}

function buildAuthHeaders(baseHeaders = {}) {
    if (!authToken) {
        return baseHeaders;
    }
    return {
        ...baseHeaders,
        Authorization: `Bearer ${authToken}`
    };
}

// Universal POST helper
async function postJSON(url, payload) {
    try {
        const res = await fetch(url, {
            method: "POST",
            headers: buildAuthHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            throw new Error(`Server returned ${res.status}`);
        }

        return await res.json();
    } catch (err) {
        console.error("API Error:", err);
        return { reply: "Sorry, something went wrong. Please try again." };
    }
}

export async function login(username, password) {
    const data = await postJSON(`${apiBase}/auth/login`, { username, password });
    if (data.access_token) {
        setAuthToken(data.access_token);
    }
    return data;
}

export async function getCurrentUser() {
    try {
        const res = await fetch(`${apiBase}/auth/me`, {
            headers: buildAuthHeaders({})
        });
        if (!res.ok) {
            throw new Error(`Server returned ${res.status}`);
        }
        return await res.json();
    } catch (err) {
        console.error("Auth Error:", err);
        return {};
    }
}

// ===============================
// Agent Calls
// ===============================

// Concierge Agent
export async function concierge(message) {
    return await postJSON(`${apiBase}/agents/concierge`, { message });
}

// Ops Agent
export async function ops(message) {
    return await postJSON(`${apiBase}/agents/ops`, { message });
}

// Logistics Agent
export async function logistics(message) {
    return await postJSON(`${apiBase}/agents/logistics`, { message });
}

// Economics Agent
export async function economics(message) {
    return await postJSON(`${apiBase}/agents/economics`, { message });
}

// Compliance Agent
export async function compliance(message) {
    return await postJSON(`${apiBase}/agents/compliance`, { message });
}

// Memory Agent
export async function memory(message) {
    return await postJSON(`${apiBase}/agents/memory`, { message });
}

// Menu Costing Agent
export async function menuCosting(message) {
    return await postJSON(`${apiBase}/agents/menu-costing`, { message });
}

// Recipe Agent
export async function recipeAgent(message) {
    return await postJSON(`${apiBase}/agents/recipe`, { message });
}

// Client Intake Agent
export async function clientIntake(message) {
    return await postJSON(`${apiBase}/agents/client-intake`, { message });
}

// Menu Pricing Engine (Economics + Logistics)
export async function menuPricing(message) {
    return await postJSON(`${apiBase}/agents/menu-pricing`, { message });
}

// RONIN Orchestrator
export async function ronin(task, message) {
    return await postJSON(`${apiBase}/agents/ronin`, { task, message });
}

// ===============================
// Chef Knowledge Endpoints
// ===============================

// List indexed AESOCA training files
export async function getChefFiles() {
    try {
        const res = await fetch(`${apiBase}/chef/knowledge/files`, {
            headers: buildAuthHeaders({})
        });
        return await res.json();
    } catch (err) {
        console.error("Knowledge Error:", err);
        return { items: [] };
    }
}

// Chef Portfolio (training summary)
export async function getChefPortfolio() {
    try {
        const res = await fetch(`${apiBase}/chef/knowledge/portfolio`, {
            headers: buildAuthHeaders({})
        });
        return await res.json();
    } catch (err) {
        console.error("Portfolio Error:", err);
        return { total_docs: 0, samples: [] };
    }
}

// Chef Credentials
export async function getChefCredentials() {
    try {
        const res = await fetch(`${apiBase}/chef/credentials`, {
            headers: buildAuthHeaders({})
        });
        return await res.json();
    } catch (err) {
        console.error("Credentials Error:", err);
        return {};
    }
}

// ===============================
// UI Helper for Pages
// ===============================

export async function handleAgentCall(agentFunction, inputId, outputId) {
    const input = document.getElementById(inputId).value;
    const output = document.getElementById(outputId);

    output.innerText = "Thinking...";

    const reply = await agentFunction(input);
    output.innerText = reply.reply;
}

