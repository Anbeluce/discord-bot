import discord
from discord.ext import commands
import os
import sys
from dotenv import load_dotenv
from utils.logger import send_log

# Tải biến môi trường từ file .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class VoiceHoldBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True
        super().__init__(command_prefix="!", intents=intents)
        # Lưu trữ các kênh thoại mà bot đang "giữ chỗ" (theo format: guild_id -> channel_id)
        self.active_channels = {}

    async def setup_hook(self):
        # Tự động tải tất cả các Cogs (Module) trong thư mục cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                except Exception as e:
                    print(f"Lỗi khi tải file {filename}: {e}")


        # Đồng bộ Slash Commands với Discord
        await self.tree.sync()
        await send_log("✅ Đã đồng bộ Slash Commands và Cogs.")

    async def on_ready(self):
        await send_log(f'✅ Đã đăng nhập thành công với tên: {self.user}')

if __name__ == "__main__":
    if not TOKEN or TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Lỗi: Chưa cấu hình DISCORD_TOKEN hợp lệ trong file .env")
    else:
        bot = VoiceHoldBot()
        bot.run(TOKEN)
