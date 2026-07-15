import discord
from discord.ext import commands
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN           = os.getenv("DISCORD_TOKEN")
GUILD_ID        = int(os.getenv("GUILD_ID"))
ROLE_ID         = int(os.getenv("ROLE_ID"))
COMMAND_ROLE_ID = int(os.getenv("COMMAND_ROLE_ID"))

# ── Intents ───────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.members         = True
intents.message_content = True
intents.voice_states    = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ── Persistent state ──────────────────────────────────────────────────────────
DATA_FILE = "data.json"

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"killed_members": [], "burned": False}

def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_role(guild: discord.Guild) -> discord.Role | None:
    return guild.get_role(ROLE_ID)

def has_command_role(ctx: commands.Context) -> bool:
    return any(role.id == COMMAND_ROLE_ID for role in ctx.author.roles)

async def mute_member(member: discord.Member):
    try:
        await member.edit(mute=True, reason="!burn — server mute")
    except discord.Forbidden:
        print(f"❌ Could not mute {member}")

async def unmute_member(member: discord.Member):
    try:
        await member.edit(mute=False, reason="!unburn — remove mute")
    except discord.Forbidden:
        print(f"❌ Could not unmute {member}")

async def set_channel_overwrite(channel, role, overwrite):
    try:
        await channel.set_permissions(role, overwrite=overwrite, reason="!burn")
    except discord.Forbidden:
        pass

async def clear_channel_overwrite(channel, role):
    try:
        overwrite = channel.overwrites_for(role)
        if not overwrite.is_empty():
            await channel.set_permissions(role, overwrite=None, reason="!unburn")
    except discord.Forbidden:
        pass

async def _give_role(member: discord.Member):
    """Assign the auto-role to a member."""
    role = get_role(member.guild)
    if not role:
        return
    if role in member.roles:
        return  # already has it
    try:
        await member.add_roles(role, reason="Auto-role on join")
        print(f"🎭  Gave role '{role.name}' to {member}.")
    except discord.Forbidden:
        print(f"❌  Missing permissions to assign role to {member}.")

# ── Events ────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    guild = bot.get_guild(GUILD_ID)
    print(f"✅  Logged in as {bot.user} | Guild: {guild.name if guild else 'NOT FOUND'}")

@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id != GUILD_ID:
        return
    # If server has membership screening, member is pending — skip for now.
    # on_member_update will catch them once they accept the rules.
    if member.pending:
        return
    await _give_role(member)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    """Fires when a member accepts membership screening (pending → not pending)."""
    if after.guild.id != GUILD_ID:
        return
    if before.pending and not after.pending:
        await _give_role(after)

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """Auto-mute any role member who joins a VC while burn is active."""
    data = load_data()
    if not data.get("burned"):
        return
    role = get_role(member.guild)
    if not role or role not in member.roles:
        return
    if after.channel is not None and not after.mute:
        await mute_member(member)
        print(f"🔇 Auto-muted {member} on VC join (burn active)")

# ── Commands ──────────────────────────────────────────────────────────────────

@bot.command(name="burn")
async def burn(ctx: commands.Context):
    if not has_command_role(ctx):
        return

    role = get_role(ctx.guild)
    if not role:
        await ctx.send("❌ Role not found. Check your `ROLE_ID` in `.env`.")
        return

    data = load_data()
    if data.get("burned"):
        await ctx.send("⚠️ Already burned. Use `!unburn` first.")
        return

    data["burned"] = True
    save_data(data)

    deny_chat = discord.PermissionOverwrite(
        send_messages            = False,
        send_messages_in_threads = False,
        add_reactions            = False,
        speak                    = False,
    )

    members_to_mute = [
        member
        for vc in ctx.guild.voice_channels
        for member in vc.members
        if role in member.roles
    ]

    await asyncio.gather(
        *[mute_member(m) for m in members_to_mute],
        *[set_channel_overwrite(ch, role, deny_chat) for ch in ctx.guild.channels],
    )

    msg = f"🔥 **Burned.** Chat permissions removed for **{role.name}**. Server is still visible."
    if members_to_mute:
        msg += f" Server muted **{len(members_to_mute)}** member(s) in voice."
    msg += " Anyone who joins VC will be auto-muted too."
    await ctx.send(msg)


@bot.command(name="unburn")
async def unburn(ctx: commands.Context):
    if not has_command_role(ctx):
        return

    role = get_role(ctx.guild)
    if not role:
        await ctx.send("❌ Role not found. Check your `ROLE_ID` in `.env`.")
        return

    data = load_data()
    if not data.get("burned"):
        await ctx.send("⚠️ Role is not burned right now.")
        return

    data["burned"] = False
    save_data(data)

    members_to_unmute = [
        member
        for vc in ctx.guild.voice_channels
        for member in vc.members
        if role in member.roles and member.voice and member.voice.mute
    ]

    await asyncio.gather(
        *[unmute_member(m) for m in members_to_unmute],
        *[clear_channel_overwrite(ch, role) for ch in ctx.guild.channels],
    )

    msg = f"✅ **Unburned.** All permissions restored for **{role.name}**."
    if members_to_unmute:
        msg += f" Server unmuted **{len(members_to_unmute)}** member(s)."
    await ctx.send(msg)


@bot.command(name="kill")
async def kill(ctx: commands.Context):
    if not has_command_role(ctx):
        return

    role = get_role(ctx.guild)
    if not role:
        await ctx.send("❌ Role not found. Check your `ROLE_ID` in `.env`.")
        return

    victims = [m.id for m in role.members]
    if not victims:
        await ctx.send("⚠️ No members currently have that role.")
        return

    async def remove_role(member):
        try:
            await member.remove_roles(role, reason="!kill command")
        except discord.Forbidden:
            pass

    await asyncio.gather(*[remove_role(m) for m in list(role.members)])

    data = load_data()
    data["killed_members"] = victims
    save_data(data)

    await ctx.send(f"💀 **Killed.** Removed **{role.name}** from **{len(victims)}** member(s).")


@bot.command(name="revive")
async def revive(ctx: commands.Context):
    if not has_command_role(ctx):
        return

    role = get_role(ctx.guild)
    if not role:
        await ctx.send("❌ Role not found. Check your `ROLE_ID` in `.env`.")
        return

    data = load_data()
    killed_ids: list[int] = data.get("killed_members", [])
    if not killed_ids:
        await ctx.send("⚠️ No kill record found. Run `!kill` first.")
        return

    members = [ctx.guild.get_member(mid) for mid in killed_ids]
    members = [m for m in members if m is not None]
    not_found = len(killed_ids) - len(members)

    async def add_role(member):
        try:
            await member.add_roles(role, reason="!revive command")
        except discord.Forbidden:
            pass

    await asyncio.gather(*[add_role(m) for m in members])

    data["killed_members"] = []
    save_data(data)

    msg = f"✨ **Revived.** Gave **{role.name}** back to **{len(members)}** member(s)."
    if not_found:
        msg += f" ({not_found} member(s) left the server.)"
    await ctx.send(msg)


# ── Run ───────────────────────────────────────────────────────────────────────
bot.run(TOKEN)