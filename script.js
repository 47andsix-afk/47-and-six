// Telemetry Animation
window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const bar = document.getElementById('efficiency-bar');
        if(bar) bar.style.width = '99.9%';
    }, 1000);
});

// Front-of-House AI Concierge Logic
const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');

// Automated Response Matrix
const responseMatrix = {
    'catering': "> Routing to CU132 protocol. We scale menus from 10 to 500 covers based on the 6-minute interval. Please specify date and headcount.",
    'menu': "> Extracting CE187 data. Menus are dynamic and subject to local agricultural yields (CU222). Do you require specific dietary parameters?",
    'contact': "> Establishing direct link to Executive Chef. Operational radius: El Paso, TX. Awaiting further transmission.",
    'default': "> Inquiry received. Parsing semantic data. A 47-&-SIX operative will review this log."
};

function transmitMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Echo user input
    const userDiv = document.createElement('div');
    userDiv.className = 'user-message';
    userDiv.textContent = text;
    chatLog.appendChild(userDiv);

    // Clear input
    chatInput.value = '';
    chatLog.scrollTop = chatLog.scrollHeight;

    // Simulate agent processing time
    setTimeout(() => {
        let reply = responseMatrix['default'];
        const lowerText = text.toLowerCase();
        
        if (lowerText.includes('cater') || lowerText.includes('event')) reply = responseMatrix['catering'];
        if (lowerText.includes('menu') || lowerText.includes('food')) reply = responseMatrix['menu'];
        if (lowerText.includes('contact') || lowerText.includes('book')) reply = responseMatrix['contact'];

        const botDiv = document.createElement('div');
        botDiv.className = 'bot-message';
        botDiv.textContent = reply;
        chatLog.appendChild(botDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    }, 600);
}

// Allow Enter key execution
chatInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        transmitMessage();
    }
});