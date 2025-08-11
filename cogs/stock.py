import discord
from discord.ext import commands
import os
from main import create_embed, EMOJI, COLORS, log_generation, get_stock_count, get_random_account

class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='gen', description='Generate an account from stock')
    async def gen(self, ctx, service: str):
        """Generate an account from the specified service"""
        account = get_random_account(service)
        
        if not account:
            embed = create_embed(
                title=f"{EMOJI['error']} Out of Stock",
                description=f"No accounts available for **{service}**.\nTry again later or check other services with `{ctx.prefix}stock`.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Send account to user's DMs
            dm_embed = create_embed(
                title=f"{EMOJI['gen']} Account Generated",
                description=f"Here's your **{service}** account:\n```{account}```\n\n**Important:**\n- Vouch in #bot-vouch after claiming\n- Do not share this account",
                color=COLORS['success'],
                footer=False
            )
            await ctx.author.send(embed=dm_embed)
            
            # Send success message in channel
            embed = create_embed(
                title=f"{EMOJI['success']} Account Delivered",
                description=f"Check your DMs for the **{service}** account!\n\n**Remember to vouch in** #bot-vouch",
                color=COLORS['success']
            )
            await ctx.send(embed=embed)
            
            # Log the generation
            log_generation(ctx.author.id, service, account)
            
        except discord.Forbidden:
            embed = create_embed(
                title=f"{EMOJI['error']} DMs Disabled",
                description="I couldn't send you the account because your DMs are disabled.\nPlease enable DMs and try again.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='stock', description='View available stock')
    async def stock(self, ctx):
        """Show all available services and their stock counts"""
        services = []
        for filename in os.listdir('stock'):
            if filename.endswith('.txt'):
                service_name = filename[:-4]
                count = get_stock_count(service_name)
                services.append((service_name, count))
        
        if not services:
            embed = create_embed(
                title=f"{EMOJI['error']} No Stock Available",
                description="There are currently no services with available stock.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        # Split into chunks for pagination if too many services
        chunks = [services[i:i + 10] for i in range(0, len(services), 10)]
        
        embeds = []
        for i, chunk in enumerate(chunks):
            fields = []
            for service, count in chunk:
                fields.append((
                    f"{EMOJI['stock']} {service.capitalize()}",
                    f"**Stock:** `{count}` accounts\n`{ctx.prefix}gen {service.lower()}`",
                    True
                ))
            
            embed = create_embed(
                title=f"{EMOJI['stock']} Available Stock",
                description=f"Use `{ctx.prefix}gen <service>` to claim an account.",
                color=COLORS['info'],
                fields=fields,
                thumbnail="https://i.imgur.com/xyz1234.png"  # Replace with your thumbnail URL
            )
            embed.set_footer(text=f"Page {i+1}/{len(chunks)} • {WATERMARK}")
            embeds.append(embed)
        
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            from discord.ext import menus
            class StockMenu(menus.Menu):
                def __init__(self, embeds):
                    super().__init__(timeout=60.0, delete_message_after=True)
                    self.embeds = embeds
                    self.current_page = 0
                
                async def send_initial_message(self, ctx, channel):
                    return await channel.send(embed=self.embeds[0])
                
                @menus.button('⬅️')
                async def on_previous(self, payload):
                    if self.current_page > 0:
                        self.current_page -= 1
                        await self.message.edit(embed=self.embeds[self.current_page])
                
                @menus.button('➡️')
                async def on_next(self, payload):
                    if self.current_page < len(self.embeds) - 1:
                        self.current_page += 1
                        await self.message.edit(embed=self.embeds[self.current_page])
            
            await StockMenu(embeds).start(ctx)
    
    @gen.error
    @stock.error
    async def stock_error(self, ctx, error):
        """Error handler for stock commands"""
        if isinstance(error, commands.MissingRequiredArgument):
            embed = create_embed(
                title=f"{EMOJI['error']} Missing Service",
                description=f"Please specify a service.\n\n**Example:**\n`{ctx.prefix}gen minecraft`",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stock(bot))