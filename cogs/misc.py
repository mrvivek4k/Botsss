import discord
from discord.ext import commands
from main import create_embed, EMOJI, COLORS

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='cmdlist', description='Show all available commands')
    async def cmdlist(self, ctx):
        """Show a paginated list of all commands"""
        # General commands
        general_commands = [
            ("gen <service>", "Generate an account from stock"),
            ("stock", "View available stock counts"),
            ("vouches [user]", "Check a user's vouch count"),
            ("cmdlist", "Show this command list")
        ]
        
        # Admin commands
        admin_commands = [
            ("stock_add <service>", "Add stock via file upload"),
            ("create <service>", "Create new service file"),
            ("clear <service>", "Clear all stock for a service"),
            ("drop <service> <count>", "Drop accounts into channel"),
            ("remove <user> <count>", "Remove vouches from a user")
        ]
        
        # Create embeds
        embeds = []
        
        # General commands embed
        general_fields = []
        for cmd, desc in general_commands:
            general_fields.append((f"`{ctx.prefix}{cmd}`", desc, False))
        
        general_embed = create_embed(
            title=f"{EMOJI['info']} Available Commands",
            description="**General Commands**",
            color=COLORS['primary'],
            fields=general_fields
        )
        embeds.append(general_embed)
        
        # Admin commands embed
        admin_fields = []
        for cmd, desc in admin_commands:
            admin_fields.append((f"`{ctx.prefix}{cmd}`", desc, False))
        
        admin_embed = create_embed(
            title=f"{EMOJI['admin']} Admin Commands",
            description="These commands require admin permissions.",
            color=COLORS['primary'],
            fields=admin_fields
        )
        embeds.append(admin_embed)
        
        # Send embeds
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            from discord.ext import menus
            class CmdListMenu(menus.Menu):
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
            
            await CmdListMenu(embeds).start(ctx)

async def setup(bot):
    await bot.add_cog(Misc(bot))