import discord
from discord.ext import commands
import asyncio
from utils.logger import send_log

class VoiceEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user:
            guild_id = member.guild.id
            
            # Kiểm tra xem bot có đang nằm trong danh sách cần "giữ chỗ" không
            if guild_id in self.bot.active_channels:
                target_channel_id = self.bot.active_channels[guild_id]
                
                # Trường hợp 1: Bot bị văng ra hoặc bị kick khỏi kênh thoại
                if before.channel and after.channel is None:
                    await send_log(f'⚠️ [Server: {member.guild.name}] Bot bị ngắt kết nối. Đang thử kết nối lại sau 1 giây...')
                    await asyncio.sleep(1)
                    
                    target_channel = self.bot.get_channel(target_channel_id)
                    if target_channel:
                        try:
                            # Dọn dẹp kết nối cũ nếu còn kẹt trước khi kết nối lại
                            if member.guild.voice_client:
                                await member.guild.voice_client.disconnect(force=True)
                                
                            await target_channel.connect(self_deaf=True, self_mute=False)
                            await send_log(f'🎙️ [Server: {member.guild.name}] Đã kết nối lại thành công vào kênh: {target_channel.name}')
                        except Exception as e:
                            await send_log(f'❌ [Server: {member.guild.name}] Lỗi khi kết nối lại: {e}')
                
                # Trường hợp 2: Bot bị di chuyển sang kênh thoại khác
                elif before.channel and after.channel and after.channel.id != target_channel_id:
                    await send_log(f'⚠️ [Server: {member.guild.name}] Bot bị di chuyển sang kênh khác. Đang quay lại kênh cũ...')
                    await asyncio.sleep(1)
                    
                    target_channel = self.bot.get_channel(target_channel_id)
                    if target_channel and member.guild.voice_client:
                        try:
                            await member.guild.voice_client.move_to(target_channel)
                            await send_log(f'🎙️ [Server: {member.guild.name}] Đã quay lại kênh: {target_channel.name}')
                        except Exception as e:
                            await send_log(f'❌ [Server: {member.guild.name}] Lỗi khi quay lại kênh cũ: {e}')

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceEventsCog(bot))
