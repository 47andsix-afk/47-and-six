function startIntervalTimer(duration, display) {
    let timer = duration, minutes, seconds;
    setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;
        display.textContent = minutes + ":" + seconds;
        if (--timer < 0) { timer = duration; }
    }, 1000);
}

function switchView(viewId, buttonEl) {
    document.querySelectorAll('.view-panel').forEach(panel => {
        panel.classList.remove('active-view');
        panel.style.display = 'none'; 
    });
    const targetView = document.getElementById(viewId);
    targetView.classList.add('active-view');
    targetView.style.display = 'block'; 
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('active');
    });
    buttonEl.classList.add('active');
}

function triggerManualDeployment(target) {
    const consoleBox = document.getElementById('storefront-console-output');
    const timestamp = new Date().toLocaleTimeString([], { hour12: false });
    const line = document.createElement('div');
    line.style.marginTop = '6px';
    line.style.borderTop = '1px dashed #333';
    line.style.paddingTop = '6px';
    line.textContent = `[${timestamp}] DEPLOYMENT TRIGGERED: ${target}\nExecuting parallel handshake validation layers... STATUS: OK.`;
    consoleBox.appendChild(line);
    consoleBox.scrollTop = consoleBox.scrollHeight;
}

function startLiveLogs() {
    const logsData = {
        'hub-log-storefront': ['System armed. Monitoring production lines...', 'Interval check: Active deployment window clear.', 'Syncing storefront metrics with core cadence...', 'Cycle state verified. Standing by for execution.'],
        'hub-log-ronin': ['Verification successful. Cluster operational...', 'Sweeping target data nodes...', 'Data packet optimization loop initialized.', 'Parallel acquisition threads running clean.'],
        'hub-log-sustasis': ['Memory space quantized. Index map stable...', 'Running HNSW vector node verification...', 'Semantic quantization threshold at 99.9%', 'Indexing latest conceptual schemas...'],
        'hub-log-tensile': ['Translating baseline instructions... 100% precision.', 'Listening for incoming translation hooks...', 'Parsing human intent strings into machine blocks.', 'Zero fluff filtering protocol active.']
    };

    Object.keys(logsData).forEach(id => {
        const logBox = document.getElementById(id);
        if (!logBox) return;
        setInterval(() => {
            const timestamp = new Date().toLocaleTimeString([], { hour12: false });
            const randomLog = logsData[id][Math.floor(Math.random() * logsData[id].length)];
            const line = document.createElement('div');
            line.style.marginBottom = '4px';
            line.textContent = `[${timestamp}] ${randomLog}`;
            logBox.appendChild(line);
            logBox.scrollTop = logBox.scrollHeight;
        }, Math.floor(Math.random() * 3000) + 3000);
    });
}

function runRoninTelemetry() {
    let t1 = 74; let t2 = 41;
    setInterval(() => {
        t1 += Math.floor(Math.random() * 5) + 1;
        t2 += Math.floor(Math.random() * 6) + 1;
        if (t1 > 100) t1 = 0;
        if (t2 > 100) t2 = 0;
        const el1 = document.getElementById('ronin-t1-status');
        const el2 = document.getElementById('ronin-t2-status');
        if (el1) el1.textContent = t1 === 0 ? "VERIFYING // 0%" : `SWEEPING // ${t1}%`;
        if (el2) el2.textContent = t2 === 0 ? "OPTIMIZING // 0%" : `SWEEPING // ${t2}%`;
    }, 1200);
}

window.onload = function () {
    let sixMinutes = 60 * 6,
        display = document.querySelector('#cadence-clock');
    startIntervalTimer(sixMinutes, display);
    startLiveLogs();
    runRoninTelemetry();
};