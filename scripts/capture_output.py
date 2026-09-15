"""Capture actual local model results and the resulting review UI. Requires Playwright."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--url',default='http://127.0.0.1:8091');args=a.parse_args()
with sync_playwright() as p:
 browser=p.chromium.launch();page=browser.new_page(viewport={'width':1600,'height':1180},device_scale_factor=1.5)
 with page.expect_response(lambda r:'/api/scenarios/video_tampered_01/analyze' in r.url,timeout=180000) as response:
  page.goto(args.url)
 result=response.value.json();assert response.value.ok,result
 (root/'docs/output-example.json').write_text(json.dumps(result,indent=2))
 page.wait_for_function("document.querySelector('#decision').textContent!=='Analysing media'")
 page.locator('#mediaPlayer').evaluate('(v)=>{v.pause();v.currentTime=2.4;}')
 page.wait_for_function("document.querySelector('#mediaPlayer').readyState>=2")
 page.wait_for_timeout(500)
 page.screenshot(path=str(root/'docs/output-showcase.png'),full_page=True)
 with page.expect_download() as download:page.get_by_role('button',name='Download evidence report').click()
 assert download.value.suggested_filename=='approvalguard-evidence.json'
 browser.close();print(json.dumps(result['review'],indent=2));print(result['processing_ms'])
