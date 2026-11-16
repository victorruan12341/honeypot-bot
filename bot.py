print("script iniciou")
import os
import discord
from dotenv import load_dotenv

load_dotenv("bot.env")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_IDS = {
    int(i) for i in os.getenv("HONEYPOT_CHANNEL_IDS", "").split(",") if i.strip()
}
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
PROTECTED_IDS = {
    int(i) for i in os.getenv("PROTECTED_USER_IDS", "").split(",") if i.strip()
}
if not TOKEN or not CHANNEL_IDS:
    raise SystemExit("Defina DISCORD_TOKEN e HONEYPOT_CHANNEL_IDS no arquivo .env")

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    modo = "SIMULAÇÃO (não bane)" if DRY_RUN else "ATIVO (bane de verdade)"
    print(f"Online como {client.user} | Modo: {modo}")
    print(f"Canais armadilha: {CHANNEL_IDS}")


@client.event
async def on_message(message: discord.Message):
    # ignora bots e mensagens privadas
    if message.author.bot or message.guild is None:
        return

    # só age nos canais armadilha
    if message.channel.id not in CHANNEL_IDS:
        return

    member = message.author

        # protege só o dono e os IDs da lista
    if member.id in PROTECTED_IDS or member.id == message.guild.owner_id:
        return

    if DRY_RUN:
        print(f"[SIMULAÇÃO] Baniria {member} ({member.id}) em {message.guild.name}")
        return

    try:
        await member.ban(
            reason="Caiu no canal honeypot",
            delete_message_seconds=3600,  # apaga as mensagens da última hora
        )
        print(f"Banido: {member} ({member.id}) em {message.guild.name}")
    except discord.Forbidden:
        print("Sem permissão: confira o cargo do bot e a permissão Ban Members")
    except discord.HTTPException as e:
        print(f"Erro ao banir: {e}")


client.run(TOKEN)