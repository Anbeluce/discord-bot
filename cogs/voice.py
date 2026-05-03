import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.logger import send_log
from config import check_permission

class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Lưu trữ các kênh thoại mà bot đang "giữ chỗ" (theo format: guild_id -> channel_id)
        self.active_channels = {}

    @app_commands.command(name="join", description="Gọi bot lọ chéo")
    async def join(self, interaction: discord.Interaction):
        if not check_permission("join", interaction.user.id):
            await interaction.response.send_message("❌ Bạn không có quyền dùng lệnh này!", ephemeral=True)
            return
            
        channel = None
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
            await interaction.response.send_message(
                "❌ Bot không thấy bạn trong kênh thoại nào! Hãy thử **thoát kênh thoại rồi vào lại**, hoặc kiểm tra xem bot đã được cấp quyền Xem Kênh chưa nhé.", 
                ephemeral=True
            )
            return
        
        guild_id = interaction.guild.id
        voice_client = interaction.guild.voice_client
        
        # Nếu bot đã ở trong 1 kênh của server này
        if voice_client and voice_client.is_connected():
            if voice_client.channel.id == channel.id:
                await interaction.response.send_message(f"✅ Bot đã ở sẵn trong kênh {channel.mention} rồi nhé!", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Bot đang lọ chéo {voice_client.channel.mention} rồi nhé!", ephemeral=True)
            return
        else:
            # Nếu bot chưa ở kênh nào, tham gia vào kênh mới
            try:
                await channel.connect(self_deaf=True, self_mute=True)
                self.active_channels[guild_id] = channel.id
                await interaction.response.send_message(f"Bắt đầu lọ chéo ở {channel.mention} ")
                await send_log(f'🎙️ [Server: {interaction.guild.name}] Đã tham gia kênh: {channel.name}')
            except Exception as e:
                await interaction.response.send_message("❌ Lỗi khi kết nối vào kênh thoại. Kiểm tra lại quyền của bot.", ephemeral=True)
                await send_log(f'❌ [Server: {interaction.guild.name}] Lỗi kết nối: {e}')

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
            if guild_id in self.active_channels:
                del self.active_channels[guild_id]
                
            await interaction.response.send_message("👋.")
            await send_log(f'👋 [Server: {interaction.guild.name}] Đã rời kênh thoại theo yêu cầu.')
        else:
            await interaction.response.send_message("❌ Bot không ở trong kênh thoại nào cả.", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Xử lý tự động kết nối lại khi bot bị văng ra (do mạng hoặc bị kick)
        if member == self.bot.user and before.channel and after.channel is None:
            guild_id = before.channel.guild.id
            
            # Kiểm tra xem bot có đang nằm trong danh sách cần "giữ chỗ" không
            if guild_id in self.active_channels:
                target_channel_id = self.active_channels[guild_id]
                
                # Nếu người dùng không gọi /leave, bot sẽ tự động cố gắng kết nối lại
                await send_log(f'⚠️ [Server: {before.channel.guild.name}] Bot bị ngắt kết nối. Đang thử kết nối lại sau 5 giây...')
                await asyncio.sleep(5)
                
                target_channel = self.bot.get_channel(target_channel_id)
                if target_channel:
                    try:
                        # Dọn dẹp kết nối cũ nếu còn kẹt trước khi kết nối lại
                        if member.guild.voice_client:
                            await member.guild.voice_client.disconnect(force=True)
                            
                        await target_channel.connect(self_deaf=True, self_mute=True)
                        await send_log(f'🎙️ [Server: {before.channel.guild.name}] Đã kết nối lại thành công vào kênh: {target_channel.name}')
                    except Exception as e:
                        await send_log(f'❌ [Server: {before.channel.guild.name}] Lỗi khi kết nối lại: {e}')

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
