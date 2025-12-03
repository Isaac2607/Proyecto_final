import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import unicodedata
from difflib import get_close_matches

# -------------------------
#   Cargar TOKEN del .env
# -------------------------
load_dotenv()
TOKEN = os.getenv("TOKEN")

# -------------------------
#   Configuración del bot
# -------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------
#   Base de datos
# -------------------------
VAT_RATES = {
    "usa": 0, "estados unidos": 0, "eeuu": 0,
    "mexico": 16, "méxico": 16,
    "canada": 5, "canadá": 5,
    "españa": 21, "espana": 21,
    "francia": 20, "alemania": 19, "italia": 22,
    "reino unido": 20, "argentina": 21, "chile": 19,
    "peru": 18, "perú": 18, "colombia": 19,
    "brasil": 17, "japon": 10, "japón": 10,
    "china": 13, "india": 18, "portugal": 23,
    "puerto rico": 11.5, "pr": 11.5
}

ISO_MAP = {
    "estados unidos": "US",
    "usa": "US",
    "eeuu": "US",
    "mexico": "MX",
    "canada": "CA",
    "espana": "ES",
    "francia": "FR",
    "alemania": "DE",
    "italia": "IT",
    "reino unido": "GB",
    "argentina": "AR",
    "chile": "CL",
    "peru": "PE",
    "colombia": "CO",
    "brasil": "BR",
    "japon": "JP",
    "china": "CN",
    "india": "IN",
    "portugal": "PT",
    "puerto rico": "PR",
    "pr": "PR"
}

# -------------------------
#   Normalizar país
# -------------------------
def normalizar(texto: str) -> str:
    """Convierte un texto en minúsculas y sin acentos."""
    t = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").strip()

# -------------------------
#   Obtener país
# -------------------------
def obtener_pais(args):
    """Detecta país de 1 o 2 palabras y devuelve país, precios_raw."""
    if len(args) >= 3:
        dos = normalizar(args[-2] + " " + args[-1])
        if dos in VAT_RATES:
            return args[-2] + " " + args[-1], args[:-2]
    return args[-1], args[:-1]

# -------------------------
#   Formatear lista de países
# -------------------------
def formatear_paises():
    lista = sorted(VAT_RATES.keys())
    bloques = []
    block = ""
    for p in lista:
        line = f"{p}\n"
        if len(block) + len(line) > 1900:
            bloques.append(block)
            block = ""
        block += line
    if block:
        bloques.append(block)
    return bloques

# -------------------------
#   Formatear VAT
# -------------------------
def formatear_vat():
    lista = sorted(VAT_RATES)
    bloques = []
    block = ""
    for p in lista:
        line = f"{p:<15} → {VAT_RATES[p]}%\n"
        if len(block) + len(line) > 1900:
            bloques.append(block)
            block = ""
        block += line
    if block:
        bloques.append(block)
    return bloques

# -------------------------
#   Bot listo
# -------------------------
@bot.event
async def on_ready():
    print(f"Bot iniciado como {bot.user}")

# -------------------------
#   !precio
# -------------------------
@bot.command()
async def precio(ctx, *args):
    if len(args) < 2:
        return await ctx.reply("❌ Uso: !precio <precio(s)> <país>")

    pais, precios_raw = obtener_pais(args)
    país_norm = normalizar(pais)

    # Convertir precios
    precios = []
    for p in precios_raw:
        try:
            precios.append(float(p))
        except ValueError:
            return await ctx.reply(f"❌ Precio inválido: `{p}`. Debe ser un número.")

    subtotal = sum(precios)

    # IVA del país
    iva = VAT_RATES.get(país_norm)
    if iva is None:
        # Sugerencias de país
        sugerencias = get_close_matches(país_norm, VAT_RATES.keys(), n=3, cutoff=0.6)
        texto_sugerencias = f" ¿Quizás quisiste decir: {', '.join(sugerencias)}?" if sugerencias else ""
        return await ctx.reply(f"❌ País no encontrado: **{pais}**.{texto_sugerencias}")

    iso = ISO_MAP.get(país_norm, "N/A")
    iva_total = subtotal * iva / 100
    total_final = subtotal + iva_total

    await ctx.reply(
        f"🌍 **{pais.title()}** ({iso})\n"
        f"💰 Subtotal: **${subtotal:.2f}**\n"
        f"🏛️ IVA ({iva}%): **${iva_total:.2f}**\n"
        f"✅ Total: **${total_final:.2f}**"
    )

# -------------------------
#   !paises
# -------------------------
@bot.command()
async def paises(ctx):
    for bloque in formatear_paises():
        await ctx.send(f"🌍 **Países disponibles:**\n```\n{bloque}```")

# -------------------------
#   !vat
# -------------------------
@bot.command()
async def vat(ctx):
    for bloque in formatear_vat():
        await ctx.send(f"🏛️ **VAT Rates:**\n```\n{bloque}```")

# -------------------------
#   !comandos
# -------------------------
@bot.command()
async def comandos(ctx):
    await ctx.send(
        "📌 **Comandos disponibles:**\n\n"
        "**!precio** → Calcula total con IVA\n"
        "**!paises** → Lista de países disponibles\n"
        "**!vat** → IVA de cada país\n"
        "**!comandos** → Lista de comandos\n"
    )

# -------------------------
#   Ejecutar bot
# -------------------------
bot.run(TOKEN)
