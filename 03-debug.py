import os
import sys

print("=" * 60)
print("🤖 DEBUG: Starting Roblox Bot")
print("=" * 60)

# Проверяем переменные
print(f"BOT_TOKEN: {'SET' if 'BOT_TOKEN' in os.environ else 'NOT SET'}")
if 'BOT_TOKEN' in os.environ:
    token = os.environ['BOT_TOKEN']
    print(f"Token length: {len(token)}")
    print(f"Token starts with: {token[:10]}...")

print(f"ADMIN_ID: {os.environ.get('ADMIN_ID', 'NOT SET')}")
print(f"PORT: {os.environ.get('PORT', '8080 (default)')}")

# Простой веб-сервер чтобы Railway видел что сервис живой
try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return """
        <h1>🤖 Roblox Cookie Bot</h1>
        <p>Service is RUNNING!</p>
        <p><a href="/health">Health Check</a></p>
        <p><a href="/check">Status Check</a></p>
        """
    
    @app.route('/health')
    def health():
        return "OK", 200
    
    @app.route('/check')
    def check():
        return {
            'status': 'online',
            'service': 'Roblox Cookie Bot',
            'bot_token_configured': 'BOT_TOKEN' in os.environ,
            'variables': {
                'BOT_TOKEN_set': 'BOT_TOKEN' in os.environ,
                'ADMIN_ID': os.environ.get('ADMIN_ID'),
                'PORT': os.environ.get('PORT', 8080)
            }
        }
    
    print("\n✅ Все импорты успешны!")
    print("🚀 Запускаю Flask сервер...")
    
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Порт: {port}")
    
    # Запускаем
    app.run(host='0.0.0.0', port=port)
    
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    print(f"Тип ошибки: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)