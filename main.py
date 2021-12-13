import discord
from discord.ext import commands
from config.token import token
from config.playlist import playlis
import youtube_dl
import os
import time
from asyncio import run_coroutine_threadsafe as rct

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Bot connected...\n')

@bot.event
async def on_message(message):
    if message.channel.name == 'канал-геев':
        await bot.process_commands(message)
        time.sleep(5)
        await message.channel.purge(limit=1)
    else:
        return

server, server_id, name_channel, replay, src = None, None, None, None, 0

domains = ['http://www.youtube.com/','https://www.youtube.com/','http://youtu.be/','https://youtu.be/']
async def check_domains(link):
    for x in domains:
        if link.startswith(x):
            return True
    return False

@bot.command()
async def play(ctx, *,command = None):
    global server, server_id, name_channel
    author = ctx.author
    poslushat = author.voice.channel.name
    botik = ctx.channel.name

    if poslushat == 'концерт пошле моле' and botik == 'канал-геев':
        if command is None:
            server = ctx.guild
            name_channel = author.voice.name
            voice_channel = discord.utils.get(server.voice_channels, name=name_channel)

        params = command.split(' ')
        if len(params) == 1:
            source = params[0]
            server = ctx.guild
            name_channel = author.voice.channel.name
            voice_channel = discord.utils.get(server.voice_channels, name=name_channel)
            print('Param 1')
        elif len(params) == 3:
            server_id = params[0]
            voice_id = params[1]
            source = params[2]
            try:
                server_id = int(server_id)
                voice_id = int(voice_id)
            except:
                await ctx.channel.send(f'{author.mention}, id сервера и voice должны быть записаны в цифрах!')
                return
            print('Param 3')
            server = bot.get_guild(server_id)
            voice_channel = discord.utils.get(server.voice_channels, id=voice_id)
        else:
            await ctx.channel.send(f'{author.mention}, команда не корректна!')
            return

        voice = discord.utils.get(bot.voice_clients, guild = server)
        if voice is None:
            await voice_channel.connect()
            voice = discord.utils.get(bot.voice_clients, guild = server)

        if source is None:
            pass
        elif source.startswith('http'):
            if not check_domains(source):
                await ctx.channel.send(f'{author.mention}, неверная ссылка!')
                return

            song_there = os.path.isfile('music/song.mp3')
            try:
                if song_there:
                    os.remove('music/song.mp3')
            except PermissionError:
                await ctx.channel.send('Недостаточно прав на удаление!')
                return
            await ctx.channel.send(f'{ctx.author.mention}, идет закачка музыки, подожди...')
            ydl_opts = {
                'outtmpl': 'music/song.mp3',
                'format':'bestaudio/best',
                'postprocessors':[
                    {
                        'key':'FFmpegExtractAudio',
                        'preferredcodec':'mp3',
                        'preferredquality':'192',
                    }
                ],
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print('1')
                ydl.download([source])
                print('2 '+source)
            # for file in os.listdir('music/'):
            #     print('3')
            #     if file.endswith('.mp3'):
            #         print('4 '+file)
            #         os.rename()
            #         print('5')
            print('voice')
            print(voice)
            voice.play(discord.FFmpegPCMAudio('music/song.mp3'))
            print(voice)
        else:
            voice.play(discord.FFmpegPCMAudio(f'music/{source}'))
    else:
        return

@bot.command()
async def leave(ctx):
    global server, name_channel
    voice = discord.utils.get(bot.voice_clients, guild = server)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, бот не был подключен!')

@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = server)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, бот не играет!')

@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = server)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, бот не приостановлен!')

@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild = server)
    if voice.is_connected():
        voice.stop()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, бот не подключен!')

@bot.command()
async def plist(ctx):
    await ctx.channel.send(playlis)

@bot.command()
async def playlist(ctx, *,command = None):
    global server, server_id, name_channel, replay
    author = ctx.author
    poslushat = author.voice.channel.name
    botik = ctx.channel.name

    if poslushat == 'концерт пошле моле' and botik == 'канал-геев':
        if command is None:
            server = ctx.guild
            name_channel = author.voice.name

        params = command.split(' ')
        if len(params) == 1:
            src = params[0]
            server = ctx.guild
            name_channel = author.voice.channel.name
            voice_channel = discord.utils.get(server.voice_channels, name=name_channel)
            print('Param 1')
        else:
            await ctx.channel.send(f'{author.mention}, команда не корректна!')
            return

        voice = discord.utils.get(bot.voice_clients, guild = server)
        if voice is None:
            await voice_channel.connect()
            voice = discord.utils.get(bot.voice_clients, guild = server)

        if src is None:
            pass
        else:
            ydl_opts = {
                'format':'bestaudio/best',
                'postprocessors':[
                    {
                        'key':'FFmpegExtractAudio',
                        'preferredcodec':'mp3',
                        'preferredquality':'192',
                    }
                ],
            }
            replay = 1
            youtube_dl.YoutubeDL(ydl_opts)
            voice.play(discord.FFmpegPCMAudio(f'playlist/{src}.mp3'))
    else:
        return

while True:
    voice = discord.utils.get(bot.voice_clients, guild=server)
    if replay == 1:
        if not voice.is_playing():
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }
                ],
            }
            youtube_dl.YoutubeDL(ydl_opts)
            voice.play(discord.FFmpegPCMAudio(f'playlist/{src+1}.mp3'))
        else:
            pass
    else:
        pass

bot.run(token)
