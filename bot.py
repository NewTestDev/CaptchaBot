import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from flask import Flask
import threading

# Charger le fichier .env pour obtenir le token en toute sécurité
load_dotenv()

# Lire le token à partir du fichier .env
TOKEN = os.getenv("DISCORD_TOKEN")

# Vérifier si le token a été correctement chargé
if not TOKEN:
    print("❌ Token non trouvé. Assurez-vous que le fichier .env est présent et correctement configuré.")
    exit(1)  # Arrêter l'exécution du bot si le token est manquant

# Configuration du bot Discord
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# IDs à jour
ROLE_ID = 1348599259276247061
CHANNEL_ID = 1348599259276247068

class BoutonAcces(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Permet de rendre le bouton persistant

    @discord.ui.button(label="Je ne suis pas un robot 🔄️", style=discord.ButtonStyle.primary, custom_id="verif_button")
    async def bouton(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Accès accordé !", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erreur, rôle introuvable.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

    # Enregistre le bouton dans le bot (indispensable pour qu'il marche après un restart)
    try:
        bot.add_view(BoutonAcces())
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout de la vue : {e}")

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ Erreur : Le salon n'a pas été trouvé. Vérifie l'ID.")
        return

    # Vérifie si un message avec un bouton existe déjà
    async for message in channel.history(limit=10):
        if message.author == bot.user and len(message.components) > 0:
            print("✅ Bouton déjà en place, pas besoin de renvoyer.")
            return  # Si un bouton existe déjà, on ne le recrée pas

    await channel.send(" ", view=BoutonAcces())  # Envoie le bouton si absent
    print("✅ Bouton envoyé dans le salon !")

# Créer un serveur Flask pour maintenir le bot en ligne
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"  # Une réponse simple pour prouver que ton bot est en vie

def run_flask():
    app.run(host="0.0.0.0", port=8080)  # Le port 8080 est utilisé par Render

# Lancer Flask dans un thread séparé pour ne pas bloquer ton bot
threading.Thread(target=run_flask, daemon=True).start()

# Utiliser le token depuis .env
bot.run(TOKEN)