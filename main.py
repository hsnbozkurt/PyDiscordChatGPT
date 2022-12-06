#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Builtins
import json
import os
import time
import discord
# Local
from classes import auth as Auth
from classes import chat as Chat
from classes import spinner as Spinner

# Fancy stuff
import colorama
from colorama import Fore
channels = [1049708825311195207]
class DiscordChat:
    def __init__(self,thread:discord.Thread,user:discord.User,convo_id:str,auth:str):
        self.thread = thread
        self.user = user
        self.convo_id = convo_id
        self.ended = False
        self.auth = auth
        self.previous_convo = None
    def send(self,msg):
        a =self.thread.send(msg)
    def end(self):
        self.ended = True
    def __del__(self):
        self.end()
    async def ask(self,msg):
        answer, previous_convo, convo_id = await Chat.ask(self.auth,msg,self.convo_id,self.previous_convo)
        if convo_id is not None:
            self.convo_id = convo_id
        if previous_convo is not None:
            self.previous_convo = previous_convo
        return answer
colorama.init(autoreset=True)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
chats = []
# Check if config.json exists
if not os.path.exists("config.json"):
    print(">> config.json is missing. Please create it.")
    print(f"{Fore.RED}>> Exiting...")
    exit(1)

# Read config.json
with open("config.json", "r") as f:
    config = json.load(f)
    # Check if email & password are in config.json
    if "email" not in config or "password" not in config:
        print(">> config.json is missing email or password. Please add them.")
        print(f"{Fore.RED}>> Exiting...")
        exit(1)

    # Get email & password
    email = config["email"]
    password = config["password"]
def get_chat(user_id:str):
    for chat in chats:
        if chat.user.id == user_id:
            return chat
    return None
def start_discord(token:str):
    @client.event
    async def on_ready():
        print(f"{Fore.GREEN}>> Logged in as {client.user}")
        print(f"{Fore.GREEN}>> Starting chat...")
        chats = []
        # Set bot status to watching you
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you"))
        
    @client.event
    async def on_message(message:discord.Message):
        if message.author == client.user or message.author.bot or message.guild is None:
            return
        elif message.content.startswith('!create'):
            if channels.count(message.channel.id) < 0:
                await message.channel.send("You can't use this command here!")
                return
            print(f"{Fore.GREEN}>> Creating chat...")
            thread = await message.create_thread(name=f"{message.author.name}'s chat")
            print(f"{Fore.GREEN}>> Chat created.")
            chats.append(DiscordChat(thread,message.author,None,token))
            await thread.send(f"Hello {message.author.name}! Welcome to your chat!")
            print(f"{Fore.GREEN}>> Chat started.")
        elif message.content.startswith('!close'):
            for chat in chats:
                if chat.thread == message.channel and chat.user == message.author:
                    await chat.thread.send("Chat closed!")
                    chats.remove(chat)
                    return
            await message.channel.send("You don't have a chat open!")
        elif message.content.startswith('!help'):
            await message.channel.send("Commands: !create, !close, !help")
        elif message.content.startswith('!add-channel'):
            if message.author.id != 940260832867147897:
                await message.channel.send("You can't use this command!")
                return
            channels.append(message.channel.id)
            await message.channel.send("Channel added!")
        elif get_chat(message.author.id) is not None:
            chat = get_chat(message.author.id)
            if chat.thread.id != message.channel.id or chat.user.id != message.author.id:
                return
            answer = await chat.ask(message.content)
            # check string length
            if len(answer) > 2000:
                # split into multiple messages
                for i in range(0, len(answer), 2000):
                    await chat.thread.send(answer[i:i+2000])
            else:
                await chat.thread.send(answer)
    client.run(config["token"])
            
def start_chat():
    expired_creds = Auth.expired_creds()
    print(f"{Fore.GREEN}>> Checking if credentials are expired...")
    if expired_creds:
        print(f"{Fore.RED}>> Your credentials are expired." + f" {Fore.GREEN}Attempting to refresh them...")
        open_ai_auth = Auth.OpenAIAuth(email_address=email, password=password)

        print(f"{Fore.GREEN}>> Credentials have been refreshed.")
        open_ai_auth.begin()
        time.sleep(3)
        is_still_expired = Auth.expired_creds()
        if is_still_expired:
            print(f"{Fore.RED}>> Failed to refresh credentials. Please try again.")
            exit(1)
        else:
            print(f"{Fore.GREEN}>> Successfully refreshed credentials.")
    else:
        print(f"{Fore.GREEN}>> Your credentials are valid.")

    print(f"{Fore.GREEN}>> Starting chat..." + Fore.RESET)
    access_token = Auth.get_access_token()
    start_discord(access_token)

if __name__ == "__main__":
    start_chat()
