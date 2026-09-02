let currentSpec = null;
let selectedRightTab = 'yaml';

document.addEventListener("DOMContentLoaded", () => {
    loadPresets();
    connectSSE();
});

async function loadPresets() {
    try {
        const res = await fetch("/api/presets");
        const presets = await res.json();
        currentSpec = presets["gaming"] || presets["minimal"];
        syncUIToSpec();
        updatePreviewDesktop();
        compileAST();
    } catch (e) {
        console.error("Error loading presets:", e);
    }
}

function loadPresetTemplate() {
    const presetKey = document.getElementById("presetSelect").value;
    fetch("/api/presets")
        .then(res => res.json())
        .then(presets => {
            if (presets[presetKey]) {
                currentSpec = presets[presetKey];
                syncUIToSpec();
                updatePreviewDesktop();
                compileAST();
            }
        });
}

function switchConceptTab(tabName) {
    const tabs = ["appearance", "shell", "explorer", "services", "security", "apps", "oobe"];
    tabs.forEach((t, idx) => {
        const sec = document.getElementById(`concept-${t}`);
        if (sec) {
            sec.style.display = (t === tabName) ? "grid" : "none";
        }
    });

    const btnNavs = document.querySelectorAll(".concept-tabs .tab-item");
    btnNavs.forEach(btn => {
        if (btn.innerText.toLowerCase().includes(tabName.substring(0, 4))) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });
}

function syncUIToSpec() {
    if (!currentSpec) return;

    document.getElementById("appTheme").value = currentSpec.appearance?.theme || "dark";
    document.getElementById("accentColor").value = currentSpec.appearance?.accent_color || "#8B5CF6";
    document.getElementById("showExt").checked = currentSpec.explorer?.show_file_extensions ?? true;
    document.getElementById("showHidden").checked = currentSpec.explorer?.show_hidden_files ?? true;
    document.getElementById("classicCtx").checked = currentSpec.explorer?.classic_context_menu ?? true;
    document.getElementById("tbAlign").value = currentSpec.taskbar?.alignment || "left";
    document.getElementById("tbSearch").value = currentSpec.taskbar?.search_mode || "hidden";
    document.getElementById("disableCopilot").checked = !(currentSpec.taskbar?.copilot ?? false);
    document.getElementById("svcSysMain").value = currentSpec.services?.sysmain || "disabled";
    document.getElementById("svcDiagTrack").value = currentSpec.services?.diagtrack || "disabled";
    document.getElementById("bypassWin11").checked = currentSpec.security?.bypass_win11_checks ?? true;
    document.getElementById("disableTelemetry").checked = currentSpec.security?.disable_telemetry ?? true;
    document.getElementById("oobeUser").value = currentSpec.oobe?.username || "Admin";
    document.getElementById("skipOOBE").checked = currentSpec.oobe?.skip_oobe ?? true;

    // Sync AppX checkboxes
    const removeList = currentSpec.apps?.remove_packages || [];
    document.querySelectorAll(".appx-chk").forEach(chk => {
        chk.checked = removeList.includes(chk.value);
    });
}

function updateSpecFromUI() {
    if (!currentSpec) return;

    currentSpec.appearance = currentSpec.appearance || {};
    currentSpec.appearance.theme = document.getElementById("appTheme").value;
    currentSpec.appearance.accent_color = document.getElementById("accentColor").value;

    currentSpec.explorer = currentSpec.explorer || {};
    currentSpec.explorer.show_file_extensions = document.getElementById("showExt").checked;
    currentSpec.explorer.show_hidden_files = document.getElementById("showHidden").checked;
    currentSpec.explorer.classic_context_menu = document.getElementById("classicCtx").checked;

    currentSpec.taskbar = currentSpec.taskbar || {};
    currentSpec.taskbar.alignment = document.getElementById("tbAlign").value;
    currentSpec.taskbar.search_mode = document.getElementById("tbSearch").value;
    currentSpec.taskbar.copilot = !document.getElementById("disableCopilot").checked;

    currentSpec.services = currentSpec.services || {};
    currentSpec.services.sysmain = document.getElementById("svcSysMain").value;
    currentSpec.services.diagtrack = document.getElementById("svcDiagTrack").value;

    currentSpec.security = currentSpec.security || {};
    currentSpec.security.bypass_win11_checks = document.getElementById("bypassWin11").checked;
    currentSpec.security.disable_telemetry = document.getElementById("disableTelemetry").checked;

    currentSpec.oobe = currentSpec.oobe || {};
    currentSpec.oobe.username = document.getElementById("oobeUser").value || "Admin";
    currentSpec.oobe.skip_oobe = document.getElementById("skipOOBE").checked;

    // Gather selected AppX removals
    const selectedAppx = [];
    document.querySelectorAll(".appx-chk:checked").forEach(chk => {
        selectedAppx.push(chk.value);
    });
    currentSpec.apps = currentSpec.apps || {};
    currentSpec.apps.remove_packages = selectedAppx;

    updatePreviewDesktop();
    compileAST();
}

