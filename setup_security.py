import os
import re

base_dir = r"C:\ai-insight"
endpoints_path = os.path.join(base_dir, "backend", "api", "endpoints.py")
main_path = os.path.join(base_dir, "backend", "main.py")

# 1. Update endpoints.py to add Basic Auth
with open(endpoints_path, "r", encoding="utf-8") as f:
    endpoints_code = f.read()

auth_code = """
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import status
import secrets

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
"""

# Insert auth_code after imports
endpoints_code = endpoints_code.replace("logger = logging.getLogger(__name__)", auth_code + "\nlogger = logging.getLogger(__name__)")

# Protect endpoints
endpoints_code = endpoints_code.replace(
    'def get_settings(db: Session = Depends(get_db)):',
    'def get_settings(db: Session = Depends(get_db), username: str = Depends(verify_admin)):'
)
endpoints_code = endpoints_code.replace(
    'def update_settings(settings: SystemConfigSchema, db: Session = Depends(get_db)):',
    'def update_settings(settings: SystemConfigSchema, db: Session = Depends(get_db), username: str = Depends(verify_admin)):'
)
endpoints_code = endpoints_code.replace(
    'async def generate_insight(db: Session = Depends(get_db)):',
    'async def generate_insight(db: Session = Depends(get_db), username: str = Depends(verify_admin)):'
)

with open(endpoints_path, "w", encoding="utf-8") as f:
    f.write(endpoints_code)

# 2. Update main.py to add /admin route
with open(main_path, "r", encoding="utf-8") as f:
    main_code = f.read()

admin_route = """
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import status, Depends, HTTPException
from fastapi.responses import FileResponse
import secrets

security = HTTPBasic()

def verify_admin_page(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/admin", include_in_schema=False)
def admin_page(username: str = Depends(verify_admin_page)):
    return FileResponse(os.path.join(frontend_path, "admin.html"))
"""

main_code = main_code.replace('if os.path.exists(frontend_path):', admin_route + '\nif os.path.exists(frontend_path):')

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_code)

# 3. Handle Frontend Files
frontend_dir = os.path.join(base_dir, "frontend")
index_path = os.path.join(frontend_dir, "index.html")
app_js_path = os.path.join(frontend_dir, "app.js")
admin_html_path = os.path.join(frontend_dir, "admin.html")
admin_js_path = os.path.join(frontend_dir, "admin.js")
public_js_path = os.path.join(frontend_dir, "public.js")

# Copy index.html to admin.html and rename script
with open(index_path, "r", encoding="utf-8") as f:
    index_html = f.read()

admin_html = index_html.replace('src="app.js"', 'src="admin.js"')
with open(admin_html_path, "w", encoding="utf-8") as f:
    f.write(admin_html)

# Clean index.html for public
public_html = re.sub(r'<div class="header-actions">.*?</div>', '', index_html, flags=re.DOTALL)
public_html = re.sub(r'<!-- Settings Modal -->.*?</div>\s*</div>', '', public_html, flags=re.DOTALL)
public_html = public_html.replace('src="app.js"', 'src="public.js"')
with open(index_path, "w", encoding="utf-8") as f:
    f.write(public_html)

# Move app.js to admin.js
import shutil
shutil.move(app_js_path, admin_js_path)

# Create public.js
public_js_code = """
(function() {
    try {
        const reportsContainer = document.getElementById('reportsContainer');
        const reportCount = document.getElementById('reportCount');
        const errorBox = document.getElementById('errorBox');
        
        const modal = document.getElementById('reportModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const closeBtn = document.querySelector('.close-btn');

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

        function openReport(report) {
            modalTitle.textContent = report.title;
            if (typeof marked !== 'undefined') {
                modalBody.innerHTML = marked.parse(report.markdown_content || '');
            } else {
                modalBody.innerHTML = '<pre>' + (report.markdown_content || '') + '</pre>';
            }
            modal.classList.remove('hidden');
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
"""
with open(public_js_path, "w", encoding="utf-8") as f:
    f.write(public_js_code)

print("Security separation completed successfully.")
