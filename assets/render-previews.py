import asyncio
from playwright.async_api import async_playwright
import os
import http.server
import socketserver
import threading
import time
import logging

def start_http_server():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), Handler) as httpd:
        httpd.serve_forever()

async def render_previews():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            timeout=60000
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        # Set default timeout for all operations
        page.set_default_timeout(60000)
        
        # Setup logging for all console messages, not just errors
        page.on("console", lambda msg: logging.info(f"Browser console {msg.type}: {msg.text}"))
        
        logging.info("Starting HTTP server...")
        server_thread = threading.Thread(target=start_http_server, daemon=True)
        server_thread.start()
        time.sleep(3)
        
        os.makedirs('assets/previews', exist_ok=True)
        
        try:
            logging.info("Navigating to preview page...")
            # Use domcontentloaded instead of networkidle, with explicit timeout
            await page.goto(
                'http://localhost:8000/assets/preview.html',
                wait_until='domcontentloaded',
                timeout=60000
            )
            
            logging.info("Waiting for page to stabilize...")
            await page.wait_for_load_state('load', timeout=60000)
            await page.wait_for_timeout(5000)  # Increased wait time
            
            preview_configs = [
                {'name': 'grid', 'selector': '[data-preview="grid"]', 'number': '1'},
                {'name': 'floating', 'selector': '[data-preview="floating"]', 'number': '2'},
                {'name': 'feature', 'selector': '[data-preview="feature"]', 'number': '3'}
            ]
            
            for config in preview_configs:
                try:
                    await page.wait_for_selector(config['selector'], state='visible')
                    element = await page.query_selector(config['selector'])
                    if element:
                        await element.screenshot(path=f'assets/previews/{config["number"]}-preview.png')
                    else:
                        logging.error(f'Could not find element with selector: {config["selector"]}')
                except Exception as e:
                    logging.error(f'Error capturing {config["name"]}: {str(e)}')
            
        except Exception as e:
            logging.error(f'Error during preview generation: {str(e)}')
            # Add error screenshot for debugging
            await page.screenshot(path='assets/previews/error.png')
        finally:
            await browser.close()

def main():
    # Set more detailed logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Check if preview.html exists relative to repo root
    if not os.path.exists('assets/preview.html'):
        raise FileNotFoundError("assets/preview.html not found")
    
    # No need to change directory since we're already in repo root
    asyncio.run(render_previews())

if __name__ == "__main__":
    main()