function updatePreviewDesktop() {
    const isDark = document.getElementById("appTheme").value === "dark";
    const align = document.getElementById("tbAlign").value;
    const searchMode = document.getElementById("tbSearch").value;
    const classicCtx = document.getElementById("classicCtx").checked;
    const showExt = document.getElementById("showExt").checked;
    const disableCopilot = document.getElementById("disableCopilot").checked;

    // Wallpaper & Theme
    const wallpaper = document.getElementById("previewWallpaper");
    wallpaper.className = `desktop-wallpaper ${isDark ? 'wallpaper-dark' : 'wallpaper-light'}`;

    const miniWin = document.getElementById("previewWindow");
    miniWin.className = `mini-window ${isDark ? '' : 'mini-window-light'}`;

    const taskbar = document.getElementById("previewTaskbar");
    taskbar.className = `mini-taskbar ${isDark ? '' : 'mini-taskbar-light'}`;

    // Taskbar alignment
    const tbIcons = document.getElementById("previewTaskbarIcons");
    tbIcons.className = `mini-taskbar-icons align-${align}`;

    // Search bar
    const previewSearch = document.getElementById("previewSearch");
    if (searchMode === "hidden") {
        previewSearch.style.display = "none";
    } else if (searchMode === "icon") {
        previewSearch.style.display = "flex";
        previewSearch.innerText = "🔍";
        previewSearch.style.width = "28px";
    } else {
        previewSearch.style.display = "flex";
        previewSearch.innerText = "Search...";
        previewSearch.style.width = "100px";
    }

    // Copilot
    document.getElementById("previewCopilot").style.display = disableCopilot ? "none" : "flex";

    // File Explorer mockup
    document.getElementById("previewFile1").innerText = showExt ? "Document.txt" : "Document";
    document.getElementById("previewFile2").innerText = showExt ? "Installer.exe" : "Installer";
    document.getElementById("previewContextItem").innerText = classicCtx ? "Context Menu: Win10 Classic" : "Context Menu: Win11 Double";
}

async function compileAST() {
    if (!currentSpec) return;

    try {
        const res = await fetch("/api/compile-ast", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ spec: currentSpec })
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById("viewYaml").innerText = data.yaml;
            document.getElementById("viewAst").innerText = JSON.stringify(data.plan, null, 2);
        }
    } catch (e) {
        console.error("Error compiling AST:", e);
    }
}

function switchRightTab(tab) {
    selectedRightTab = tab;
    document.getElementById("tabYaml").classList.toggle("active", tab === "yaml");
    document.getElementById("tabAst").classList.toggle("active", tab === "ast");
    document.getElementById("viewYaml").style.display = (tab === "yaml") ? "block" : "none";
    document.getElementById("viewAst").style.display = (tab === "ast") ? "block" : "none";
}

async function inspectISO() {
    const isoPath = document.getElementById("isoPath").value.trim();
    if (!isoPath) {
        alert("Please enter a valid Windows ISO file path.");
        return;
    }

    appendLog(`Extracting and analyzing ISO: ${isoPath}...`);
    try {
        const res = await fetch("/api/inspect-iso", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ iso_path: isoPath })
        });
        const data = await res.json();
        if (data.error) {
            appendLog(`[ERROR] ${data.error}`);
            alert(`Inspection error: ${data.error}`);
            return;
        }

        const statsDiv = document.getElementById("isoStats");
        statsDiv.style.display = "block";
        const sum = data.analysis.components_summary;
        statsDiv.innerText = `Target Edition: ${data.analysis.target_edition} (${data.analysis.architecture}) | Build: ${data.analysis.build_version}\n` +
            `Components: ${sum.packages_count} packages, ${sum.optional_features_count} optional features, ${sum.provisioned_apps_count} apps, ${sum.services_count} services`;

        appendLog(`[SUCCESS] Analysis complete for ${data.analysis.target_edition}.`);
    } catch (e) {
        appendLog(`[ERROR] ${e.message}`);
    }
}

async function startBuild() {
    const isoPath = document.getElementById("isoPath").value.trim();
    if (!isoPath) {
        alert("Please enter a valid Windows ISO file path first.");
        return;
    }

    document.getElementById("btnBuild").disabled = true;
    appendLog("\nLaunching WinAlter Distribution Compiler...");

    try {
        const res = await fetch("/api/start-build", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                spec: currentSpec,
                iso_path: isoPath,
                edition_index: 1
            })
        });
        const data = await res.json();
        if (data.error) {
            appendLog(`[ERROR] ${data.error}`);
            document.getElementById("btnBuild").disabled = false;
        }
    } catch (e) {
        appendLog(`[ERROR] Build launch failed: ${e.message}`);
        document.getElementById("btnBuild").disabled = false;
    }
}

function connectSSE() {
    const evtSource = new EventSource("/api/events");
    evtSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.message) {
                appendLog(data.message);
                if (data.message.startsWith("BUILD_SUCCESS:") || data.message.startsWith("BUILD_ERROR:")) {
                    document.getElementById("btnBuild").disabled = false;
                }
            }
        } catch (e) {
            console.error("SSE parse error:", e);
        }
    };
}

function appendLog(msg) {
    const consoleTerminal = document.getElementById("consoleLog");
    const ts = new Date().toLocaleTimeString();
    consoleTerminal.innerText += `\n[${ts}] ${msg}`;
    consoleTerminal.scrollTop = consoleTerminal.scrollHeight;
}
