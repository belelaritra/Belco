import os
import re
import discord
import json
import nacl
import requests
import validators
import wikipedia
import wolframalpha
import youtube_dl

from discord.ext import commands
from pytz import timezone
from datetime import datetime
from youtube_search import YoutubeSearch
from bs4 import BeautifulSoup
from selenium import webdriver

# Wolfram Alpha
waclient = wolframalpha.Client('___WA KEY___')

# CLIENT
client = commands.Bot(command_prefix="!")

#Oxygen Dist
oxy_dict = {'Alipurduar': 719,
            'Bankura': 720,
            'Birbhum': 721,
            'Cooch': 722,
            'Dakshindinajpur': 723,
            'Darjeeling': 724,
            'Hoogly': 725,
            'Howrah': 726,
            'Jalpaiguri': 727,
            'Jhargram': 728,
            'Kalimpong': 729,
            'Kolkata': 730,
            'Malda': 731,
            'Murshidabad': 732,
            'Nadia': 733,
            'North24parganas': 734,
            'Paschimbardhaman': 735,
            'Paschimmedinipur': 736,
            'Purbabardhaman': 737,
            'Purbamedinipur': 738,
            'Purulia': 739,
            'South24parganas': 740,
            'Uttardinajpur': 741,
            }

#Date:
d1 = datetime.now(timezone("Asia/Kolkata")).strftime("%d-%m-%Y")

# EVENT
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# Command
@client.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send('You are not in a voice channel.')
    channel = ctx.message.author.voice.channel
    voice = ctx.voice_client
    if voice and voice.is_connected():
        song_there = os.path.isfile("song.mp3")
        if song_there:
            os.remove("song.mp3")
        await voice.move_to(channel)
        await ctx.send(f'Moved to {channel}')
    else:
        voice = await channel.connect()
        song_there = os.path.isfile("song.mp3")
        if song_there:
            os.remove("song.mp3")
        await ctx.send(f'Connected to {channel}')


