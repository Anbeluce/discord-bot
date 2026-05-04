import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
from utils.logger import send_log
from config import check_permission

class RestartCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="restart", description="Cho bot đi đái (Khởi động lại)")
    async def restart(self, interaction: discord.Interaction):
        if not check_permission("restart", interaction.user.id):
            await interaction.response.send_message("❌ stupid!", ephemeral=True)
            return
        
        await interaction.response.send_message("Bot đi đái đợi tí...", ephemeral=True)
        await send_log("🔄 Bot đang được khởi động lại bằng lệnh /restart...")
        
        # Khởi động lại tiến trình Python bằng cách thay thế process hiện tại
        os.execv(sys.executable, ['python'] + sys.argv)

async def setup(bot: commands.Bot):
    await bot.add_cog(RestartCog(bot))
