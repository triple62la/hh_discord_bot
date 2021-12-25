import discord
from discord.ext import commands
from config import  help_msg, BOT_USER_ID
from bot_token import TOKEN
from models import Giphy
from models import UserLevelsDb

bot = commands.Bot(command_prefix='.', help_command=None, self_bot=False)
level_system = UserLevelsDb('database.db', 'levels')


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    msg = f'connected to the channel {after.channel}' if not before.channel else f'left channel {before.channel}'
    for channel in member.guild.channels:
        if isinstance(channel, discord.TextChannel):
            await channel.send(f'{member.name}  {msg}')

@bot.event
async def on_message(message: discord.Message):
    if str(message.channel.type) == 'text' and message.author.id != BOT_USER_ID:

        info = await level_system.get_user_info(message.author.id)
        if info is None:
            await level_system.create_user(message.author.id)
        else:
            msg_count, user_level = info
            need_lvlup = msg_count % 20 == 0
            user_level += 1 if need_lvlup else 0
            msg_count += 1
            await level_system.update_params(message.author.id,
                                             total_messages=msg_count,
                                             user_level=user_level)
            if need_lvlup:
                await message.channel.send(f"{message.author.name} just reached {user_level} level!")
    await bot.process_commands(message)


@bot.command(aliases=['some_test'])
async def test(ctx: commands.context.Context, *, argument):
    await ctx.send(f'It was just a test, {argument}')


@bot.command()
async def giphy(ctx: commands.context.Context, *, argument):
    gif_url_list = await Giphy.search(argument)

    await ctx.send(*gif_url_list)


@bot.command()
async def help(ctx):
    await ctx.send(help_msg)


@bot.command()
async def kick(ctx, member: discord.Member):
    await member.kick(reason=f'You was kicked by {ctx.author}')


@bot.command()
async def ban(ctx, member: discord.Member):
    await member.send(f'You was banned from {ctx.guild.name} for being a jerk')
    await member.ban(reason=f'You was banned for being a jerk')
    await ctx.send(f'User {member.display_name} was banned')


@bot.command()
async def unban(ctx, *, user_name):
    ban_entries = await ctx.guild.bans()
    for ban_entry in ban_entries:
        if ban_entry.user.name == user_name:
            user = ban_entry.user
            await ctx.guild.unban(user)
            await ctx.send(f'User {user_name} was unbanned')

@bot.command()
async def level(ctx:commands.context.Context):
    msg_count,level=await level_system.get_user_info(ctx.author.id)
    await ctx.send(f'{ctx.author.name} level is {level}, {msg_count} messages was sent')



if __name__ == '__main__':
    bot.run(TOKEN)
