import os
import re

base_dir = r"C:\ai-insight"
public_js = os.path.join(base_dir, "frontend", "public.js")

with open(public_js, "r", encoding="utf-8") as f:
    js_content = f.read()

# Replace the innerHTML generation in renderReports
old_card_gen = """
            reports.forEach(report => {
                const card = document.createElement('div');
                card.className = 'report-card';
                const dateStr = new Date(report.created_at).toLocaleString('ja-JP');
                let previewText = report.markdown_content ? report.markdown_content.replace(/[#*`]/g, '').substring(0, 150) + '...' : '';

                card.innerHTML = `
                    <h3>${report.title}</h3>
                    <div class="date">${dateStr}</div>
                    <div class="preview">${previewText}</div>
                `;
                card.addEventListener('click', () => openReport(report));
                reportsContainer.appendChild(card);
            });
"""

new_card_gen = """
            reports.forEach(report => {
                const card = document.createElement('div');
                card.className = 'report-card';
                const dateStr = new Date(report.created_at).toLocaleDateString('ja-JP');
                
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
                card.addEventListener('click', () => openReport(report));
                reportsContainer.appendChild(card);
            });
"""

js_content = js_content.replace(old_card_gen.strip(), new_card_gen.strip())
with open(public_js, "w", encoding="utf-8") as f:
    f.write(js_content)


style_css = os.path.join(base_dir, "frontend", "style.css")
with open(style_css, "r", encoding="utf-8") as f:
    css_content = f.read()

new_css = """
/* Phase 6: Youth-targeted Card UI */
.report-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.report-card:hover {
    transform: translateY(-6px) scale(1.02);
    background: rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 40px -10px rgba(0, 242, 254, 0.15), 0 0 20px rgba(0, 242, 254, 0.05);
    border-color: rgba(0, 242, 254, 0.3);
}

.report-card h3 {
    font-size: 1.15rem;
    line-height: 1.4;
    margin-top: 0.5rem;
}

.card-badge {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
    color: #fff;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.25rem 0.6rem;
    border-radius: 20px;
    letter-spacing: 0.05em;
    box-shadow: 0 4px 10px rgba(79, 172, 254, 0.3);
}

.hook-box {
    background: rgba(0, 0, 0, 0.25);
    border-left: 3px solid #00f2fe;
    padding: 0.75rem;
    border-radius: 4px 8px 8px 4px;
    font-size: 0.9rem;
    font-weight: 500;
    line-height: 1.5;
    color: #e2e8f0;
    margin-top: 0.5rem;
}

.read-more-btn {
    margin-top: auto;
    background: transparent;
    color: #00f2fe;
    border: none;
    text-align: right;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0.75rem 0 0 0;
    transition: color 0.2s;
    outline: none;
}

.report-card:hover .read-more-btn {
    color: #fff;
}
"""

with open(style_css, "a", encoding="utf-8") as f:
    f.write(new_css)

print("Updated public UI for young audience.")
