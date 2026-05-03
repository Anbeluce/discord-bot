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

    async def setup_hook(self):
        # Tải các Cogs (Module)
        await self.load_extension('cogs.voice')
        await self.load_extension('cogs.admin')


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
