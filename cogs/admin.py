import discord
from discord.ext import commands
import os
import aiohttp
from main import create_embed, EMOJI, COLORS

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        """Check if user has admin role"""
        admin_role = discord.utils.get(ctx.guild.roles, name=ADMIN_ROLE)
        if not admin_role:
            return False
        return admin_role in ctx.author.roles
    
    @commands.hybrid_command(name='stock_add', description='Add stock to a service (Admin only)')
    async def stock_add(self, ctx, service: str):
        """Add accounts to a service's stock via file upload"""
        if not ctx.message.attachments:
            embed = create_embed(
                title=f"{EMOJI['error']} Missing File",
                description="Please upload a .txt file with accounts.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith('.txt'):
            embed = create_embed(
                title=f"{EMOJI['error']} Invalid File",
                description="Please upload a .txt file.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # Download the file
        file_path = f'stock/{service.lower()}.txt'
        await attachment.save(file_path)
        
        # Count lines added
        with open(file_path, 'r', encoding='utf-8') as f:
            count = len(f.readlines())
        
        embed = create_embed(
            title=f"{EMOJI['success']} Stock Added",
            description=f"Successfully added `{count}` accounts to **{service}** stock.",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='create', description='Create a new service file (Admin only)')
    async def create(self, ctx, service: str):
        """Create a new empty service file"""
        file_path = f'stock/{service.lower()}.txt'
        if os.path.exists(file_path):
            embed = create_embed(
                title=f"{EMOJI['error']} Service Exists",
                description=f"**{service}** already exists.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        open(file_path, 'w').close()
        
        embed = create_embed(
            title=f"{EMOJI['success']} Service Created",
            description=f"Created new service: **{service}**",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='clear', description='Clear all stock for a service (Admin only)')
    async def clear(self, ctx, service: str):
        """Clear all accounts from a service"""
        file_path = f'stock/{service.lower()}.txt'
        if not os.path.exists(file_path):
            embed = create_embed(
                title=f"{EMOJI['error']} Service Not Found",
                description=f"**{service}** does not exist.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # Get count before clearing
        with open(file_path, 'r', encoding='utf-8') as f:
            count = len(f.readlines())
        
        open(file_path, 'w').close()
        
        embed = create_embed(
            title=f"{EMOJI['success']} Stock Cleared",
            description=f"Cleared `{count}` accounts from **{service}**.",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='drop', description='Drop accounts into channel (Admin only)')
    async def drop(self, ctx, service: str, count: int = 1):
        """Drop accounts into channel without removing from stock"""
        file_path = f'stock/{service.lower()}.txt'
        if not os.path.exists(file_path):
            embed = create_embed(
                title=f"{EMOJI['error']} Service Not Found",
                description=f"**{service}** does not exist.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            accounts = f.readlines()
        
        if not accounts:
            embed = create_embed(
                title=f"{EMOJI['error']} Out of Stock",
                description=f"No accounts available for **{service}**.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        count = min(count, len(accounts))
        dropped = accounts[:count]
        
        embed = create_embed(
            title=f"{EMOJI['admin']} Accounts Dropped",
            description=f"Dropped `{count}` **{service}** accounts:",
            color=COLORS['info']
        )
        
        account_list = '\n'.join([f"`{acc.strip()}`" for acc in dropped])
        embed.add_field(name="Accounts", value=account_list, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))