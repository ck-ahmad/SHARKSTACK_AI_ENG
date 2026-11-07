from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", response_class=HTMLResponse)
def root_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EnterpriseIQ - Enterprise RAG Platform</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-slate-900 text-slate-100 font-sans min-h-screen flex flex-col">
        <!-- Header -->
        <header class="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
            <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-bold text-xl shadow-lg shadow-blue-500/20">
                        IQ
                    </div>
                    <div>
                        <h1 class="font-bold text-lg leading-tight text-white">EnterpriseIQ</h1>
                        <p class="text-xs text-slate-400">Enterprise RAG & Hybrid Retrieval Platform</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="/docs" target="_blank" class="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition flex items-center space-x-2">
                        <i class="fa-solid fa-code-branch"></i>
                        <span>Swagger API Docs</span>
                    </a>
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 mr-2 animate-pulse"></span>
                        System Operational
                    </span>
                </div>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="flex-1 max-w-7xl w-full mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            <!-- Left Sidebar Controls: Ingestion & Telemetry -->
            <div class="lg:col-span-4 space-y-6">
                
                <!-- Document Ingestion Card -->
                <div class="bg-slate-950/50 border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center space-x-2">
                        <i class="fa-solid fa-file-arrow-up text-blue-400"></i>
                        <span>1. Ingest Knowledge Document</span>
                    </h2>
                    <form id="uploadForm" class="space-y-4">
                        <div class="border-2 border-dashed border-slate-800 rounded-xl p-6 text-center hover:border-blue-500/50 transition cursor-pointer bg-slate-900/50" onclick="document.getElementById('fileInput').click()">
                            <i class="fa-solid fa-cloud-arrow-up text-3xl text-slate-500 mb-2"></i>
                            <p class="text-xs text-slate-400" id="fileLabel">Click to select TXT, PDF, DOCX, or MD file</p>
                            <input type="file" id="fileInput" class="hidden" required onchange="document.getElementById('fileLabel').innerText = this.files[0].name">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="text-[10px] text-slate-400 uppercase font-semibold">Chunk Size</label>
                                <input type="number" id="chunkSize" value="500" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-blue-500">
                            </div>
                            <div>
                                <label class="text-[10px] text-slate-400 uppercase font-semibold">Overlap</label>
                                <input type="number" id="chunkOverlap" value="50" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-blue-500">
                            </div>
                        </div>
                        <button type="submit" class="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/20 transition">
                            Process & Index Document
                        </button>
                    </form>
                    <div id="uploadStatus" class="mt-4 text-xs"></div>
                </div>

                <!-- Enterprise Security & Tenant Controls -->
                <div class="bg-slate-950/50 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                    <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
                        <i class="fa-solid fa-shield-halved text-emerald-400"></i>
                        <span>Security & RBAC Headers</span>
                    </h2>
                    <div>
                        <label class="text-[10px] text-slate-400 uppercase font-semibold">Tenant Context ID</label>
                        <input type="text" id="tenantId" value="tenant_enterprise" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-emerald-500">
                    </div>
                    <div>
                        <label class="text-[10px] text-slate-400 uppercase font-semibold">User Role</label>
                        <select id="userRole" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-emerald-500">
                            <option value="admin">Admin</option>
                            <option value="analyst">Analyst</option>
                            <option value="viewer">Viewer</option>
                        </select>
                    </div>
                    <button onclick="fetchAnalytics()" class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition">
                        Refresh Telemetry & Audit Logs
                    </button>
                </div>

                <!-- Admin Analytics Panel -->
                <div class="bg-slate-950/50 border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center space-x-2">
                        <i class="fa-solid fa-chart-line text-indigo-400"></i>
                        <span>Operational Telemetry</span>
                    </h2>
                    <div id="analyticsDisplay" class="text-xs text-slate-400 space-y-2">
                        <p class="italic text-slate-500">No telemetry recorded yet.</p>
                    </div>
                </div>

            </div>

            <!-- Right Workspace: Hybrid Search & Chat UI -->
            <div class="lg:col-span-8 flex flex-col space-y-6">
                
                <!-- Chat Window Container -->
                <div class="bg-slate-950/50 border border-slate-800 rounded-2xl p-6 shadow-xl flex-1 flex flex-col min-h-[500px]">
                    <div class="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-4">
                        <div class="flex items-center space-x-2">
                            <i class="fa-solid fa-comments text-blue-400"></i>
                            <h2 class="text-sm font-semibold text-slate-200">RAG Interactive Assistant</h2>
                        </div>
                        <span id="activeDocBadge" class="text-[11px] px-2.5 py-1 rounded-md bg-slate-800 text-slate-400">
                            No Active Document Target
                        </span>
                    </div>

                    <!-- Messages Output area -->
                    <div id="chatMessages" class="flex-1 overflow-y-auto space-y-4 pr-2 max-h-[420px]">
                        <div class="flex space-x-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800/50">
                            <div class="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold text-xs">AI</div>
                            <div class="text-xs leading-relaxed text-slate-300">
                                Welcome to <strong>EnterpriseIQ</strong>. Upload a document on the left panel, then ask any question here. Responses will feature automatic context retrieval and inline source citations (<span class="text-blue-400">[Source X]</span>).
                            </div>
                        </div>
                    </div>

                    <!-- Prompt Input Form -->
                    <form id="chatForm" class="mt-4 pt-4 border-t border-slate-800 flex space-x-3">
                        <input type="text" id="userQuery" placeholder="Ask a question grounded in your document..." class="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-xs focus:outline-none focus:border-blue-500" required>
                        <button type="submit" class="px-5 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl text-xs transition flex items-center space-x-2 shadow-lg shadow-blue-600/20">
                            <span>Send</span>
                            <i class="fa-solid fa-paper-plane"></i>
                        </button>
                    </form>
                </div>

            </div>
        </main>

        <script>
            let currentDocId = null;

            // Ingest Document
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const fileInput = document.getElementById('fileInput');
                const chunkSize = document.getElementById('chunkSize').value;
                const chunkOverlap = document.getElementById('chunkOverlap').value;
                const statusDiv = document.getElementById('uploadStatus');

                if (!fileInput.files.length) return;

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                statusDiv.innerHTML = '<span class="text-blue-400 animate-pulse">Uploading and parsing document...</span>';

                try {
                    const res = await fetch(`/api/v1/documents/ingest?chunk_size=${chunkSize}&chunk_overlap=${chunkOverlap}`, {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (res.ok) {
                        currentDocId = data.document_id;
                        statusDiv.innerHTML = `<span class="text-emerald-400">✓ Parsed: ${data.chunks_count} chunks created.</span>`;
                        document.getElementById('activeDocBadge').innerHTML = `Target: ${data.filename}`;
                        document.getElementById('activeDocBadge').className = 'text-[11px] px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono';
                    } else {
                        statusDiv.innerHTML = `<span class="text-rose-400">Error: ${data.detail}</span>`;
                    }
                } catch (err) {
                    statusDiv.innerHTML = `<span class="text-rose-400">Failed to connect to backend server.</span>`;
                }
            });

            // Chat Completions
            document.getElementById('chatForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const input = document.getElementById('userQuery');
                const message = input.value.trim();
                if (!message) return;

                const chatBox = document.getElementById('chatMessages');

                // User Bubble
                chatBox.innerHTML += `
                    <div class="flex space-x-3 justify-end">
                        <div class="bg-blue-600 text-white p-3.5 rounded-xl text-xs max-w-lg leading-relaxed shadow-md">
                            ${message}
                        </div>
                    </div>
                `;
                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;

                const tenantId = document.getElementById('tenantId').value;
                const userRole = document.getElementById('userRole').value;

                try {
                    const res = await fetch('/api/v1/chat/completions', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Tenant-Id': tenantId,
                            'X-Role': userRole
                        },
                        body: JSON.stringify({
                            message: message,
                            document_id: currentDocId,
                            top_k: 3
                        })
                    });
                    const data = await res.json();
                    
                    let citationHTML = '';
                    if (data.citations && data.citations.length) {
                        citationHTML = `<div class="mt-3 pt-2 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1">` +
                            data.citations.map(c => `<div><span class="text-blue-400 font-semibold">${c.source_tag}</span> ${c.content_preview}</div>`).join('') +
                            `</div>`;
                    }

                    chatBox.innerHTML += `
                        <div class="flex space-x-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800/50">
                            <div class="w-8 h-8 rounded-lg bg-emerald-600/20 text-emerald-400 flex items-center justify-center font-bold text-xs">AI</div>
                            <div class="text-xs leading-relaxed text-slate-300 flex-1">
                                ${data.response}
                                ${citationHTML}
                            </div>
                        </div>
                    `;
                    chatBox.scrollTop = chatBox.scrollHeight;
                    fetchAnalytics();
                } catch (err) {
                    chatBox.innerHTML += `<div class="text-xs text-rose-400 p-2">Failed to retrieve generation response.</div>`;
                }
            });

            // Fetch Analytics
            async function fetchAnalytics() {
                const tenantId = document.getElementById('tenantId').value;
                const userRole = document.getElementById('userRole').value;
                const display = document.getElementById('analyticsDisplay');

                try {
                    const res = await fetch('/api/v1/admin/analytics', {
                        headers: {
                            'X-Tenant-Id': tenantId,
                            'X-Role': userRole
                        }
                    });
                    const data = await res.json();
                    if (res.ok) {
                        const metrics = data.data;
                        display.innerHTML = `
                            <div class="grid grid-cols-2 gap-2 text-center">
                                <div class="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                                    <div class="text-slate-400 text-[10px]">Requests</div>
                                    <div class="text-sm font-bold text-white">${metrics.total_requests}</div>
                                </div>
                                <div class="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                                    <div class="text-slate-400 text-[10px]">Tokens</div>
                                    <div class="text-sm font-bold text-blue-400">${metrics.total_tokens_consumed}</div>
                                </div>
                            </div>
                        `;
                    } else {
                        display.innerHTML = `<span class="text-rose-400">${data.detail || 'Access Denied'}</span>`;
                    }
                } catch(e) {}
            }
        </script>
    </body>
    </html>
    """
    return html_content
