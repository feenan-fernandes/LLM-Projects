import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fonts & Lucide CDN in Head
head_addons = '''
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
'''
# Replace existing font link
text = re.sub(r'<link href="https://fonts.googleapis.com/css2\?family=Inter.*?rel="stylesheet">', head_addons, text)

# 2. CSS Overhaul (Typography, Icons, Semantic Layout, Micro-interactions)
new_css = '''
        :root {
            --bg-base: #09090b; /* Zinc 950 */
            --bg-panel: #18181b; /* Zinc 900 */
            --bg-surface: #27272a; /* Zinc 800 */
            --border: #27272a;
            --border-light: #3f3f46;
            --text-main: #fafafa;
            --text-muted: #a1a1aa;
            --accent-blue: #3b82f6; 
            --accent-yellow: #f59e0b; 
            --accent-green: #10b981; 
            --accent-red: #ef4444; 
            
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-glow: 0 0 15px rgba(59, 130, 246, 0.15);
        }
        
        * { box-sizing: border-box; }
        body { 
            margin: 0; padding: 0; display: flex; height: 100vh; 
            font-family: 'Inter', -apple-system, sans-serif; 
            -webkit-font-smoothing: antialiased;
            background-color: var(--bg-base); color: var(--text-main); overflow: hidden; 
        }
        
        h1, h2, h3, h4, h5, h6 { 
            font-family: 'Playfair Display', serif; 
            font-weight: 600; 
            letter-spacing: -0.02em; 
            margin: 0; 
        }
        
        .lucide { width: 18px; height: 18px; stroke-width: 2; flex-shrink: 0; }
        .lucide-sm { width: 14px; height: 14px; stroke-width: 2.5; }
        .lucide-lg { width: 22px; height: 22px; }
        
        /* Semantic Layout */
        aside#sidebar { 
            width: 320px; display: flex; flex-direction: column; 
            background-color: var(--bg-base); border-right: 1px solid var(--border); 
            z-index: 10; padding: 25px 20px;
        }
        main#canvas { 
            flex: 1; position: relative; background-color: var(--bg-base); 
            background-image: radial-gradient(var(--border) 1px, transparent 0);
            background-size: 24px 24px; display: flex; flex-direction: column; 
        }
        
        /* Header & Controls */
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .header h1 { font-size: 1.3rem; color: #fff; display: flex; align-items: center; gap: 10px; }
        
        .mode-toggle { 
            display: flex; background: var(--bg-panel); border-radius: 12px; 
            padding: 5px; border: 1px solid var(--border); margin-bottom: 25px; 
            box-shadow: inset var(--shadow-sm);
        }
        .mode-btn { 
            padding: 8px; text-align: center; font-size: 0.85rem; font-weight: 500; 
            cursor: pointer; border-radius: 8px; flex: 1; transition: all 0.2s ease; 
            color: var(--text-muted); display: flex; justify-content: center; align-items: center; gap: 6px;
        }
        .mode-btn:hover:not(.active-search):not(.active-build) { color: var(--text-main); }
        .mode-btn.active-search, .mode-btn.active-build { 
            background: var(--bg-surface); color: var(--text-main); 
            box-shadow: var(--shadow-sm); 
        }
        
        .uncensored-wrap { 
            display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.8rem; font-weight: 500;
            color: var(--accent-red); margin-bottom: 20px; padding: 10px; background: rgba(239, 68, 68, 0.05); 
            border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.15); transition: all 0.2s ease;
        }
        .uncensored-wrap:hover { background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.3); }
        
        .topic-select { 
            width: 100%; background: var(--bg-panel); color: var(--text-main); 
            border: 1px solid var(--border); padding: 12px; border-radius: 8px; 
            font-size: 0.85rem; outline: none; margin-bottom: 20px; cursor: pointer;
            transition: all 0.2s ease; appearance: none;
        }
        .topic-select:hover { border-color: var(--border-light); }
        
        /* Telemetry Panel */
        #metrics-panel { 
            margin-top: auto; padding: 20px; background: var(--bg-panel); 
            border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow-sm);
        }
        
        /* Footer */
        .minimal-footer {
            margin-top: 20px; text-align: center; font-size: 0.7rem; color: var(--text-muted);
            border-top: 1px solid var(--border); padding-top: 15px;
        }
        
        /* Terminal Canvas */
        #builder-panel { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; flex-direction: column; padding: 30px; padding-bottom: 120px; box-sizing: border-box; }
        .builder-header { 
            padding: 12px 20px; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px 12px 0 0;
            display: flex; align-items: center; color: var(--text-muted); font-family: monospace; font-size: 0.85rem;
            box-shadow: var(--shadow-md); z-index: 2;
        }
        .traffic-light { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
        .tl-red { background: var(--accent-red); }
        .tl-yellow { background: var(--accent-yellow); }
        .tl-green { background: var(--accent-green); margin-right: 15px; }
        
        #builder-log { 
            flex: 1; padding: 25px; font-family: "SFMono-Regular", Consolas, monospace; font-size: 0.85rem; line-height: 1.6; 
            color: var(--text-main); overflow-y: auto; background: rgba(9, 9, 11, 0.75); backdrop-filter: blur(12px);
            border: 1px solid var(--border); border-top: none; border-radius: 0 0 12px 12px; box-shadow: var(--shadow-lg);
        }
        
        /* Live Flowchart HUD */
        .hud-flow { 
            display: flex; align-items: center; justify-content: center; gap: 10px; padding: 12px; 
            background: rgba(24, 24, 27, 0.8); backdrop-filter: blur(16px); border-bottom: 1px solid var(--border); 
            font-size: 0.75rem; font-weight: 500; border-left: 1px solid var(--border); border-right: 1px solid var(--border);
        }
        .flow-node { padding: 6px 12px; border-radius: 20px; border: 1px solid var(--border); background: var(--bg-base); color: var(--text-muted); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); display: flex; align-items: center; gap: 6px; }
        .flow-node.active { background: rgba(59, 130, 246, 0.1); border-color: var(--accent-blue); color: var(--accent-blue); box-shadow: var(--shadow-glow); transform: translateY(-1px); }
        .flow-node.error { background: rgba(239, 68, 68, 0.1); border-color: var(--accent-red); color: var(--accent-red); }
        .flow-node.success { background: rgba(16, 185, 129, 0.1); border-color: var(--accent-green); color: var(--accent-green); }
        .flow-arrow { color: var(--border-light); font-size: 1rem; transition: color 0.3s; display: flex; align-items: center; justify-content: center; }
        .flow-arrow.active { color: var(--accent-blue); }
        
        /* Input Box - Elegant Pill */
        .input-area { 
            position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); 
            width: 90%; max-width: 800px; z-index: 1000;
        }
        #search-form { 
            display: flex; align-items: center; background: rgba(24, 24, 27, 0.85); backdrop-filter: blur(16px); 
            border: 1px solid var(--border-light); border-radius: 24px; padding: 8px 12px; box-shadow: var(--shadow-lg); 
            transition: all 0.2s ease;
        }
        #search-form:focus-within { border-color: var(--accent-blue); box-shadow: var(--shadow-glow), var(--shadow-lg); }
        #query { 
            flex: 1; padding: 12px 15px; border: none; background: transparent; color: var(--text-main); 
            font-size: 0.95rem; font-family: 'Inter', sans-serif; outline: none; 
        }
        #query::placeholder { color: var(--text-muted); }
        .file-attach-btn { 
            background: transparent; color: var(--text-muted); border: none; padding: 8px; 
            cursor: pointer; border-radius: 50%; display: flex; align-items: center; justify-content: center; 
            transition: all 0.2s ease; 
        }
        .file-attach-btn:hover { background: var(--bg-surface); color: var(--text-main); transform: scale(1.05); }
        button[type="submit"] { 
            padding: 10px 20px; border-radius: 18px; border: none; background: var(--text-main); color: #000; 
            font-weight: 500; cursor: pointer; font-size: 0.9rem; transition: all 0.2s ease; display: flex; 
            justify-content: center; align-items: center; gap: 8px; margin-left: 5px; box-shadow: var(--shadow-md);
        }
        button[type="submit"]:hover { filter: brightness(0.9); transform: translateY(-1px); box-shadow: var(--shadow-lg); }
        button[type="submit"]:active { transform: translateY(0); }
        
        #tab-3d { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        #3d-graph { width: 100%; height: 100%; }
        
        .loader { border: 2px solid var(--border-light); border-top: 2px solid var(--text-main); border-radius: 50%; width: 16px; height: 16px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        /* Governance Dashboard */
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 2000; justify-content: center; align-items: center; backdrop-filter: blur(8px); }
        .modal-content { background: var(--bg-panel); border: 1px solid var(--border-light); border-radius: 16px; width: 650px; max-width: 90%; padding: 35px; box-shadow: var(--shadow-lg); }
        .modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 20px; margin-bottom: 25px; }
        .modal-header h2 { font-size: 1.5rem; color: var(--text-main); display: flex; align-items: center; gap: 10px; }
        .stat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-box { background: var(--bg-surface); border: 1px solid var(--border); padding: 20px; border-radius: 12px; text-align: center; transition: transform 0.2s ease; }
        .stat-box:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
        .stat-box h4 { margin: 0; font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; font-weight: 600; font-family: 'Inter', sans-serif; }
        .stat-box p { margin: 12px 0 0 0; font-size: 1.8rem; font-weight: 700; color: var(--text-main); }
        .violation-log { max-height: 180px; overflow-y: auto; background: var(--bg-base); padding: 15px; border-radius: 8px; font-family: "SFMono-Regular", Consolas, monospace; font-size: 0.8rem; border: 1px solid rgba(239, 68, 68, 0.3); }
        
        .pulsing { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
'''
text = re.sub(r':root\s*\{.*?\@keyframes pulse \{ 0%, 100% \{ opacity: 1; \} 50% \{ opacity: \.5; \} \}', new_css, text, flags=re.DOTALL)

