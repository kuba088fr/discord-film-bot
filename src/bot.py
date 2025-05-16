import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

import discord
from discord.ext import commands
import requests

# Absolute imports from src package
from src.db import init_db, save_user_preference, get_user_preference, get_connection
from src.movie_api import get_random_movie, _load_genres, BASE_URL, API_KEY

# Get your Discord token from the environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

# Disable the default help command so we can define our own
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

@bot.event
async def on_ready():
    init_db()
    print(f"Bot logged in as {bot.user.name} ({bot.user.id})")

@bot.command(name="help")
async def help_command(ctx):
    """Show available commands."""
    help_text = (
        "**📖 Available Commands:**\n"
        "`/hello` — test if the bot is online\n"
        "`/setfavorite <genre>` — set your favorite genre\n"
        "`/removefavorite` — remove your favorite genre\n"
        "`/listgenres` — list all supported genres\n"
        "`/search <query>` — search movies by title\n"
        "`/recommend` — get a movie recommendation based on your favorite genre\n"
    )
    await ctx.send(help_text)

@bot.command(name="hello")
async def hello(ctx):
    """Basic test command to check if the bot is responsive."""
    await ctx.send(f"Hello {ctx.author.display_name}! I am ready!")

@bot.command(name="setfavorite")
async def set_favorite(ctx, genre: str):
    """Set or update the user's favorite genre."""
    save_user_preference(str(ctx.author.id), genre.lower())
    await ctx.send(f"✅ Your favorite genre has been set to: **{genre}**")

@bot.command(name="removefavorite")
async def remove_favorite(ctx):
    """Remove the user's favorite genre from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_preferences WHERE user_id = %s",
        (str(ctx.author.id),)
    )
    conn.commit()
    cursor.close()
    conn.close()
    await ctx.send(
        "🗑️ Your favorite genre has been removed. Set a new one using `/setfavorite <genre>`."
    )

@bot.command(name="listgenres")
async def list_genres(ctx):
    """Display a list of all supported genres."""
    genres = _load_genres()
    names = sorted(genres.keys())
    chunks = [", ".join(names[i:i+10]) for i in range(0, len(names), 10)]
    await ctx.send("🎞️ Supported genres:\n" + "\n".join(chunks))

@bot.command(name="search")
async def search(ctx, *, query: str):
    """Search for movies by title (top 5 results)."""
    resp = requests.get(
        f"{BASE_URL}/search/movie",
        params={
            "api_key": API_KEY,
            "query": query,
            "language": "en-US",
            "include_adult": False
        }
    ).json().get("results", [])
    if not resp:
        return await ctx.send(f'🔍 No movies found for "{query}".')
    top5 = resp[:5]
    lines = [f"{f['title']} ({f.get('release_date', '?')[:4]})" for f in top5]
    await ctx.send("🔍 Top 5 results:\n" + "\n".join(lines))

@bot.command(name="recommend")
async def recommend(ctx):
    """Recommend a random movie based on the user's favorite genre."""
    genre = get_user_preference(str(ctx.author.id))
    if not genre:
        return await ctx.send(
            '⚠️ Please set a favorite genre first using `/setfavorite <genre>`.'
        )
    movie = get_random_movie(genre)
    await ctx.send(f'🎬 Recommendation for **{genre}**: {movie}')

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN is not set. Make sure you have a .env file with the token.")
    else:
        print("Starting bot...")
        bot.run(DISCORD_TOKEN)