# Play
@client.command()
async def play(ctx, *, search: str):
    valid = validators.url(search)
    print(valid)
    # If Valid URL
    if valid == True:
        print("Url is valid")
        url = search
        # Json
        yt = YoutubeSearch(url, max_results=1).to_json()
        yt_id = str(json.loads(yt)['videos'][0]['id'])
    # If Song Name (Invalid URL)
    else:
        newsearch = search.replace(" ", "")
        print("Invalid url")
        # Json
        yt = YoutubeSearch(newsearch, max_results=1).to_json()
        yt_id = str(json.loads(yt)['videos'][0]['id'])
        # Creating URL
        url = 'https://www.youtube.com/watch?v=' + yt_id

    # Getting Details From JSON
    title = json.loads(yt)['videos'][0]['title']
    duration = json.loads(yt)['videos'][0]['duration']
    channel = json.loads(yt)['videos'][0]['channel']

    # Embed Details
    embedVar = discord.Embed(title=title, description=url, color=0x00ff00)
    embedVar.set_thumbnail(url=json.loads(yt)['videos'][0]['thumbnails'][0])
    embedVar.add_field(name="Channel", value=" ".join(re.findall('[A-Z][a-z]*', channel)), inline=False)
    embedVar.add_field(name="Song Duration", value=duration, inline=False)
    await ctx.channel.send(embed=embedVar)
    # Quality
    ydl_opts = {'format': 'beataudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}

    # If Already Playing
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    ytdl = youtube_dl.YoutubeDL(ydl_opts)
    info = ytdl.extract_info(url, download=False)
    asrc = discord.FFmpegOpusAudio(info['formats'][0]['url'],
                                   before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
    voice.play(asrc)


# Leave
@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if ctx.author.voice.channel and ctx.author.voice.channel == ctx.voice_client.channel:
        await ctx.voice_client.disconnect()
        channel = ctx.message.author.voice.channel
        await ctx.send(f'Disconnected to {channel}')
    else:
        await ctx.send('You have to be connected to the same voice channel to disconnect me.')

#Pause
@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")

#Resume
@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")

#Stop
@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

#!Command
@client.command()
async def command(ctx):
    embedVar = discord.Embed(title="!quote", description="To Get Random Quotes", color=0x00ff00)
    embedVar.add_field(name="!join", value="To add in any Voice Channel", inline=False)
    embedVar.add_field(name="!play _<url or song name>_", value="To Play a Song", inline=False)
    embedVar.add_field(name="!pause", value="To pause a Song", inline=False)
    embedVar.add_field(name="!resume", value="To resume a paused Song", inline=False)
    embedVar.add_field(name="!stop", value="To Stop a Song", inline=False)
    embedVar.add_field(name="!leave", value="To Leave the Voice Channel", inline=False)
    embedVar.add_field(name="!math _<question>_", value="To Solve Any Mathematics Problems", inline=False)
    embedVar.add_field(name="!spam *<message>* *<no_of_times>*",
                       value="To Spam a Message for Infinity Times ( Currently Restricted upto 10 Times )",
                       inline=False)
    embedVar.add_field(name="!decimal _<number>_", value="To Convert Binary Numbers into Decimal", inline=False)
    embedVar.add_field(name="!binary _<number>_", value="To Convert Decimal Numbers into Binary", inline=False)
    embedVar.add_field(name="!wikipedia _<query>_",
                       value="To Get Wikipedia Details of Searched Item (First 3 Lines Only)", inline=False)
    embedVar.add_field(name="!weather _<city>_", value="To Get Live Weather Report of That City", inline=False)
    embedVar.add_field(name="!covid _<city>_", value="To Get Live Statistics of That City", inline=False)
    embedVar.add_field(name="!vaccine _<pincode>_", value="To Check the Vaccine Avaibility in Your Area", inline=False)
    await ctx.channel.send(embed=embedVar)


# HI REPLY
@client.command(name='hi', help='Replies Namaste')
async def hi(ctx):
    await ctx.channel.send('Namaste !! ' + ctx.author.name)

#Clear
@client.command()
async def clear(ctx, amount : str):
    await ctx.channel.purge(limit=int(amount))


# RANDOM QUOTE
@client.command(name='!quote :', help='To Get Random Quotes')
async def quote(ctx):
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    await ctx.channel.send(quote)


#Vaccine
@client.command()
async def vaccine(ctx, query: str):
    print(d1)
    response = requests.get(
        "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=" + query + "&date=" + str(
            d1))
    resp_json = response.json()
    try:
        if resp_json["centers"]:
            for center in resp_json["centers"]:
                for session in center["sessions"]:
                    embedVar = discord.Embed(title=center["name"], description=session["date"],
                                             color=discord.Colour.random())
                    embedVar.add_field(name="Vaccine :", value=session["vaccine"], inline=True)
                    embedVar.add_field(name="Price :", value=center["fee_type"], inline=True)
                    embedVar.add_field(name="Age :", value=str(session["min_age_limit"]) + "+", inline=True)
                    embedVar.add_field(name="Dose 1 :", value=session["available_capacity_dose1"], inline=True)
                    embedVar.add_field(name="Dose 2 :", value=session["available_capacity_dose2"], inline=True)
                    embedVar.add_field(name="Total Availability :", value=session["available_capacity"], inline=True)
                    await ctx.channel.send(embed=embedVar)

        else:
            await ctx.channel.send("No Vaccine Available")
    except:
        await ctx.channel.send("Invalid Pincode")

# BINARY TO DECIMAL
@client.command()
async def decimal(ctx, query: str):
    response = requests.get("https://networkcalc.com/api/binary/" + query)
    json_data = json.loads(response.text)
    result = json_data['converted']
    await ctx.channel.send(result)


# DECIMAL TO BINARY
@client.command()
async def binary(ctx, query: str):
    num = int(query)
    result = int(bin(num)[2:])
    await ctx.channel.send(result)


# SPAM
@client.command()
async def spam(ctx, query: str):
    new = query.split()
    num = int(new[1])
    if num < 11:
        for x in range(num):
            await ctx.channel.send(new[0])

    else:
        await ctx.channel.send('Sorry currently it is restricted upto 10 times')


# MATH
@client.command()
async def math(ctx, query: str):
    res = waclient.query(query)
    answer = next(res.results).text
    await ctx.channel.send(answer)


# WIKIPEDIA
@client.command()
async def wiki(ctx, query: str):
    search = wikipedia.search(query, results=1)
    try:
        result = wikipedia.summary(query, sentences=3)
        embedVar = discord.Embed(title=search[0], description=result.replace(". ", ".\n", 3),
                                 color=discord.Colour.random())
        await ctx.channel.send(embed=embedVar)

    except:
        await ctx.channel.send('Unable to Find it out\nPlease be more Specific.\nLike: < ' + str(query) + ' .... >')


# COVID
@client.command()
async def covid(ctx, city: str):
    query = city.capitalize()
    response = requests.get("https://api.covid19india.org/v4/min/data.min.json")
    json_data = json.loads(response.text)
    try:
        confirmed = json_data['WB']['districts'][query]['delta']['confirmed']
        deceased = json_data['WB']['districts'][query]['delta']['deceased']
        recovered = json_data['WB']['districts'][query]['delta']['recovered']
        totconfirmed = json_data['WB']['districts'][query]['total']['confirmed']
        totdeceased = json_data['WB']['districts'][query]['total']['deceased']
        totrecovered = json_data['WB']['districts'][query]['total']['recovered']
        vaccinated1 = json_data['WB']['districts'][query]['total']['vaccinated1']
        vaccinated2 = json_data['WB']['districts'][query]['total']['vaccinated2']
        population = json_data['WB']['districts'][query]['meta']['population']

        embedVar = discord.Embed(title=query, description=d1, color=discord.Colour.random())
        embedVar.add_field(name="Confirmed :", value=confirmed, inline=True)
        embedVar.add_field(name="Recovered :", value=recovered, inline=True)
        embedVar.add_field(name="Deceased :", value=deceased, inline=True)

        embedVar.add_field(name="Total Confirmed :", value=totconfirmed, inline=True)
        embedVar.add_field(name="Total Recovered :", value=totrecovered, inline=True)

        embedVar.add_field(name="Total Deceased :", value=totdeceased, inline=True)
        embedVar.add_field(name="Population :", value=population, inline=True)
        embedVar.add_field(name="Vaccinated Dose 1:", value=vaccinated1, inline=True)
        embedVar.add_field(name="Vaccinated Dose 2:", value=vaccinated2, inline=True)
        await ctx.channel.send(embed=embedVar)
    except:
        try:
            totconfirmed = json_data['WB']['districts'][query]['total']['confirmed']
            totrecovered = json_data['WB']['districts'][query]['total']['recovered']
            totdeceased = json_data['WB']['districts'][query]['total']['deceased']
            totrecovered = json_data['WB']['districts'][query]['total']['recovered']
            population = json_data['WB']['districts'][query]['meta']['population']
            vaccinated1 = json_data['WB']['districts'][query]['total']['vaccinated1']
            vaccinated2 = json_data['WB']['districts'][query]['total']['vaccinated2']
            await ctx.channel.send('Daily Data is not Updated Yet. Here is the Total Data')
            embedVar.add_field(name="Total Confirmed :", value=totconfirmed, inline=True)
            embedVar.add_field(name="Total Recovered :", value=totrecovered, inline=True)

            embedVar.add_field(name="Total Deceased :", value=totdeceased, inline=True)
            embedVar.add_field(name="Population :", value=population, inline=True)
            embedVar.add_field(name="Vaccinated Dose 1:", value=vaccinated1, inline=True)
            embedVar.add_field(name="Vaccinated Dose 2:", value=vaccinated2, inline=True)

            await ctx.channel.send(embed=embedVar)
        except:
            await ctx.channel.send('Enter a Valid City Name\nor Try within West Bengal')

# WEATHER
@client.command()
async def weather(ctx, query: str):
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather?" + "q=" + query + "&appid=" + '___kEY___')
    json_data = json.loads(response.text)
    print(json_data)
    temp = round(json_data['main']['temp'] - 273, 2)
    feels_like = round(json_data['main']['feels_like'] - 273, 2)
    temp_min = round(json_data['main']['temp_min'] - 273, 2)
    temp_max = round(json_data['main']['temp_max'] - 273, 2)
    speed = json_data['wind']['speed']
    pressure = json_data['main']['pressure']
    embedVar = discord.Embed(title=query.capitalize(), description=d1, color=discord.Colour.random())
    embedVar.add_field(name="Temperature :", value=str(temp) + " °C", inline=True)
    embedVar.add_field(name="Max :", value=str(temp_max) + " °C", inline=True)
    embedVar.add_field(name="Min :", value=str(temp_min) + " °C", inline=True)
    embedVar.add_field(name="Feels Like :", value=str(feels_like) + " °C", inline=True)
    embedVar.add_field(name="Wind Speed :", value=str(speed) + " m/s", inline=True)
    embedVar.add_field(name='Pressure', value=str(pressure) + " hPa", inline=True)
    await ctx.channel.send(embed=embedVar)


@client.command()
async def oxygen(ctx, stringstart: str):
    query = stringstart.replace(" ", "")
    word = query.capitalize()
    if word in oxy_dict:
        key = oxy_dict[word]
        page = requests.get("https://covidsupport.live/result/?state=37&district=" + str(
            key) + "&pincode=711101&requireditem=oxygen&bloodgroup=%20&medicine=%20")
        soup = BeautifulSoup(page.content, 'html.parser')
        x = 0
        for div in soup.find_all('div', class_='col-10'):
            x = x + 1
            if (x < 4):
                embedVar = discord.Embed(title="OXYGEN", description=div.text, color=discord.Colour.random())
                await ctx.channel.send(embed=embedVar)
            else:
                break

#Screen Shot
@client.command()
async def ss(ctx, *, query :str):
  browser = webdriver.Chrome(r"C:\Users\Aritra Belel\PycharmProjects\NPTEL\chromedriver.exe")
  query = query.replace(' ', '+')
  browser.get("https://www.google.com/search?q=" + str(query))
  result = browser.find_element_by_tag_name('h3')
  result.click()
  browser.save_screenshot("screenshot.png")
  await ctx.channel.send(file=discord.File('screenshot.png'))
  os.remove("screenshot.png")


client.run('___BOT KEY___')
