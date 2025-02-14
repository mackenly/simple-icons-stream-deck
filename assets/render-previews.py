import asyncio
from playwright.async_api import async_playwright
import os
import http.server
import socketserver
import threading
import time

def start_http_server():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), Handler) as httpd:
        httpd.serve_forever()

async def render_previews():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        # Start local HTTP server in a separate thread
        server_thread = threading.Thread(target=start_http_server, daemon=True)
        server_thread.start()
        time.sleep(3)  # Give the server a moment to start
        
        # Create previews directory if it doesn't exist
        os.makedirs('assets/previews', exist_ok=True)
        
        # Navigate to the page via HTTP server (note we're serving from repo root)
        await page.goto('http://localhost:8000/assets/preview.html')
        
        # Take screenshots of each preview
        preview_configs = [
            {'name': 'grid', 'selector': '[data-preview="grid"]'},
            {'name': 'floating', 'selector': '[data-preview="feature"]:nth-of-type(1)'},
            {'name': 'feature', 'selector': '[data-preview="feature"]:nth-of-type(2)'}
        ]
        
        for config in preview_configs:
            await page.wait_for_selector(config['selector'])
            element = await page.query_selector(config['selector'])
            await element.screenshot(path=f'assets/previews/preview_{config["name"]}.png')
        
        await browser.close()

def main():
    # Check if preview.html exists relative to repo root
    if not os.path.exists('assets/preview.html'):
        raise FileNotFoundError("assets/preview.html not found")
    
    # No need to change directory since we're already in repo root
    asyncio.run(render_previews())

if __name__ == "__main__":
    main()