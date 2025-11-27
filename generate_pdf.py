#!/usr/bin/env python3
"""
Generate PDF from cv.html using Chrome/Edge headless browser
"""

from pathlib import Path
import subprocess
import sys
import os
import re

# Paths
BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
HTML_FILE = DOCS_DIR / "cv.html"
OUTPUT_PDF = DOCS_DIR / "cv.pdf"

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
    
    # Ensure docs directory exists
    DOCS_DIR.mkdir(exist_ok=True)
    
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
    
    # Remove title to prevent it showing in PDF header
    html_content = re.sub(r'<title>.*?</title>', '<title></title>', html_content, flags=re.IGNORECASE)
    
    # Remove the entire sidebar - simple string find/replace approach
    sidebar_start = html_content.find('<aside class="urls-sidebar">')
    if sidebar_start != -1:
        sidebar_end = html_content.find('</aside>', sidebar_start)
        if sidebar_end != -1:
            html_content = html_content[:sidebar_start] + html_content[sidebar_end + 8:]
            print("✓ Sidebar removed from PDF")
    else:
        print("⚠ Warning: Could not find sidebar")
    
    # Read the CSS file and inline it for PDF
    css_file = DOCS_DIR / "static" / "style.css"
    css_content = css_file.read_text(encoding='utf-8') if css_file.exists() else ""
    
    # Find and replace any CSS link tag with inline CSS
    css_link_pattern = r"<link rel='stylesheet' href='[^']*style\.css[^']*'>"
    html_content = re.sub(css_link_pattern, f"<style>{css_content}</style>", html_content)
    
    # Add print-specific CSS and JavaScript for expanding engagements
    html_content = html_content.replace('</head>', '''
    <style>
        /* Always apply these styles for PDF generation */
        @page {
            margin: 0.5in;
            size: A4;
        }
        
        /* Expand all engagements - show all details */
        .engagement-details {
            max-height: none !important;
            overflow: visible !important;
            padding-top: 12px !important;
        }
        
        /* Hide toggle arrow */
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
        
        /* Full width for main content since sidebar is removed */
        .container {
            display: block !important;
            margin: 0 !important;
            padding: 12px !important;
            max-width: none !important;
            flex-direction: column !important;
            gap: 0 !important;
        }
        
        .main-content {
            margin: 0 !important;
            margin-left: 0 !important;
            width: 100% !important;
            flex: none !important;
        }
        
        /* Force remove any sidebar remnants */
        .urls-sidebar, aside {
            display: none !important;
        }
        
        .pdf-download-btn {
            display: none !important;
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
    
    # Debug: Save a copy to see what we're generating
    debug_file = BASE_DIR / "cv_debug.html"
    debug_file.write_text(html_content, encoding='utf-8')
    print(f"✓ Debug HTML saved to: {debug_file}")
    
    temp_html.write_text(html_content, encoding='utf-8')
    
    # Run headless browser to generate PDF - wait for page to load completely
    cmd = [
        browser_path,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--print-to-pdf={OUTPUT_PDF}",
        "--print-to-pdf-no-header",
        "--no-pdf-header-footer",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=15000",  # Wait 15 seconds for rendering
        f"file:///{temp_html.resolve().as_posix()}"
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
            print("  Sidebar and download button removed")
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
