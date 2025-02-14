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
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Increase viewport size to ensure all content is visible
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        # Setup console error logging
        page.on("console", lambda msg: logging.error(msg.text) if msg.type == "error" else None)
        
        # Start local HTTP server in a separate thread
        server_thread = threading.Thread(target=start_http_server, daemon=True)
        server_thread.start()
        time.sleep(3)  # Give the server a moment to start
        
        # Create previews directory if it doesn't exist
        os.makedirs('assets/previews', exist_ok=True)
        
        try:
            await page.goto('http://localhost:8000/assets/preview.html', wait_until='networkidle')
            
            # Wait for JavaScript to execute
            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_timeout(2000)  # Wait for JS animations
            
            # Wait for all images to load
            await page.evaluate("""
                async () => {
                    const images = document.querySelectorAll('img');
                    await Promise.all(Array.from(images).map(img => {
                        if (img.complete) return;
                        return new Promise((resolve, reject) => {
                            img.addEventListener('load', resolve);
                            img.addEventListener('error', reject);
                        });
                    }));
                }
            """)
            
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
        finally:
            await browser.close()

def main():
    logging.basicConfig(level=logging.INFO)
    # Check if preview.html exists relative to repo root
    if not os.path.exists('assets/preview.html'):
        raise FileNotFoundError("assets/preview.html not found")
    
    # No need to change directory since we're already in repo root
    asyncio.run(render_previews())

if __name__ == "__main__":
    main()