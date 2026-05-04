import discord
from discord.ext import commands
from discord import app_commands
from utils.logger import send_log
from config import check_permission

class LeaveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leave", description="Cho bot đi đái")
    async def leave(self, interaction: discord.Interaction):
        if not check_permission("leave", interaction.user.id):
            await interaction.response.send_message("❌", ephemeral=True)
            return
            
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            
            # Xoá khỏi danh sách giữ chỗ để bot không tự kết nối lại
            guild_id = interaction.guild.id
            if guild_id in self.bot.active_channels:
                del self.bot.active_channels[guild_id]
                
            await interaction.response.send_message("👋.", ephemeral=True)
            await send_log(f'👋 [Server: {interaction.guild.name}] Đã rời kênh thoại theo yêu cầu.')
        else:
            await interaction.response.send_message("❌ Bot không ở trong kênh thoại nào cả.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(LeaveCog(bot))
