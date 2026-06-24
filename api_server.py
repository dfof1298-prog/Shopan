#!/usr/bin/env python3
"""
Shiro Shopify API v7.0 - AUTO-RESTART & MEMORY CLEANER
"""

import time
import threading
import queue
import random
import asyncio
import gc
import os
import sys
from flask import Flask, request, jsonify
from datetime import datetime
from shopifyapi import run_shopify_check

app = Flask(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
NUM_WORKERS = 10
TIMEOUT = 55
MAX_QUEUE = 1000
AUTO_RESTART_INTERVAL = 3600

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL STATE
# ══════════════════════════════════════════════════════════════════════════════

_queue = queue.Queue()
_results = {}
_events = {}
_rlock = threading.Lock()
_running = False
_busy = [False] * NUM_WORKERS
_last_cleanup = time.time()
_restart_timer = None

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
# MEMORY CLEANER
# ══════════════════════════════════════════════════════════════════════════════

def memory_cleaner():
    global _last_cleanup, _results, _events
    while _running:
        time.sleep(300)
        now = time.time()
        if now - _last_cleanup > 300:
            with _rlock:
                old_results = []
                for rid, res in _results.items():
                    try:
                        rid_time = float(rid.split('_')[0])
                        if now - rid_time > 600:
                            old_results.append(rid)
                    except:
                        pass
                for rid in old_results:
                    _results.pop(rid, None)
                
                old_events = []
                for rid, ev in _events.items():
                    try:
                        rid_time = float(rid.split('_')[0])
                        if now - rid_time > 600:
                            old_events.append(rid)
                    except:
                        pass
                for rid in old_events:
                    _events.pop(rid, None)
            
            gc.collect()
            _last_cleanup = now
            print(f"[MEMORY] 🧹 Cleaned {len(old_results)} old results, {len(old_events)} old events | Memory: {gc.get_count()}")

def auto_restart():
    global _restart_timer
    time.sleep(AUTO_RESTART_INTERVAL)
    print("[RESTART] 🔄 Auto-restarting API...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# ══════════════════════════════════════════════════════════════════════════════
# ASYNC CHECK - ✅ تم التعديل
# ══════════════════════════════════════════════════════════════════════════════

def run_async_check(site, card_str, proxy, min_price=0.01, max_price=999999.0):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            run_shopify_check(
                site, 
                card_str, 
                proxy, 
                verbose=False, 
                timeout=50.0,
                min_price=min_price,
                max_price=max_price
            )
        )
        loop.close()
        
        status = result.get("status", "Error")
        if status == "Charged":
            response_msg = "PAYMENT_SUCCESS"
        elif status == "Approved":
            response_msg = "OTP_REQUIRED"
        elif status == "Declined":
            response_msg = "CARD_DECLINED"
        else:
            response_msg = result.get("message", "ERROR")[:50]
        
        return {
            "status": status,
            "Response": response_msg,
            "Price": result.get("price", "-"),
            "Gateway": "Shopify Payments",
            "error_code": result.get("error_code", "")
        }
    except asyncio.TimeoutError:
        return {"status": "Error", "Response": "Timeout", "Price": "-", "Gateway": "Shopify Payments"}
    except Exception as e:
        return {"status": "Error", "Response": str(e)[:50], "Price": "-", "Gateway": "Shopify Payments"}

def _worker(wid):
    global _running
    print(f"[W{wid}] ✅ Worker ready")
    
    while _running:
        try:
            req = _queue.get(timeout=1.0)
        except queue.Empty:
            continue
        
        rid, site, cc, mon, yr, cvv, proxy, min_price, max_price = req
        _busy[wid] = True
        
        try:
            card_str = f"{cc}|{mon}|{yr}|{cvv}"
            proxy_fixed = fix_proxy(proxy) if proxy else None
            
            print(f"[W{wid}] 🔍 {site[:30]}...")
            start = time.time()
            res = run_async_check(site, card_str, proxy_fixed, min_price, max_price)
            elapsed = time.time() - start
            print(f"[W{wid}] ✅ {res['status']} | {elapsed:.1f}s")
        except Exception as e:
            res = {"status": "Error", "Response": str(e)[:50]}
        finally:
            _busy[wid] = False
        
        with _rlock:
            _results[rid] = res
            if rid in _events:
                _events[rid].set()
        
        _queue.task_done()

def _start():
    global _running
    if _running:
        return
    _running = True
    
    threading.Thread(target=memory_cleaner, daemon=True).start()
    
    for i in range(NUM_WORKERS):
        threading.Thread(target=_worker, args=(i,), daemon=True).start()
    print(f"[API] ✅ {NUM_WORKERS} workers started")
    print(f"[API] 🧹 Memory cleaner: Every 5 minutes")
    print(f"[API] 🔄 Auto-restart: Every {AUTO_RESTART_INTERVAL//3600} hour(s)")

def _check(site, card, proxy, min_price=0.01, max_price=999999.0):
    _start()
    
    p = card.strip().replace(" ", "").split("|")
    if len(p) != 4:
        return {"status": "Error", "Response": "Bad format"}
    cc, mon, yr, cvv = p
    if len(yr) == 2:
        yr = "20" + yr
    
    rid = f"{time.time()}_{random.randint(1000,9999)}"
    ev = threading.Event()
    
    with _rlock:
        _events[rid] = ev
    
    _queue.put((rid, site, cc, mon, yr, cvv, proxy, min_price, max_price))
    
    if ev.wait(timeout=TIMEOUT):
        with _rlock:
            _events.pop(rid, None)
            return _results.pop(rid, {"status": "Error", "Response": "No result"})
    
    with _rlock:
        _events.pop(rid, None)
        _results.pop(rid, None)
    return {"status": "Error", "Response": "Timeout"}

# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS - ✅ تم التعديل
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/shopify', methods=['GET'])
def shopify():
    site = request.args.get('site', '').strip()
    cc = request.args.get('cc', '').strip()
    proxy = request.args.get('proxy', '').strip()
    
    # ✅ أضيفت معاملات الأسعار
    min_price = float(request.args.get('min_price', 0.01))
    max_price = float(request.args.get('max_price', 999999.0))
    
    if not site or not cc or cc.count('|') != 3:
        return jsonify({"status": "Error", "Response": "Bad params"})
    
    t0 = time.time()
    res = _check(site, cc, proxy if proxy else None, min_price, max_price)
    elapsed = time.time() - t0
    
    out = {
        "status": res.get("status", "Error"),
        "Response": res.get("Response", "Unknown"),
        "Price": res.get("Price", "-"),
        "Gateway": "Shopify Payments",
        "time": f"{elapsed:.1f}s"
    }
    
    card_num = cc.split("|")[0] if "|" in cc else cc
    mask = card_num[:6] + "******" + card_num[-4:] if len(card_num) > 10 else "****"
    busy = sum(_busy)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {out['status']:<8} | {mask} | {elapsed:.1f}s | q:{_queue.qsize()} w:{busy}")
    
    return jsonify(out)

@app.route('/health')
def health():
    return jsonify({
        "status": "ok", 
        "workers": NUM_WORKERS, 
        "busy": sum(_busy), 
        "queue": _queue.qsize(),
        "memory": gc.get_count()
    })

@app.route('/clear_queue', methods=['POST'])
def clear_queue():
    with _rlock:
        size = _queue.qsize()
        while not _queue.empty():
            try:
                _queue.get_nowait()
                _queue.task_done()
            except:
                break
        _results.clear()
        _events.clear()
    return jsonify({"status": "ok", "cleared": size})

if __name__ == '__main__':
    print("=" * 60)
    print("Shiro Shopify API v7.0 - AUTO-RESTART & MEMORY CLEANER")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Auto-restart: Every {AUTO_RESTART_INTERVAL//3600} hour(s)")
    print("=" * 60)
    _start()
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