# 3. HTML Semantic Replacements & Emoji -> Lucide
# Sidebar to <aside> and replace emoji
text = text.replace('<div id="sidebar">', '<aside id="sidebar">')
# The closing tag of sidebar needs to become </aside>, it occurs right before <div id="canvas">
text = re.sub(r'</div>\s*<div id="canvas">', '</aside>\n    <main id="canvas">', text)
# Close canvas with </main>
text = re.sub(r'</div>\s*<script>', '</main>\n\n    <script>', text)

# Replace all ugly emojis with crisp semantic icons
text = text.replace('<h1>&#x26A1; Swarm IDE</h1>', '<h1><i data-lucide="zap" class="lucide-lg" style="color:var(--accent-blue);"></i> Swarm IDE</h1>')
text = text.replace('&#x1F6E1;&#xFE0F; Governance', '<i data-lucide="shield" class="lucide-sm"></i> Governance')
text = text.replace('RAG Search', '<i data-lucide="search" class="lucide-sm"></i> Search')
text = text.replace('Builder &#x1F6E0;&#xFE0F;', '<i data-lucide="hammer" class="lucide-sm"></i> Builder')

text = text.replace('&#x26A1; Telemetry', '<i data-lucide="activity" class="lucide-sm"></i> Telemetry')

# Input bar attachment icon
text = text.replace('&#x1F4CE;', '<i data-lucide="paperclip"></i>')

