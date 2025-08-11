import discord
from discord.ext import commands
import json
import os
from main import create_embed, EMOJI, COLORS

# Vouch system storage
VOUCH_FILE = 'data/vouches.json'

class Vouches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vouches = {}
        self.load_vouches()
    
    def load_vouches(self):
        """Load vouch data from file"""
        os.makedirs('data', exist_ok=True)
        if os.path.exists(VOUCH_FILE):
            with open(VOUCH_FILE, 'r', encoding='utf-8') as f:
                self.vouches = json.load(f)
    
    def save_vouches(self):
        """Save vouch data to file"""
        with open(VOUCH_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.vouches, f, indent=4)
    
    @commands.hybrid_command(name='vouches', description='Check a user\'s vouch count')
    async def vouches(self, ctx, user: discord.Member = None):
        """Check how many vouches a user has"""
        target = user or ctx.author
        user_id = str(target.id)
        
        count = self.vouches.get(user_id, 0)
        
        embed = create_embed(
            title=f"{EMOJI['vouch']} Vouch Count",
            description=f"**{target.display_name}** has `{count}` vouches.",
            color=COLORS['info']
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='remove', description='Remove vouches from a user (Admin only)')
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, user: discord.Member, count: int = 1):
        """Remove vouches from a user"""
        user_id = str(user.id)
        
        if user_id not in self.vouches or self.vouches[user_id] <= 0:
            embed = create_embed(
                title=f"{EMOJI['error']} No Vouches",
                description=f"**{user.display_name}** has no vouches to remove.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        self.vouches[user_id] = max(0, self.vouches[user_id] - count)
        self.save_vouches()
        
        embed = create_embed(
            title=f"{EMOJI['success']} Vouches Removed",
            description=f"Removed `{count}` vouches from **{user.display_name}**.\nNew count: `{self.vouches[user_id]}`",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Automatically track vouches in the vouch channel"""
        if message.channel.name != 'bot-vouch':
            return
        
        if message.author.bot:
            return
        
        # Check if message contains "legit" or similar keywords
        content = message.content.lower()
        if 'legit' in content or 'vouch' in content or 'thanks' in content:
            # Find mentioned users
            for mention in message.mentions:
                if mention.bot and mention.id == self.bot.user.id:
                    # Bot was mentioned, give vouch to author
                    user_id = str(message.author.id)
                    self.vouches[user_id] = self.vouches.get(user_id, 0) + 1
                    self.save_vouches()
                    
                    embed = create_embed(
                        title=f"{EMOJI['vouch']} Vouch Recorded",
                        description=f"Thanks for your vouch! You now have `{self.vouches[user_id]}` vouches.",
                        color=COLORS['success']
                    )
                    await message.reply(embed=embed)
                    break

async def setup(bot):
    await bot.add_cog(Vouches(bot))