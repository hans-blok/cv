#!/usr/bin/env python3
"""
Generate PDF from cv.html using Chrome/Edge headless browser
"""

from pathlib import Path
import subprocess
import sys
import os

# Paths
BASE_DIR = Path(__file__).parent
PAGES_DIR = BASE_DIR / "pages"
HTML_FILE = PAGES_DIR / "cv.html"
OUTPUT_PDF = PAGES_DIR / "cv.pdf"

def find_chrome():
    """Find Chrome or Edge browser executable"""
    # Try Chrome first
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    
    # Try Edge
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    
    for path in edge_paths:
        if os.path.exists(path):
            return path
    
    return None

def generate_pdf():
    """Generate PDF from HTML file using headless browser"""
    
    if not HTML_FILE.exists():
        print(f"Error: {HTML_FILE} not found. Run generate_site.py first.")
        return False
    
    # Ensure pages directory exists
    PAGES_DIR.mkdir(exist_ok=True)
    
    browser_path = find_chrome()
    if not browser_path:
        print("Error: Chrome or Edge browser not found.")
        print("\nPlease install Chrome or manually:")
        print(f"  1. Open {HTML_FILE} in your browser")
        print("  2. Press Ctrl+P (Print)")
        print("  3. Select 'Save as PDF' as destination")
        print("  4. Enable 'Background graphics' in More settings")
        print(f"  5. Save as {OUTPUT_PDF}")
        return False
    
    print(f"Using browser: {browser_path}")
    print(f"Reading HTML from: {HTML_FILE}")
    print(f"Generating PDF: {OUTPUT_PDF}")
    
    # Create a temporary HTML with expanded engagements for PDF
    temp_html = BASE_DIR / "cv_temp.html"
    html_content = HTML_FILE.read_text(encoding='utf-8')
    
    # Read the CSS file and inline it for PDF
    css_file = PAGES_DIR / "static" / "style.css"
    css_content = css_file.read_text(encoding='utf-8') if css_file.exists() else ""
    
    # Find and replace any CSS link tag with inline CSS
    import re
    css_link_pattern = r"<link rel='stylesheet' href='[^']*style\.css[^']*'>"
    html_content = re.sub(css_link_pattern, f"<style>{css_content}</style>", html_content)
    
    # Add print-specific CSS and JavaScript for expanding engagements
    html_content = html_content.replace('</head>', '''
    <style>
        @media print {
            /* Expand all engagements - show all details */
            .engagement-details {
                max-height: none !important;
                overflow: visible !important;
                padding-top: 12px !important;
            }
            
            /* Hide toggle arrow in print */
            .engagement-toggle {
                display: none !important;
            }
            
            /* Remove pointer cursor */
            .engagement-summary {
                cursor: default !important;
            }
            
            /* Avoid page breaks inside engagements */
            .engagement-item {
                page-break-inside: avoid;
            }
            
            /* Keep section title with content */
            .block-title {
                page-break-after: avoid !important;
            }
            
            /* Remove generated timestamp footer */
            .generated {
                display: none !important;
            }
            
            /* Hide sidebar in PDF */
            .urls-sidebar {
                display: none !important;
            }
            
            /* Full width for main content without sidebar */
            .main-content {
                margin-left: 0 !important;
            }
        }
    </style>
    <script>
        // Auto-expand all engagements when page loads (before print)
        window.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.engagement-summary').forEach(summary => {
                if (summary.getAttribute('aria-expanded') !== 'true') {
                    summary.click();
                }
            });
        });
    </script>
    </head>''')
    
    temp_html.write_text(html_content, encoding='utf-8')
    
    # Run headless browser to generate PDF - wait for page to load completely
    cmd = [
        browser_path,
        "--headless=new",
        "--disable-gpu",
        f"--print-to-pdf={OUTPUT_PDF}",
        "--print-to-pdf-no-header",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=10000",  # Wait 10 seconds for rendering
        f"file:///{temp_html.as_posix()}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Clean up temp file
        if temp_html.exists():
            temp_html.unlink()
        
        if OUTPUT_PDF.exists():
            print(f"✓ PDF generated successfully: {OUTPUT_PDF}")
            print("  All werkervaring sections are fully expanded")
            print("  Section headers stay with their content")
            return True
        else:
            print("Error: PDF was not created")
            if result.stderr:
                print(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Error: PDF generation timed out")
        if temp_html.exists():
            temp_html.unlink()
        return False
    except Exception as e:
        print(f"Error: {e}")
        if temp_html.exists():
            temp_html.unlink()
        return False

if __name__ == "__main__":
    try:
        success = generate_pdf()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(1)
