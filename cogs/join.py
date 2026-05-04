import discord
from discord.ext import commands
from discord import app_commands
from utils.logger import send_log
from config import check_permission

class JoinCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="join", description="Gọi bot lọ chéo")
    @app_commands.describe(target_channel="Kênh thoại bạn muốn bot tham gia (Bỏ trống để bot tự vào kênh bạn đang ở)")
    async def join(self, interaction: discord.Interaction, target_channel: discord.VoiceChannel = None):
        await interaction.response.defer(ephemeral=True)
        if not check_permission("join", interaction.user.id):
            await interaction.followup.send("❌ Bạn không có quyền dùng lệnh này!", ephemeral=True)
            return
            
        channel = target_channel
        
        # Nếu người dùng không chỉ định kênh, tự tìm kênh họ đang ở
        if not channel:
            # 1. Kiểm tra cache thông thường
            if interaction.user.voice and interaction.user.voice.channel:
                channel = interaction.user.voice.channel
            else:
                # 2. Quét thủ công phòng hờ lỗi cache của Discord
                for vc in interaction.guild.voice_channels:
                    if interaction.user in vc.members:
                        channel = vc
                        break

        if not channel:
            await interaction.followup.send(
                "❌ Bạn chưa chọn kênh và bot cũng không thấy bạn trong kênh thoại nào! Hãy chọn kênh hoặc tự tham gia kênh trước nhé.", 
                ephemeral=True
            )
            return
        
        guild_id = interaction.guild.id
        voice_client = interaction.guild.voice_client
        
        # Nếu bot đã ở trong 1 kênh của server này
        if voice_client and voice_client.is_connected():
            if voice_client.channel.id == channel.id:
                await interaction.followup.send(f"✅ Bot đã ở sẵn trong kênh {channel.mention} rồi nhé!", ephemeral=True)
            else:
                # Bot đang ở kênh khác, thực hiện chuyển kênh
                try:
                    # Cập nhật kênh cần giữ chỗ TRƯỚC KHI di chuyển để tránh voice_events kéo lại
                    self.bot.active_channels[guild_id] = channel.id
                    await voice_client.move_to(channel)
                    await interaction.followup.send(f"✅ Đã di chuyển sang kênh {channel.mention} theo yêu cầu!", ephemeral=True)
                    await send_log(f'🎙️ [Server: {interaction.guild.name}] Đã chuyển sang kênh: {channel.name}')
                except Exception as e:
                    await interaction.followup.send("❌ Lỗi khi chuyển kênh thoại. Kiểm tra lại quyền của bot.", ephemeral=True)
                    await send_log(f'❌ [Server: {interaction.guild.name}] Lỗi chuyển kênh: {e}')
            return
        else:
            # Nếu bot chưa ở kênh nào, tham gia vào kênh mới
            try:
                # Phải để self_mute=False thì bot mới có thể phát âm thanh (đọc văn bản) được
                await channel.connect(self_deaf=True, self_mute=False)
                self.bot.active_channels[guild_id] = channel.id
                await interaction.followup.send(f"Bắt đầu lọ chéo ở {channel.mention} ", ephemeral=True)
                await send_log(f'🎙️ [Server: {interaction.guild.name}] Đã tham gia kênh: {channel.name}')
            except Exception as e:
                await interaction.followup.send("❌ Lỗi khi kết nối vào kênh thoại. Kiểm tra lại quyền của bot.", ephemeral=True)
                await send_log(f'❌ [Server: {interaction.guild.name}] Lỗi kết nối: {e}')

async def setup(bot: commands.Bot):
    await bot.add_cog(JoinCog(bot))
