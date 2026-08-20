import os

base_dir = r"C:\ai-insight"

# 1. Update gemini_client.py
gemini_py = os.path.join(base_dir, "backend", "core", "gemini_client.py")
with open(gemini_py, "r", encoding="utf-8") as f:
    gemini_content = f.read()

# Remove the Hook from prompt
old_hook_prompt = """## 🎬 TikTok / Shorts Hook (最初の3秒のツカミ)
[Provide a 1-2 sentence script idea for a short video hook. Make it super intriguing, e.g., "AIがまたヤバいことになってるんだけど...知ってる？"]
## 🎯 要するに何がスゴイの？ (Core Concept)"""

new_hook_prompt = """## 🎯 要するに何がスゴイの？ (Core Concept)"""

gemini_content = gemini_content.replace(old_hook_prompt, new_hook_prompt)
with open(gemini_py, "w", encoding="utf-8") as f:
    f.write(gemini_content)

# 2. Update public.js to use standard preview text instead of Hook
public_js = os.path.join(base_dir, "frontend", "public.js")
with open(public_js, "r", encoding="utf-8") as f:
    js_content = f.read()

old_js_logic = """
                let hookText = '';
                if (report.markdown_content) {
                    const hookMatch = report.markdown_content.match(/##.*?Hook.*?\\n+([^\\n]+)/i);
                    if (hookMatch && hookMatch[1]) {
                        hookText = hookMatch[1].replace(/[#*`]/g, '').trim();
                    } else {
                        hookText = report.markdown_content.replace(/[#*`]/g, '').substring(0, 80) + '...';
                    }
                }

                card.innerHTML = `
                    <div class="card-badge">✨ INSIGHT</div>
                    <div class="date">${dateStr}</div>
                    <h3>${report.title}</h3>
                    <div class="hook-box">
                        <span class="hook-icon">🎬</span> 
                        <span class="hook-text">"${hookText}"</span>
                    </div>
                    <button class="read-more-btn">続きを読む ➔</button>
                `;
"""

new_js_logic = """
                let hookText = '';
                if (report.markdown_content) {
                    // Extract the core concept if available
                    const coreMatch = report.markdown_content.match(/## 🎯.*?\\n+([^\\n]+)/i);
                    if (coreMatch && coreMatch[1]) {
                        hookText = coreMatch[1].replace(/[#*`]/g, '').trim();
                        // Truncate if too long
                        if (hookText.length > 70) hookText = hookText.substring(0, 70) + '...';
                    } else {
                        hookText = report.markdown_content.replace(/[#*`]/g, '').substring(0, 80) + '...';
                    }
                }

                card.innerHTML = `
                    <div class="card-badge">✨ INSIGHT</div>
                    <div class="date">${dateStr}</div>
                    <h3>${report.title}</h3>
                    <div class="hook-box" style="border-left-color: #f59e0b;">
                        <span class="hook-icon">💡</span> 
                        <span class="hook-text">${hookText}</span>
                    </div>
                    <button class="read-more-btn">続きを読む ➔</button>
                `;
"""

js_content = js_content.replace(old_js_logic.strip(), new_js_logic.strip())
with open(public_js, "w", encoding="utf-8") as f:
    f.write(js_content)

print("Removed TikTok Hook from prompt and UI.")
