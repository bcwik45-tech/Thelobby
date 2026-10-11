import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime
import os

# Konfiguracja intencji
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- ID KANAŁÓW I RÓL ---
BOOST_CHANNEL_ID = 1558818745084805190

# Role do autoroli (kategorie)
AUTOROLE_DATA = {
    "CS": 1558280731627880518,
    "FN": 1558280885587935344,
    "GTA": 1558281042870145064,
    "Inne": 1558281149569175604
}

# Kategorie ticketów (ID kategorii na serwerze Discord)
TICKET_CATEGORIES = {
    "Rekrutacja": 1558817096534855751,
    "Partnerstwo": 1558817268799111238,
    "Owner": 155881735224060315
}

# Role posiadające dostęp do danych ticketów (oraz do pingowania)
TICKET_ROLES = {
    "Rekrutacja": [1558480828156088471],
    "Partnerstwo": [1558279332592361522, 1558279751376965742],
    "Owner": [1558279332592361522, 1558279751376965742]
}


@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend slash.")
    except Exception as e:
        print(e)


# ==================== PRZYWITANIA ====================
@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.system_channel
    if not channel:
        return

    embed = discord.Embed(
        title="New member!",
        description=f"🎉 Hi\n{member.mention}\nWelcome to the best cfg in Poland!\nGo check out our stuff!",
        color=discord.Color.from_rgb(40, 40, 40)
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    
    member_count = member.guild.member_count
    embed.add_field(name="", value=f"**You're our {member_count} member!**", inline=False)
    
    created_at_str = member.created_at.strftime("%d.%m.%Y %H:%M:%S")
    joined_at_str = member.joined_at.strftime("%d.%m.%Y %H:%M")
    
    info_text = (
        f"💳 **Discord account created:**\n{created_at_str}\n"
        f"👤 **Username:** `{member.name}`\n"
        f"📅 **Joined at:** {joined_at_str}"
    )
    embed.add_field(name="Member Info:", value=info_text, inline=False)

    await channel.send(embed=embed)


# ==================== BOOSTY ====================
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.premium_since is None and after.premium_since is not None:
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if channel:
            boost_count = after.guild.premium_subscription_count
            boost_level = after.guild.premium_tier
            
            embed = discord.Embed(
                title="New server Boost!",
                description=f"{after.mention} **BOOST!**\nthanks for boosting our server!\nGo check out our booster zone!",
                color=discord.Color.from_rgb(150, 100, 255)
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            
            info_text = (
                f"🧊 **Server Boost level:** `{boost_level}`\n"
                f"🔢 **Boost count:** `{boost_count}`"
            )
            embed.add_field(name="Boost Info:", value=info_text, inline=False)
            embed.set_image(url="https://images.unsplash.com/photo-1550684848-fac1c5b4e853")
            
            await channel.send(embed=embed)


# ==================== KOMENDY /bandc i /unbandc ====================
@bot.tree.command(name="bandc", description="Banuje użytkownika.")
async def bandc(interaction: discord.Interaction, member: discord.Member, reason: str = "Brak powodu"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Nie masz uprawnień do banowania!", ephemeral=True)
        return
    
    await member.ban(reason=reason)
    await interaction.response.send_message(f"Pomyślnie zbanowano użytkownika {member.mention}. Powód: {reason}")

@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika po ID.")
async def unbandc(interaction: discord.Interaction, user_id: str, reason: str = "Brak powodu"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Nie masz uprawnień do odbanowywania!", ephemeral=True)
        return
    
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=reason)
        await interaction.response.send_message(f"Pomyślnie odbanowano użytkownika {user.name}.")
    except Exception as e:
        await interaction.response.send_message(f"Wystąpił błąd podczas odbanowywania: {e}", ephemeral=True)


# ==================== AUTOROLA SETUP ====================
class AutoRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)

    async def handle_role(self, interaction: discord.Interaction, role_id: int, role_name: str):
        role = interaction.guild.get_role(role_id)
        if not role:
            await interaction.response.send_message("Rola nie istnieje na tym serwerze!", ephemeral=True)
            return
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Pomyślnie **usunięto** rolę {role.name}.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Pomyślnie **nadano** rolę {role.name}.", ephemeral=True)

    @discord.ui.button(label="CS", style=discord.ButtonStyle.primary, custom_id="role_cs")
    async def cs_button(self, interaction: discord.Interaction, button: Button):
        await self.handle_role(interaction, AUTOROLE_DATA["CS"], "CS")

    @discord.ui.button(label="FN", style=discord.ButtonStyle.primary, custom_id="role_fn")
    async def fn_button(self, interaction: discord.Interaction, button: Button):
        await self.handle_role(interaction, AUTOROLE_DATA["FN"], "FN")

    @discord.ui.button(label="GTA", style=discord.ButtonStyle.primary, custom_id="role_gta")
    async def gta_button(self, interaction: discord.Interaction, button: Button):
        await self.handle_role(interaction, AUTOROLE_DATA["GTA"], "GTA")

    @discord.ui.button(label="Inne", style=discord.ButtonStyle.secondary, custom_id="role_inne")
    async def inne_button(self, interaction: discord.Interaction, button: Button):
        await self.handle_role(interaction, AUTOROLE_DATA["Inne"], "Inne")


@bot.tree.command(name="setup_autorola", description="Wysyła panel wybierania ról (CS, FN, GTA, Inne).")
async def setup_autorola(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Musisz być administratorem!", ephemeral=True)
        return

    embed = discord.Embed(
        title="Wybierz swoje role gry",
        description="Kliknij odpowiedni przycisk poniżej, aby otrzymać lub usunąć daną rolę.",
        color=discord.Color.blurple()
    )
    await interaction.channel.send(embed=embed, view=AutoRoleView())
    await interaction.response.send_message("Wysłano panel autoroli!", ephemeral=True)


# ==================== TICKETY ====================
class TicketCreateView(View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        guild = interaction.guild
        category_id = TICKET_CATEGORIES.get(ticket_type)
        category = guild.get_channel(category_id) if category_id else None
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        role_pings = []
        role_ids = TICKET_ROLES.get(ticket_type, [])
        for r_id in role_ids:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
                role_pings.append(role.mention)

        channel_name = f"ticket-{ticket_type.lower()}-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        pings_str = " ".join(role_pings)
        embed = discord.Embed(
            title=f"Ticket: {ticket_type}",
            description=f"Witaj {interaction.user.mention}!\nOpisz swój problem lub sprawę. Administracja wkrótce odpowie.",
            color=discord.Color.green()
        )
        
        class CloseTicketView(View):
            @discord.ui.button(label="Zamknij ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
            async def close_btn(self, inter: discord.Interaction, btn: Button):
                await inter.response.send_message("Zamykanie kanału za 3 sekundy...")
                import asyncio
                await asyncio.sleep(3)
                await inter.channel.delete()

        await ticket_channel.send(content=pings_str, embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"Utworzono ticket: {ticket_channel.mention}", ephemeral=True)

    @discord.ui.button(label="Owner 👑", style=discord.ButtonStyle.grey, custom_id="ticket_owner")
    async def owner_ticket(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "Owner")

    @discord.ui.button(label="Partnerstwo", style=discord.ButtonStyle.blurple, custom_id="ticket_partner")
    async def partner_ticket(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "Partnerstwo")

    @discord.ui.button(label="Recruitment 📄", style=discord.ButtonStyle.danger, custom_id="ticket_recruitment")
    async def recruitment_ticket(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "Rekrutacja")


@bot.tree.command(name="setup_tickets", description="Wysyła panel tworzenia ticketów.")
async def setup_tickets(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Musisz być administratorem!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎫 Tickets",
        description=(
            "Want to place an order, need to contact the owner or staff for help?\n"
            "Click the appropriate button below to open a private channel with the administration.\n\n"
            "Please don't open the tickets without a proper reason."
        ),
        color=discord.Color.dark_embed()
    )
    await interaction.channel.send(embed=embed, view=TicketCreateView())
    await interaction.response.send_message("Wysłano panel ticketów!", ephemeral=True)


# Uruchomienie bota przy użyciu zmiennej środowiskowej z Railway
bot.run(os.getenv("DISCORD_TOKEN"))