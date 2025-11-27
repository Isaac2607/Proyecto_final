import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import unicodedata

# Cargar variables del .env (solo necesita TOKEN)
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Base de datos local de impuestos
VAT_RATES = {
    "estados unidos": 0,
    "usa": 0,
    "eeuu": 0,
    "mexico": 16,
    "méxico": 16,
    "canada": 5,
    "canadá": 5,
    "espana": 21,
    "españa": 21,
    "francia": 20,
    "alemania": 19,
    "italia": 22,
    "reino unido": 20,
    "argentina": 21,
    "chile": 19,
    "peru": 18,
    "perú": 18,
    "colombia": 19,
    "brasil": 17,
    "japon": 10,
    "japón": 10,
    "china": 13,
    "india": 18,
    "portugal": 23,

    # 🟦 Puerto Rico
    "puerto rico": 11.5,
    "pr": 11.5
}


# Mapas ISO locales
ISO_MAP = {
    "estados unidos": "us",
    "usa": "us",
    "méxico": "mx",
    "mexico": "mx",
    "canadá": "ca",
    "canada": "ca",
    "españa": "es",
    "espana": "es",
    "francia": "fr",
    "alemania": "de",
    "italia": "it",
    "reino unido": "gb",
    "japón": "jp",
    "japon": "jp",
    "china": "cn",
    "india": "in",
    "portugal": "pt",

    # 🟦 Puerto Rico
    "puerto rico": "pr",
    "pr": "pr"
}


# Normalizador de nombres de país
def normalize_country(name: str) -> str:
    name = name.lower()
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    return name.strip()

@bot.event
async def on_ready():
    print(f"Bot iniciado como {bot.user}")

# -----------------------------
#   COMANDO precio
# -----------------------------
@bot.command()
async def precio(ctx, *args):
    """
    Uso: !precio 100 200 300 españa
    El último argumento siempre se toma como país,
    los anteriores como precios.
    """
    if len(args) < 2:
        await ctx.reply("❌ Debes indicar al menos un precio y un país")
        return

    *precios_str, pais = args
    pais_normal = normalize_country(pais)

    # Convertir precios a float y sumar
    try:
        precios = [float(p) for p in precios_str]
    except ValueError:
        await ctx.reply("❌ Todos los precios deben ser números válidos")
        return

    total_sin_iva = sum(precios)

    # Buscar impuesto local
    tax_rate = VAT_RATES.get(pais_normal)
    if tax_rate is None:
        await ctx.reply(f"❌ País no encontrado en la base local: **{pais}**")
        return

    # ISO
    iso = ISO_MAP.get(pais_normal, "N/A")

    # Calcular precio final con IVA sobre la suma total
    precio_final = total_sin_iva * (1 + tax_rate / 100)

    await ctx.reply(
        f"🌍 País: **{pais.title()}** ({iso})\n"
        f"💰 Total base: **${total_sin_iva:.2f}**\n"
        f"🏛️ IVA (local {tax_rate}%): **${total_sin_iva * tax_rate / 100:.2f}**\n"
        f"✅ Total con impuesto: **${precio_final:.2f}**"
    )

bot.run(TOKEN)
