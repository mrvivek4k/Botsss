import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_ROLE = os.getenv('ADMIN_ROLE', 'Admin')
BOT_PREFIX = os.getenv('BOT_PREFIX', '$')
WATERMARK = os.getenv('WATERMARK', 'Powered by Semicloud Gen')

# Define bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance
bot = commands.Bot(
    command_prefix=BOT_PREFIX,
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# Custom emoji IDs (replace with your server's emoji IDs)
EMOJI = {
    'success': '<:success:123456789012345678>',
    'error': '<:error:123456789012345678>',
    'info': '<:info:123456789012345678>',
    'warning': '<:warning:123456789012345678>',
    'stock': '<:stock:123456789012345678>',
    'gen': '<:gen:123456789012345678>',
    'admin': '<:admin:123456789012345678>',
    'vouch': '<:vouch:123456789012345678>'
}

# Colors for embeds
COLORS = {
    'primary': 0x5865F2,   # Blurple
    'success': 0x57F287,   # Green
    'error': 0xED4245,     # Red
    'warning': 0xFEE75C,   # Yellow
    'info': 0xEB459E      # Pink
}

# Ensure required directories exist
os.makedirs('stock', exist_ok=True)
os.makedirs('images', exist_ok=True)
os.makedirs('logs', exist_ok=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    
    # Load cogs
    await load_cogs()
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")

async def load_cogs():
    """Load all cogs from the cogs directory"""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded cog: {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load cog {filename}: {e}')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = create_embed(
            title=f"{EMOJI['error']} Missing Argument",
            description=f"Please provide all required arguments.\n\n**Usage:**\n`{ctx.prefix}{ctx.command.name} {ctx.command.signature}`",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = create_embed(
            title=f"{EMOJI['error']} Missing Permissions",
            description="You don't have permission to use this command.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CheckFailure):
        embed = create_embed(
            title=f"{EMOJI['error']} Access Denied",
            description="You don't have the required role to use this command.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)
    else:
        embed = create_embed(
            title=f"{EMOJI['error']} Error Occurred",
            description=f"An unexpected error occurred: ```{str(error)}```",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)
        raise error

def create_embed(title=None, description=None, color=None, fields=None, footer=True, thumbnail=None):
    """Helper function to create consistent embeds"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color or COLORS['primary'],
        timestamp=datetime.datetime.now()
    )
    
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    
    if footer:
        embed.set_footer(text=WATERMARK)
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    return embed

def log_generation(user_id, service, account):
    """Log account generation to file"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] User: {user_id} | Service: {service} | Account: {account}\n"
    
    with open('logs/gen_logs.txt', 'a', encoding='utf-8') as f:
        f.write(log_entry)

def get_stock_count(service):
    """Get the number of accounts in stock for a service"""
    file_path = f'stock/{service.lower()}.txt'
    if not os.path.exists(file_path):
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    return len(lines)

def get_random_account(service):
    """Get and remove a random account from stock"""
    file_path = f'stock/{service.lower()}.txt'
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        accounts = f.readlines()
    
    if not accounts:
        return None
    
    # Select random account and remove it
    import random
    account = random.choice(accounts)
    accounts.remove(account)
    
    # Write updated stock back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(accounts)
    
    return account.strip()

if __name__ == '__main__':
    bot.run(TOKEN)