#!/usr/bin/env python
from time import strftime, gmtime

import discord
from discord.ext import commands

import functions


class BotWrapper(commands.Bot):
    async def on_message(self, msg):
        if msg.author.id == 125649678850064384:
            return
        await self.process_commands(msg)

################################################################################

bot = BotWrapper(command_prefix="eli ", description="your mom lol")

@bot.event
async def on_ready():
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    print("\033[92mREADY\033[0m")
    print("Startup latency: {}ms\n".format(int(bot.latency * 1000)))


@bot.command()
async def price(ctx, *args):
    """
    eli price <item ID> <enchant level>
    """
    await ctx.send(await functions.price(*args))


@bot.command()
async def enchant(ctx, *args):
    """
    eli enchant <typ> <tier> <enchant level> <cena> <nová cena>
    """
    await ctx.send(await functions.enchant(*args))


with open("TOKEN") as f:
    bot.run(f.read().strip())
