import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput

TOKEN = "token"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=",", intents=intents)

_temp = {}

async def embedconf(interaction, text, success=True):
    color = 0x1c1c1c
    icon = "<:success:1402754707306315786>" if success else "<:error:1402754697248505876>"
    await interaction.response.send_message(
        embed=discord.Embed(description=f"> {icon} {text}", color=color),
        ephemeral=True
    )

class renamemodal(Modal, title="Rename Voice Channel"):
    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel
        self.new_name = TextInput(label="Reanem", placeholder="Enter new name", max_length=100)
        self.add_item(self.new_name)

    async def onsubmit(self, interaction: discord.Interaction):
        await self.channel.edit(name=self.new_name.value)
        await embedconf(interaction, f"Voice channel renamed to **{self.new_name.value}**")

class buttonsSetup(Button):
    def __init__(self, emoji_name, label, action, channel, style=discord.ButtonStyle.secondary):
        super().__init__(emoji=emoji_name, label="", style=style)
        self.action = action
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        is_owner = _temp.get(self.channel.id) == interaction.user.id
        has_permission = self.channel.permissions_for(interaction.user).manage_channels

        if self.action != "Create" and not (is_owner or has_permission):
            await embedconf(interaction, "You are not the owner of this voice channel!", success=False)
            return

        try:
            if self.action == "Create":
                category = self.channel.category or interaction.guild.voice_channels[0].category
                new_vc = await interaction.guild.create_voice_channel(f"{interaction.user.display_name}'s Room", category=category)
                _temp[new_vc.id] = interaction.user.id
                await embedconf(interaction, f"Created a new voice channel: {new_vc.mention}")
            elif self.action == "Lock":
                await self.channel.set_permissions(self.channel.guild.default_role, connect=False)
                await embedconf(interaction, "Voice channel locked!")
            elif self.action == "Unlock":
                await self.channel.set_permissions(self.channel.guild.default_role, connect=True)
                await embedconf(interaction, "Voice channel unlocked!")
            elif self.action == "Hide":
                await self.channel.set_permissions(self.channel.guild.default_role, view_channel=False)
                await embedconf(interaction, "Voice channel hidden!")
            elif self.action == "Reveal":
                await self.channel.set_permissions(self.channel.guild.default_role, view_channel=True)
                await embedconf(interaction, "Voice channel revealed!")
            elif self.action == "Rename":
                await interaction.response.send_modal(renamemodal(self.channel))
            elif self.action == "Claim":
                _temp[self.channel.id] = interaction.user.id
                await embedconf(interaction, "You are now the owner of this channel!")
            elif self.action == "Increase":
                new_limit = min((self.channel.user_limit or 0) + 1, 99)
                await self.channel.edit(user_limit=new_limit)
                await embedconf(interaction, f"User limit increased to `{new_limit}`")
            elif self.action == "Decrease":
                new_limit = max((self.channel.user_limit or 1) - 1, 0)
                await self.channel.edit(user_limit=new_limit)
                await embedconf(interaction, f"User limit decreased to `{new_limit}`")
            elif self.action == "Delete":
                await embedconf(interaction, "Voice channel deleted!")
                await self.channel.delete()
        except:
            await embedconf(interaction, "Something went wrong!", success=False)

class voiceView(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        buttons = [ # update the emojis (<:emojiname:id>) with your own 😉
            ("<:create:1402752754715201597>", "Create"),
            ("<:lock:1402752712256393317>", "Lock"),
            ("<:unlock:1402752705142849536>", "Unlock"),
            ("<:hide:1402754025832579194>", "Hide"),
            ("<:reveal:1402752688822685788>", "Reveal"),
            ("<:rename:1402752695156215859>", "Rename"),
            ("<:claim:1402752647810908210>", "Claim"),
            ("<:increase:1402752722150756402>", "Increase"),
            ("<:decrease:1402752747010265248>", "Decrease"),
            ("<:delete:1402752739254992998>", "Delete"),
        ]
        for emoji, action in buttons:
            self.add_item(buttonsSetup(emoji, "", action, channel))

@bot.command(name="panel")
async def panel(ctx):
    voice_state = ctx.author.voice
    if not voice_state or not voice_state.channel:
        return await ctx.send(embed=discord.Embed(
            description="> <:error:1402754697248505876> You must be in a voice channel to use this.",
            color=0x1c1c1c
        ))

    channel = voice_state.channel
    if channel.id not in _temp:
        _temp[channel.id] = ctx.author.id

    embed = discord.Embed(
        title="Voicemaster Panel",
        description="Easily manage and customize your own personal voice channel using the buttons below.",
        color=discord.Color.from_str("#1c1c1c")
    )
    await ctx.send(embed=embed, view=voiceView(channel))

bot.run(TOKEN)
