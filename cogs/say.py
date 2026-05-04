import discord
from discord.ext import commands
from discord import app_commands
import os
from gtts import gTTS
from utils.logger import send_log
from config import check_permission

class SayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists("cache"):
            os.makedirs("cache")

    @app_commands.command(name="say", description="Cho bot đọc một đoạn văn bản (Text-to-Speech)")
    @app_commands.describe(text="Đoạn văn bản muốn bot đọc")
    async def say(self, interaction: discord.Interaction, text: str):
        if not check_permission("say", interaction.user.id):
            await interaction.response.send_message("❌ Bạn không có quyền dùng lệnh này!", ephemeral=True)
            return
            
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            await interaction.response.send_message("❌ Bot chưa tham gia vào kênh thoại nào! Hãy dùng lệnh /join trước.", ephemeral=True)
            return

        # Phản hồi trước để tránh bị timeout do quá trình tải/chuyển đổi tốn thời gian
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Tạo file âm thanh từ văn bản (ngôn ngữ Tiếng Việt)
            tts = gTTS(text=text, lang='vi')
            filename = f"cache/tts_{interaction.id}.mp3"
            tts.save(filename)
            
            # Hàm dọn dẹp sau khi phát xong
            def after_playing(error):
                if error:
                    print(f"Lỗi phát audio: {error}")
                try:
                    if os.path.exists(filename):
                        os.remove(filename)
                except Exception as e:
                    print(f"Lỗi xoá file tts: {e}")
                    
            # Nếu bot đang phát âm thanh khác, phải dừng lại
            if voice_client.is_playing():
                voice_client.stop()
                
            # Đọc file âm thanh
            # THỬ CÁCH KHÔNG CẦN CÀI FFMPEG VÀO MÁY BẰNG IMAGEIO-FFMPEG
            try:
                import imageio_ffmpeg
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                source = discord.FFmpegPCMAudio(filename, executable=ffmpeg_path)
            except ImportError:
                # Nếu không có thư viện imageio_ffmpeg, dùng ffmpeg mặc định của hệ thống
                source = discord.FFmpegPCMAudio(filename)

            voice_client.play(source, after=after_playing)
            
            await interaction.followup.send(f"🔊 Đang đọc: **{text}**", ephemeral=True)
            await send_log(f'🔊 [Server: {interaction.guild.name}] Đã đọc: {text}')
            
        except Exception as e:
            if "ffmpeg" in str(e).lower() or "ffmpeg was not found" in str(e).lower():
                await interaction.followup.send("❌ Thiếu công cụ FFmpeg để phát nhạc. Đang tiến hành xử lý, bạn chờ chút nhé!", ephemeral=True)
            else:
                await interaction.followup.send("❌ Đã có lỗi xảy ra khi tạo hoặc phát âm thanh.", ephemeral=True)
            await send_log(f'❌ Lỗi lệnh say: {e}')

async def setup(bot: commands.Bot):
    await bot.add_cog(SayCog(bot))
