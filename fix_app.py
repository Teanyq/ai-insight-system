import os

js_code = """
document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const reportsContainer = document.getElementById('reportsContainer');
    const reportCount = document.getElementById('reportCount');
    const errorBox = document.getElementById('errorBox');
    
    const modal = document.getElementById('reportModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const closeBtn = document.querySelector('.close-btn');

    fetchReports();

    generateBtn.addEventListener('click', generateInsight);
    
    closeBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });

    async function fetchReports() {
        try {
            const res = await fetch('/api/v1/insights');
            if (!res.ok) throw new Error('Failed to fetch reports');
            
            const reports = await res.json();
            renderReports(reports);
        } catch (err) {
            showError(err.message);
        }
    }

    async function generateInsight() {
        setLoading(true);
        try {
            const res = await fetch('/api/v1/generate-insight', { method: 'POST' });
            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.detail || 'Generation failed');
            }
            await fetchReports();
        } catch (err) {
            showError(err.message);
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
            
            const previewText = report.markdown_content.replace(/[#*`]/g, '').substring(0, 150) + '...';

            card.innerHTML = `
                <h3>${report.title}</h3>
                <div class="date">${dateStr}</div>
                <div class="preview">${previewText}</div>
            `;

            card.addEventListener('click', () => openReport(report));
            reportsContainer.appendChild(card);
        });
    }

    function openReport(report) {
        modalTitle.textContent = report.title;
        modalBody.innerHTML = marked.parse(report.markdown_content);
        modal.classList.remove('hidden');
    }

    function setLoading(isLoading) {
        const btnText = generateBtn.querySelector('.btn-text');
        const loader = generateBtn.querySelector('.loader');
        
        generateBtn.disabled = isLoading;
        if (isLoading) {
            btnText.textContent = 'Generating... (This takes a minute)';
            loader.classList.remove('hidden');
        } else {
            btnText.textContent = 'Generate New Insight';
            loader.classList.add('hidden');
        }
    }

    function showError(msg) {
        errorBox.textContent = msg;
        errorBox.classList.remove('hidden');
        setTimeout(() => {
            errorBox.classList.add('hidden');
        }, 5000);
    }
});
"""

with open(r"C:\ai-insight\frontend\app.js", "w", encoding="utf-8") as f:
    f.write(js_code)
