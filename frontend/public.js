
(function() {
    try {
        const reportsContainer = document.getElementById('reportsContainer');
        const reportCount = document.getElementById('reportCount');
        const errorBox = document.getElementById('errorBox');
        
        const modal = document.getElementById('reportModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const closeBtn = document.querySelector('.close-btn');
        let currentReportId = null;

        mermaid.initialize({ startOnLoad: false, theme: 'dark', themeVariables: { background: 'transparent' } });
        fetchReports();
        
        if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.add('hidden'));

        window.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
        });

        const privacyLink = document.getElementById('privacyLink');
        const contactLink = document.getElementById('contactLink');
        const infoModal = document.getElementById('infoModal');
        const infoModalTitle = document.getElementById('infoModalTitle');
        const infoModalBody = document.getElementById('infoModalBody');
        const infoCloseBtn = document.querySelector('.info-close-btn');

        if (infoCloseBtn) infoCloseBtn.addEventListener('click', () => infoModal.classList.add('hidden'));

        window.addEventListener('click', (e) => {
            if (e.target === infoModal) infoModal.classList.add('hidden');
        });

        if (privacyLink) {
            privacyLink.addEventListener('click', (e) => {
                e.preventDefault();
                infoModalTitle.textContent = "Privacy Policy";
                infoModalBody.innerHTML = `
                    <h3>広告の配信について</h3>
                    <p>当サイトは Google AdSense を利用して広告を配信しています。</p>
                    <p>Googleなどの第三者配信事業者は、Cookieを使用して、ユーザーが当サイトや他のウェブサイトに過去にアクセスした際の情報に基づいて広告を配信します。</p>
                    <p>ユーザーは、<a href="https://myadcenter.google.com/" target="_blank" style="color: #3b82f6;">広告設定</a>でパーソナライズ広告を無効にすることができます。</p>
                `;
                infoModal.classList.remove('hidden');
            });
        }

        if (contactLink) {
            contactLink.addEventListener('click', (e) => {
                e.preventDefault();
                infoModalTitle.textContent = "Contact / About";
                infoModalBody.innerHTML = `
                    <h3>運営者情報</h3>
                    <p>AI Insight Engineは、最新のAI論文とビジネスニュースを掛け合わせてインサイトを自動生成するプロジェクトです。</p>
                    <p>お問い合わせやフィードバックは、以下のX（Twitter）アカウント（またはDM）までお気軽にどうぞ。</p>
                    <p><a href="https://x.com/AIInsightBridge" target="_blank" style="color: #3b82f6; font-weight: bold;">@AIInsightBridge (X) に問い合わせる</a></p>
                `;
                infoModal.classList.remove('hidden');
            });
        }

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

        const deleteReportBtn = document.getElementById('deleteReportBtn');
        if (deleteReportBtn) {
            deleteReportBtn.addEventListener('click', async () => {
                if (!currentReportId) return;
                
                if (!confirm('このレポートを削除しますか？\n(管理者のログインが必要です)')) return;
                
                try {
                    const res = await fetch(`/api/v1/insights/${currentReportId}`, {
                        method: 'DELETE'
                    });
                    
                    if (res.status === 401) {
                        alert('管理者のログインが必要です。管理画面（/docs または /api/v1/settings 等）でBasic認証を行ってから再度お試しください。');
                        return;
                    }
                    
                    if (!res.ok) throw new Error('Delete failed: ' + res.status);
                    
                    alert('削除しました。');
                    modal.classList.add('hidden');
                    fetchReports(); // reload
                } catch (err) {
                    console.error(err);
                    alert('削除に失敗しました: ' + err.message);
                }
            });
        }

        function openReport(report) {
            const modalTitle = document.getElementById('modalTitle');
            const modal = document.getElementById('reportModal');
            
            currentReportId = report.id;
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
