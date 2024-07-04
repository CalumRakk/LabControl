import re

FOLDER_SERVER = "/home/leo/Descargas/Minecraft/serverdoble"
PEM_PATH = "/home/leo/Descargas/AWS_EC2/windows.pem"
SSH_COMMAND = f'ssh -i "{PEM_PATH}" ubuntu@ec2-3-95-13-7.compute-1.amazonaws.com'


SESSION_NAME = "server_minecraft"
regex_player_count = re.compile(
    r"\[minecraft\/MinecraftServer\]:\sThere\sare\s(\d)\sof\sa\smax\sof\s10\splayers\sonline"
)
