"""
Shiro Shopify API v8.1 - FIXED ASYNC QUEUE & BACKGROUND WORKERS
"""

import time
import asyncio
import random
import gc
import os
import uuid
import threading
from flask import Flask, request, jsonify
from shopifyapi import run_shopify_check

app = Flask(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
MAX_CONCURRENT_TASKS = 50  # عدد المهام التي تعالج في نفس الوقت
RESULTS_EXPIRY = 600       # مدة الاحتفاظ بالنتيجة (10 دقائق)
CLEANUP_INTERVAL = 300     # تنظيف الذاكرة كل 5 دقائق

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL STATE
# ══════════════════════════════════════════════════════════════════════════════
_results = {}  # {task_id: {"status": "...", "result": ...}}
_queue = asyncio.Queue()
_active_tasks = 0
_worker_loop = None  # سيتم تخزين الـ loop هنا للوصول إليه من Flask

# ══════════════════════════════════════════════════════════════════════════════
# PROXY PARSER
# ══════════════════════════════════════════════════════════════════════════════

def fix_proxy(proxy_str):
    if not proxy_str:
        return None
    from urllib.parse import quote
    proxy_str = proxy_str.strip()
    if '@' in proxy_str and '://' in proxy_str:
        return proxy_str
    parts = proxy_str.split(':')
    if len(parts) == 4:
        ip, port, user, password = parts
        user_enc = quote(user, safe='')
        pass_enc = quote(password, safe='')
        return f"http://{user_enc}:{pass_enc}@{ip}:{port}"
    if len(parts) == 2:
        ip, port = parts
        return f"http://{ip}:{port}"
    return None

# ══════════════════════════════════════════════════════════════════════════════
# BACKGROUND WORKERS
# ══════════════════════════════════════════════════════════════════════════════

async def shopify_worker():
    global _active_tasks
    while True:
        task_id, site, card_str, proxy = await _queue.get()
        _active_tasks += 1
        try:
            proxy_fixed = fix_proxy(proxy) if proxy else None
            # معالجة الطلب باستخدام shopifyapi المحسن
            res = await run_shopify_check(site, card_str, proxy_fixed, timeout=90.0)
            
            # تحويل الرد للشكل المتوقع من البوت
            status = res.get("status", "Error")
            if status == "Charged":
                response_msg = "PAYMENT_SUCCESS"
            elif status == "Approved":
                response_msg = "OTP_REQUIRED"
            elif status == "Declined":
                response_msg = "CARD_DECLINED"
            else:
                response_msg = res.get("message", "ERROR")[:50]
            
            _results[task_id] = {
                "completed": True,
                "timestamp": time.time(),
                "data": {
                    "status": status,
                    "Response": response_msg,
                    "Price": res.get("price", "-"),
                    "Gateway": "Shopify Payments",
                    "error_code": res.get("error_code", "")
                }
            }
        except Exception as e:
            _results[task_id] = {
                "completed": True,
                "timestamp": time.time(),
                "data": {"status": "Error", "Response": str(e)[:50]}
            }
        finally:
            _active_tasks -= 1
            _queue.task_done()

async def cleanup_task():
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        now = time.time()
        to_delete = [tid for tid, data in _results.items() if now - data.get("timestamp", 0) > RESULTS_EXPIRY]
        for tid in to_delete:
            if tid in _results:
                del _results[tid]
        gc.collect()

# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/submit', methods=['GET'])
def submit():
    site = request.args.get('site', '').strip()
    cc = request.args.get('cc', '').strip()
    proxy = request.args.get('proxy', '').strip()
    
    if not site or not cc or cc.count('|') != 3:
        return jsonify({"status": "Error", "Response": "Bad params"}), 400
    
    task_id = str(uuid.uuid4())
    _results[task_id] = {"completed": False, "timestamp": time.time()}
    
    # وضع المهمة في الطابور باستخدام الـ loop المخصص للعمال
    if _worker_loop and _worker_loop.is_running():
        _worker_loop.call_soon_threadsafe(_queue.put_nowait, (task_id, site, cc, proxy))
    else:
        return jsonify({"status": "Error", "Response": "Server Error: Worker loop not ready"}), 500
        
    return jsonify({"status": "Success", "task_id": task_id})

@app.route('/status/<task_id>', methods=['GET'])
def status(task_id):
    task = _results.get(task_id)
    if not task:
        return jsonify({"status": "Error", "Response": "Task not found"}), 404
    
    if task["completed"]:
        return jsonify(task["data"])
    else:
        return jsonify({"status": "Pending", "Response": "Processing..."})

@app.route('/shopify', methods=['GET'])
def shopify_legacy():
    """Endpoint قديم للتوافق، يحاول الانتظار قليلاً ثم يعطي Task ID إذا تأخر"""
    site = request.args.get('site', '').strip()
    cc = request.args.get('cc', '').strip()
    proxy = request.args.get('proxy', '').strip()
    
    task_id = str(uuid.uuid4())
    _results[task_id] = {"completed": False, "timestamp": time.time()}
    
    if _worker_loop and _worker_loop.is_running():
        _worker_loop.call_soon_threadsafe(_queue.put_nowait, (task_id, site, cc, proxy))
    else:
        return jsonify({"status": "Error", "Response": "Worker loop not ready"}), 500
    
    # الانتظار لمدة 10 ثوانٍ كحد أقصى للرد المباشر
    for _ in range(20):
        time.sleep(0.5)
        if _results.get(task_id) and _results[task_id]["completed"]:
            return jsonify(_results[task_id]["data"])
            
    return jsonify({"status": "Pending", "task_id": task_id, "Response": "Task submitted, please poll /status/<task_id>"})

# ══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_server():
    global _worker_loop
    
    # تشغيل العمال في loop منفصل
    def start_loop(loop):
        asyncio.set_event_loop(loop)
        for _ in range(MAX_CONCURRENT_TASKS):
            loop.create_task(shopify_worker())
        loop.create_task(cleanup_task())
        loop.run_forever()

    _worker_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_loop, args=(_worker_loop,), daemon=True)
    t.start()
    
    # تشغيل Flask
    app.run(host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    run_server()
