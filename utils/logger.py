import discord
import aiohttp
import os

async def send_log(message: str):
    """Hàm tiện ích giúp in log ra màn hình và gửi qua Discord Webhook"""
    print(message)
    
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url and webhook_url.strip():
        try:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(webhook_url, session=session)
                await webhook.send(content=message)
        except Exception as e:
            print(f"❌ Lỗi khi gửi webhook: {e}")
