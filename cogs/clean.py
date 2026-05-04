import discord
from discord.ext import commands
from discord import app_commands
import os
from utils.logger import send_log
from config import check_permission

class CleanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clean", description="Xoá các file âm thanh lỗi còn sót lại trong cache")
    async def clean(self, interaction: discord.Interaction):
        if not check_permission("clean", interaction.user.id):
            await interaction.response.send_message("❌ Bạn không có quyền dùng lệnh này!", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        try:
            count = 0
            if os.path.exists("cache"):
                for file in os.listdir("cache"):
                    if file.startswith("tts_") and file.endswith(".mp3"):
                        file_path = os.path.join("cache", file)
                        try:
                            os.remove(file_path)
                            count += 1
                        except Exception as e:
                            print(f"Lỗi khi xóa file {file_path}: {e}")
                            
            await interaction.followup.send(f"✅ Đã dọn dẹp thành công **{count}** file âm thanh bị kẹt trong cache.", ephemeral=True)
            await send_log(f'🧹 [Admin] Đã dọn dẹp {count} file rác trong cache.')
        except Exception as e:
            await interaction.followup.send(f"❌ Đã có lỗi xảy ra: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CleanCog(bot))
