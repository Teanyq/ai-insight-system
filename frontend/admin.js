
(function() {
    try {
        const generateBtn = document.getElementById('generateBtn');
        const settingsBtn = document.getElementById('settingsBtn');
        const reportsContainer = document.getElementById('reportsContainer');
        const reportCount = document.getElementById('reportCount');
        const errorBox = document.getElementById('errorBox');
        
        const modal = document.getElementById('reportModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const closeBtn = document.querySelector('.close-btn');

        const settingsModal = document.getElementById('settingsModal');
        const closeSettingsBtn = document.getElementById('closeSettingsBtn');
        const saveSettingsBtn = document.getElementById('saveSettingsBtn');

        const arxivQueryInput = document.getElementById('arxivQueryInput');
        const rssUrlInput = document.getElementById('rssUrlInput');
        const intervalInput = document.getElementById('intervalInput');

        mermaid.initialize({ startOnLoad: false, theme: 'default' });
        fetchReports();

        if (generateBtn) generateBtn.addEventListener('click', generateInsight);
        if (settingsBtn) settingsBtn.addEventListener('click', openSettings);
        if (saveSettingsBtn) saveSettingsBtn.addEventListener('click', saveSettings);
        
        if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
        if (closeSettingsBtn) closeSettingsBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));

        window.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
            if (e.target === settingsModal) settingsModal.classList.add('hidden');
        });

        async function openSettings() {
            try {
                const res = await fetch('/api/v1/settings');
                if (res.ok) {
                    const data = await res.json();
                    arxivQueryInput.value = data.arxiv_query;
                    rssUrlInput.value = data.rss_url;
                    intervalInput.value = data.schedule_interval_hours;
                }
            } catch (err) {
                console.error('Failed to load settings', err);
            }
            settingsModal.classList.remove('hidden');
        }

        async function saveSettings() {
            const btnText = saveSettingsBtn.textContent;
            saveSettingsBtn.textContent = 'Saving...';
            saveSettingsBtn.disabled = true;

            try {
                const res = await fetch('/api/v1/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        arxiv_query: arxivQueryInput.value,
                        rssUrl: rssUrlInput.value, // BUG: Needs to be rss_url
                        rss_url: rssUrlInput.value,
                        schedule_interval_hours: parseInt(intervalInput.value)
                    })
                });
                if (!res.ok) throw new Error('Failed to save settings');
                settingsModal.classList.add('hidden');
            } catch (err) {
                showError(err.message);
            } finally {
                saveSettingsBtn.textContent = btnText;
                saveSettingsBtn.disabled = false;
            }
        }

        async function fetchReports() {
            try {
                const res = await fetch('/api/v1/insights');
                if (!res.ok) throw new Error('Failed to fetch reports. Status: ' + res.status);
                
                const reports = await res.json();
                renderReports(reports);
            } catch (err) {
                console.error(err);
                showError('Error loading reports: ' + err.message);
            }
        }

        async function generateInsight() {
            setLoading(true);
            try {
                const res = await fetch('/api/v1/generate-insight', { method: 'POST' });
                if (!res.ok) {
                    const errorData = await res.json().catch(() => ({}));
                    throw new Error(errorData.detail || 'Generation failed with status ' + res.status);
                }
                await mermaid.initialize({ startOnLoad: false, theme: 'default' });
        fetchReports();
            } catch (err) {
                console.error(err);
                showError('Error generating: ' + err.message);
            } finally {
                setLoading(false);
            }
        }

        function renderReports(reports) {
            reportCount.textContent = reports.length;
            reportsContainer.innerHTML = '';
            
            if (reports.length === 0) {
                reportsContainer.innerHTML = '<p style="color: #64748b; grid-column: 1/-1;">No reports generated yet.</p>';
                return;
            }

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

        function setLoading(isLoading) {
            if (!generateBtn) return;
            const btnText = generateBtn.querySelector('.btn-text');
            const loader = generateBtn.querySelector('.loader');
            
            generateBtn.disabled = isLoading;
            if (isLoading) {
                btnText.textContent = 'Generating...';
                if(loader) loader.classList.remove('hidden');
            } else {
                btnText.textContent = 'Generate New Insight';
                if(loader) loader.classList.add('hidden');
            }
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
        const eb = document.getElementById('errorBox');
        if(eb) {
            eb.textContent = 'Critical JS Error: ' + e.message;
            eb.classList.remove('hidden');
        }
    }
})();
