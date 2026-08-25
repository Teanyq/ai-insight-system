
(function() {
    try {
        const reportsContainer = document.getElementById('reportsContainer');
        const reportCount = document.getElementById('reportCount');
        const errorBox = document.getElementById('errorBox');
        
        const modal = document.getElementById('reportModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const closeBtn = document.querySelector('.close-btn');

        mermaid.initialize({ startOnLoad: false, theme: 'default' });
        fetchReports();
        
        if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.add('hidden'));

        window.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
        });

        async function fetchReports() {
            try {
                const res = await fetch('/api/v1/insights');
                if (!res.ok) throw new Error('Failed to fetch reports. Status: ' + res.status);
                
                const reports = await res.json();
                renderReports(reports);

                // URLのクエリパラメータ ?id=... をチェックして特定の記事を開く
                const urlParams = new URLSearchParams(window.location.search);
                const reportId = urlParams.get('id');
                if (reportId) {
                    const targetReport = reports.find(r => r.id == reportId);
                    if (targetReport) {
                        // 少し遅らせてから開く（UIの描画完了を待つ）
                        setTimeout(() => openReport(targetReport), 100);
                    }
                }
            } catch (err) {
                console.error(err);
                showError('Error loading reports: ' + err.message);
            }
        }

        function renderReports(reports) {
            if (!reportCount || !reportsContainer) return;
            reportCount.textContent = reports.length;
            reportsContainer.innerHTML = '';
            
            if (reports.length === 0) {
                reportsContainer.innerHTML = '<p style="color: #64748b; grid-column: 1/-1;">No reports available yet.</p>';
                return;
            }

            reports.forEach(report => {
                const card = document.createElement('div');
                card.className = 'report-card';
                const dateStr = new Date(report.created_at).toLocaleDateString('ja-JP');
                
                let hookText = '';
                if (report.markdown_content) {
                    // Extract the core concept if available
                    const coreMatch = report.markdown_content.match(/## 🎯.*?\n+([^\n]+)/i);
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
                card.addEventListener('click', () => openReport(report));
                reportsContainer.appendChild(card);
            });
        }

        const tabOverview = document.getElementById('tabOverview');
        const tabDetails = document.getElementById('tabDetails');
        const modalBodyOverview = document.getElementById('modalBodyOverview');
        const modalBodyDetails = document.getElementById('modalBodyDetails');
        
        if (tabOverview) {
            tabOverview.addEventListener('click', () => {
                tabOverview.classList.add('active');
                tabDetails.classList.remove('active');
                modalBodyOverview.classList.remove('hidden');
                modalBodyDetails.classList.add('hidden');
            });
        }
        if (tabDetails) {
            tabDetails.addEventListener('click', () => {
                tabDetails.classList.add('active');
                tabOverview.classList.remove('active');
                modalBodyDetails.classList.remove('hidden');
                modalBodyOverview.classList.add('hidden');
            });
        }

        function openReport(report) {
            const modalTitle = document.getElementById('modalTitle');
            const modal = document.getElementById('reportModal');
            
            modalTitle.textContent = report.title;
            
            // Render Markdown
            let overviewHTML = marked.parse(report.markdown_content || '');
            let detailsHTML = marked.parse(report.markdown_content_detailed || 'No details available.');
            
            // Fix mermaid classes for rendering (Robust DOM Parsing)
            function processMermaid(htmlContent) {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = htmlContent;
                const mermaidBlocks = tempDiv.querySelectorAll('code[class*="language-mermaid"], code.mermaid');
                mermaidBlocks.forEach(block => {
                    const parentPre = block.parentElement;
                    if (parentPre && parentPre.tagName === 'PRE') {
                        const newDiv = document.createElement('div');
                        newDiv.className = 'mermaid';
                        // textContent automatically unescapes HTML entities like &gt;
                        newDiv.textContent = block.textContent; 
                        parentPre.replaceWith(newDiv);
                    }
                });
                return tempDiv.innerHTML;
            }
            
            overviewHTML = processMermaid(overviewHTML);
            detailsHTML = processMermaid(detailsHTML);
            
            // Also handle cases where marked might not add the language class if Gemini omitted it (unlikely, but just in case)
            overviewHTML = overviewHTML.replace(/<pre><code>graph/g, '<div class="mermaid">graph').replace(/<pre><code>mindmap/g, '<div class="mermaid">mindmap').replace(/<pre><code>flowchart/g, '<div class="mermaid">flowchart');
            
            modalBodyOverview.innerHTML = overviewHTML;
            modalBodyDetails.innerHTML = detailsHTML;
            
            // Reset tabs
            tabOverview.click();
            
            modal.classList.remove('hidden');
            
            // Render mermaid diagrams
            setTimeout(() => {
                mermaid.init(undefined, document.querySelectorAll('.mermaid'));
            }, 100);
        }

        function showError(msg) {
            if(!errorBox) return;
            errorBox.textContent = msg;
            errorBox.classList.remove('hidden');
            setTimeout(() => {
                errorBox.classList.add('hidden');
            }, 5000);
        }
    } catch(e) {
        console.error('Public JS Error:', e);
    }
})();