# Governance Modal Header
text = text.replace('<h2>&#x1F6E1;&#xFE0F; AI Governance & Auditing</h2>', '<h2><i data-lucide="shield-alert" class="lucide-lg" style="color:var(--accent-blue);"></i> AI Governance & Auditing</h2>')

# Flowchart HUD icons
text = text.replace('dY"? Prompt', '<i data-lucide="message-square" class="lucide-sm"></i> Prompt')
text = text.replace('dY"? Router', '<i data-lucide="git-branch" class="lucide-sm"></i> Router')
text = text.replace('dY  Orchestrator', '<i data-lucide="brain-circuit" class="lucide-sm"></i> Orchestrator')
text = text.replace('dY\' Sandbox', '<i data-lucide="box" class="lucide-sm"></i> Sandbox')
text = text.replace('o. Validation', '<i data-lucide="check-circle" class="lucide-sm"></i> Validation')
text = text.replace('+\'', '<i data-lucide="arrow-right" class="lucide-sm"></i>')

# Also fix the builder header traffic lights (currently they are string literals that failed regex earlier, or they were replaced? No, they were in the HTML!)
# Let's replace the traffic lights with sleek CSS circles
old_lights = \'\'\'<span style="color: var(--accent-yellow); margin-right: 10px;">&#x25CF;</span>
                <span style="color: var(--accent-green); margin-right: 10px;">&#x25CF;</span>
                <span style="color: var(--accent-red); margin-right: 15px;">&#x25CF;</span>\'\'\'
new_lights = \'\'\'<span class="traffic-light tl-red"></span>
                <span class="traffic-light tl-yellow"></span>
                <span class="traffic-light tl-green"></span>\'\'\'
text = text.replace(old_lights, new_lights)

# Add minimal footer to sidebar
footer_html = \'\'\'
        <footer class="minimal-footer">
            <div style="display:flex; justify-content:center; align-items:center; gap:5px; margin-bottom:5px;">
                <i data-lucide="cpu" class="lucide-sm"></i> Swarm IDE v2.0
            </div>
            &copy; 2026. All rights reserved.
        </footer>
    </aside>\'\'\'
text = text.replace('</aside>', footer_html)

# Add lucide.createIcons() to script
text = text.replace('// INIT MARKED', 'lucide.createIcons();\n        // INIT MARKED')

# Write to file
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
