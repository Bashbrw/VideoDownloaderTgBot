from yt_dlp import YoutubeDL
from time import sleep
from unidecode import unidecode
from pyrogram import Client, filters
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import re
import json
import requests
import os


admin = 0 # put your telegram id here
version = '1.72.0622'
last_mod = '24/06/2022'

global videosdownloaded
global defchannel
global defgroup

defchannel = 't.me/<yourchannelusername>' # default channel, remove @
defgroup = 't.me/<yourgroupusername>' # default group, remove @
videosdownloaded = 0


clog_text = f''


# time users have to wait between downloads, in seconds
global time
time = 0

if time > 60:
    time_text = f'Você deve esperar por {round(time/60)} minuto(s) entre pedidos.'
else:
    time_text = f'Você deve esperar por {time} segundos entre pedidos.'

wmsgtxt = 'O tempo de espera terminou, você pode requisitar novamente.'


# banned users list
banned_users = []
with open('banned_users.txt', 'r') as f:
    banned_users = [int(line.replace('\\n', '')) for line in f]
    #banned_users.append(int(line.replace('\\n', '')))


# quality == height of the video
users = { admin: {'type': 'video', 'quality': 1080, 'format': 'best', 'premium': True, 'caption': 'sim', 'wmsg': 'sim' }}
groups = {}

user_time = {}


# default settings for new users
default_conf = {'type': 'video', 'quality': 1080, 'format': 'best', 'premium': False, 'caption': 'sim', 'wmsg': 'sim'}


# setup environment variables
app = Client('YTDownloaderBot',
             api_id=os.environ.get('ID'),
             api_hash=os.environ.get('HASH'),
             bot_token=os.environ.get('TOKEN'))


# only match with youtube links
regex = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

# read user database and assign default configs
with open('users.txt', 'r') as f:
    for usr in f:
        users[int(usr.replace('\\n', ''))] = default_conf
    print(f'User database lenght: {len(users)}')

# read time database
with open('time.txt', 'r') as f:
    time = int(f.read())

def save_new_user(user_id):
    with open('users.txt', 'a+') as f:
        f.write(user_id)
        f.write('\n')

def save_configs(user_id):
    pass # TODO implement this function


# buttons callback query
@app.on_callback_query()
def callback(client, callback_query):
    message = callback_query.message
    messageId = message.id
    chatId = message.chat.id

    # settings section
    config_text = f'Suas configurações atuais:'

    text = f'<strong>Modo de uso:</strong> envie o link para o vídeo que deseja baixar e o bot automaticamente fará todo o processo e te enviará em modo <i>streaming</i>. Você também pode usar a ferramenta <i>inline</i> do @vid para uma melhor experiência.'

    # config buttons template
    config_btn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(f'Qualidade: {users[chatId]["quality"]}', callback_data='-cq'), InlineKeyboardButton(f'Tipo: {users[chatId]["type"]}', callback_data='-ct')],
            [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-ccap')],
            [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-wmsg')],
            [InlineKeyboardButton('Voltar', callback_data='start')],
        ])

    # start message buttons template
    join = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton('Canal', url=str(defchannel)), InlineKeyboardButton('Grupo', url=str((defgroup)))],
            [InlineKeyboardButton('Changelog(Inglês)', callback_data='-clog'), InlineKeyboardButton('Configurações', callback_data='-c')],
            [InlineKeyboardButton('Fechar', callback_data='f')]
        ])

    if '-c' == callback_query.data:
        app.edit_message_text(chatId, messageId, config_text, reply_markup=config_btn)
    
    # start message
    elif 'start' == callback_query.data:
        app.edit_message_text(chatId, messageId, text, reply_markup=join)
        del callback_query.data
    
    # -cq stands for "change quality"
    elif '-cq' == callback_query.data:
        # app.delete_messages(chatId, messageId)

        if users[chatId]['quality'] == 360:
            users[chatId]['quality'] = 480

        elif users[chatId]['quality'] == 480:
            users[chatId]['quality'] = 720

        elif users[chatId]['quality'] == 720:
            users[chatId]['quality'] = 1080

        elif users[chatId]['quality'] == 1080:
            users[chatId]['quality'] = 360


        app.edit_message_text(chatId, messageId, config_text, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(f'Qualidade: {users[chatId]["quality"]}', callback_data='-cq'), InlineKeyboardButton(f'Tipo: {users[chatId]["type"]}', callback_data='-ct')],
                [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-ccap')],
                [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-wmsg')],
                [InlineKeyboardButton('Voltar', callback_data='start')], ]))
        del callback_query.data

    
    elif '-ccap' in callback_query.data:
        if users[message.chat.id]['caption'] == 'sim':
            users[message.chat.id]['caption'] = 'não'
        
        else:
            users[message.chat.id]['caption'] = 'sim'
        
        app.edit_message_text(chatId, messageId, config_text, reply_markup=
        InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(f'Qualidade: {users[message.chat.id]["quality"]}', callback_data='-cq'), InlineKeyboardButton(f'Tipo: {users[message.chat.id]["type"]}', callback_data='-ct')],
                [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-ccap')],
                [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-wmsg')],
                [InlineKeyboardButton('Voltar', callback_data='start')], ]))
        
        del callback_query.data


    # -ct stands for 'change type'
    elif '-ct' == callback_query.data:
        if users[chatId]['type'] == 'video':
            users[chatId]['type'] = 'audio'

        elif users[chatId]['type'] == 'audio':
            users[chatId]['type'] = 'video'

        app.edit_message_text(chatId, messageId, config_text, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(f'Qualidade: {users[chatId]["quality"]}', callback_data='-cq'), InlineKeyboardButton(f'Tipo: {users[chatId]["type"]}', callback_data='-ct')],
                [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-ccap')],
                [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-wmsg')],
                [InlineKeyboardButton('Voltar', callback_data='start')], ]))
        del callback_query.data
    
    # changelog button callback
    elif '-clog' == callback_query.data:
        app.edit_message_text(chatId, messageId, clog_text, parse_mode=enums.parse_mode.ParseMode.HTML, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton('Voltar', callback_data='start')],
                [InlineKeyboardButton('Fechar', callback_data='f')], ]))

        del callback_query.data
    
    elif '-wmsg' in callback_query.data:
        if users[message.chat.id]['premium'] == True:
            app.edit_message_text(chatId, messageId, 'Você é um usuário premium.\nVocê não precisa esperar.')
            sleep(5)
            app.edit_message_text(chatId, messageId, config_text, reply_markup=
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(f'Qualidade: {users[chatId]["quality"]}', callback_data='-cq'), InlineKeyboardButton(f'Tipo: {users[chatId]["type"]}', callback_data='-ct')],
                    [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-ccap')],
                    [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-wmsg')],
                    [InlineKeyboardButton('Voltar', callback_data='start')], ]))
        
        elif users[message.chat.id]['premium'] == False:
            if users[message.chat.id]['wmsg'] == 'sim':
                users[message.chat.id]['wmsg'] = 'não'
            else:
                users[message.chat.id]['wmsg'] = 'sim'
        
        app.edit_message_text(chatId, messageId, config_text, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(f'Qualidade: {users[chatId]["quality"]}', callback_data='-cq'), InlineKeyboardButton(f'Tipo: {users[chatId]["type"]}', callback_data='-ct')],
                [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-ccap')],
                [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-wmsg')],
                [InlineKeyboardButton('Voltar', callback_data='start')], ]))
        del callback_query.data

    


    # settings to be used when user send /settings command
    # settcq stands for 'settings change quality'
    elif '-setcq' == callback_query.data:

        if users[chatId]['quality'] == 360:
            users[chatId]['quality'] = 480

        elif users[chatId]['quality'] == 480:
            users[chatId]['quality'] = 720

        elif users[chatId]['quality'] == 720:
            users[chatId]['quality'] = 1080

        elif users[chatId]['quality'] == 1080:
            users[chatId]['quality'] = 360

        app.edit_message_text(chatId, messageId, config_text, reply_markup=
        InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(f'Qualidade: {users[chatId]["quality"]}', callback_data='-setcq'), InlineKeyboardButton(f'Tipo: {users[chatId]["type"]}', callback_data='-setct')],
                [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-setcap')],
                [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-setwmsg')],
                [InlineKeyboardButton('Fechar', callback_data='f')], ]))
        
        del callback_query.data
    
    # -settct stands for 'settings change type'
    elif '-setct' == callback_query.data:
        if users[chatId]['type'] == 'video':
            users[chatId]['type'] = 'audio'

        elif users[chatId]['type'] == 'audio':
            users[chatId]['type'] = 'video'

        app.edit_message_text(chatId, messageId, config_text, reply_markup=
        InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(f'Qualidade: {users[chatId]["quality"]}', callback_data='-setcq'), InlineKeyboardButton(f'Tipo: {users[chatId]["type"]}', callback_data='-setct')],
            [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-setcap')],
            [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-setwmsg')],
            [InlineKeyboardButton('Fechar', callback_data='f')]]))
        
        del callback_query.data
    
    # -setcap stands for change caption
    elif '-setcap' in callback_query.data:
        if users[message.chat.id]['caption'] == 'sim':
            users[message.chat.id]['caption'] = 'não'
        
        else:
            users[message.chat.id]['caption'] = 'sim'
        
        app.edit_message_text(chatId, messageId, config_text, reply_markup=
        InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(f'Qualidade: {users[message.chat.id]["quality"]}', callback_data='-setcq'), InlineKeyboardButton(f'Tipo: {users[message.chat.id]["type"]}', callback_data='-setct')],
            [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-setcap')],
            [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-setwmsg')],
            [InlineKeyboardButton('Fechar', callback_data='f')]]))
    
        del callback_query.data
    
    elif '-setwmsg' in callback_query.data:
        if users[message.chat.id]['premium'] == True:
            app.edit_message_text(chatId, messageId, 'Você é um usuário premium.\nVocê não precisa esperar.')
            sleep(5)
            app.edit_message_text(chatId, messageId, config_text, reply_markup=
            InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(f'Qualidade: {users[message.chat.id]["quality"]}', callback_data='-setcq'), InlineKeyboardButton(f'Tipo: {users[message.chat.id]["type"]}', callback_data='-setct')],
                [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-setcap')],
                [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-setwmsg')],
                [InlineKeyboardButton('Fechar', callback_data='f')]]))

        elif users[message.chat.id]['premium'] == False:
            if users[message.chat.id]['wmsg'] == 'sim':
                users[message.chat.id]['wmsg'] = 'não'
        
            else:
                users[message.chat.id]['wmsg'] = 'sim'
        
        app.edit_message_text(chatId, messageId, config_text, reply_markup=
        InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(f'Qualidade: {users[message.chat.id]["quality"]}', callback_data='-setcq'), InlineKeyboardButton(f'Tipo: {users[message.chat.id]["type"]}', callback_data='-setct')],
            [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-setcap')],
            [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-setwmsg')],
            [InlineKeyboardButton('Fechar', callback_data='f')]]))

    # f stands for 'fechar'
    elif 'f' == callback_query.data:
        app.delete_messages(chatId, messageId)
        del callback_query.data




# start command
@app.on_message(filters.command('start'))
def start(client, message):
    if message.chat.id not in user_time:
        user_time[message.chat.id] = True


    elif message.chat.id not in users:
        save_new_user(message.chat.id)
        users[message.chat.id] = default_conf

    join = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton('Canal', url=defchannel), InlineKeyboardButton('Grupo', url=defgroup)],
            [InlineKeyboardButton('Changelog(Inglês)', callback_data='-clog'), InlineKeyboardButton('Configurações', callback_data='-c')],
            [InlineKeyboardButton('Fechar', callback_data='f')],
        ])

    # yes you can use HTML to format text
    text = f'Olá <b><a href="t.me/{message.from_user.username}">{message.from_user.first_name}</a></b>!\nSeja bem-vindo ao Video Downloader!\n\n<strong>Modo de uso:</strong> envie o link para o vídeo que deseja baixar e o bot automaticamente fará todo o processo e te enviará em modo <i>streaming</i>. Você também pode usar a ferramenta <i>inline</i> do @vid para uma melhor experiência.\n\nServiços suportados:\nYouTube'
    app.send_message(message.chat.id, text, reply_markup=join, disable_web_page_preview=True)




# settings command
@app.on_message(filters.command('settings'))
def settings(client, message):
    if message.chat.id not in user_time:
        user_time[message.chat.id] = True

    elif message.chat.id not in users:
        save_new_user(message.chat.id)
        users[message.chat.id] = default_conf

    btns = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(f'Qualidade: {users[message.chat.id]["quality"]}', callback_data='-setcq'), InlineKeyboardButton(f'Tipo: {users[message.chat.id]["type"]}', callback_data='-setct')],
                [InlineKeyboardButton(f'Título no vídeo: {users[message.chat.id]["caption"]}', callback_data='-setcap')],
                [InlineKeyboardButton(f'Aviso ao terminar tempo de espera: {users[message.chat.id]["wmsg"]}', callback_data='-setwmsg')],
                [InlineKeyboardButton('Fechar', callback_data='f')], ])

    config_text = 'Suas configurações atuais:'

    app.send_message(message.chat.id, config_text, reply_markup=btns)




# about command
@app.on_message(filters.command('about'))
def about(client, message):
    if message.chat.id not in user_time:
        user_time[message.chat.id] = True

    elif message.chat.id not in users:
        save_new_user(message.chat.id)
        users[message.chat.id] = default_conf

    active_users = len(users)
    abouttext = f'<strong>Video Downloader</strong>\n\nBaixe videos gratuitamente do YouTube 24/7.\n\nProgramado e adaptado por <a href="t.me/lolzaws">Bash</a>\nData de criação: 28/05/2022\nÚltimo update: {last_mod}\n\nVersão: {version}\n\nUsuários banidos: {len(banned_users)}\nVídeos baixados hoje: {videosdownloaded}\n\n<i>Sinta-se livre para fazer sugestões no <a href="t.me/skynetdevbots">grupo</a></i>'
    app.send_photo(message.chat.id, './assets/image.jpg', caption=abouttext)




# broadcast information command
@app.on_message(filters.private & filters.chat(admin) & filters.command('broadcast'))
def admin_broadcast(client, message):
    counter = 0
    broad_message = message.text.replace('/broadcast', '')

    for user in users.keys():
        app.send_message(user, broad_message)
        counter = counter + 1
        sleep(5)
        
    app.send_message(admin, f'Mensagem enviada para {counter} de {len(users)} usuários.')
    del counter



# set time between downloads for non-premiums
@app.on_message(filters.private & filters.command('settime') & filters.chat(admin))
def settime(client, message):
    # must be in seconds
    global time
    app.send_message(admin, f'O tempo era: {time}')
    t = int(message.text.replace('/settime', ''))
    with open('time.txt', 'w') as f:
        f.write(t)
    time = t
    app.send_message(admin, f'Agora é {time}')




# get user data
@app.on_message(filters.private & filters.command('getdata') & filters.chat(admin))
def getdata(client, message):
    usrnm = message.text.replace('/getdata', '').strip()
    i = app.get_users(usrnm)
    app.send_message(admin, i)




# manually add premium user
@app.on_message(filters.private & filters.command('addpremium') & filters.chat(admin))
def addpremium(client, message):
    usr = int(message.text.replace('/addpremium', ''))
    if usr not in users:
        users[usr] = default_conf
    
    users[usr]['premium'] = True
    app.send_message(admin, f'Usuário {usr} agora é premium!')




# manually remove premium from user
@app.on_message(filters.private & filters.command('rmpremium') & filters.chat(admin))
def rmpremium(clien, message):
    usr = int(message.text.replace('/rmpremium', ''))
    
    if usr in users:
        users[usr]['premium'] = False
        app.send_message(admin, f'Usuário <code>{usr}</code> não tem mais premium!')

    elif usr not in users:
        app.send_message(admin, 'Usuário não está na lista de usuários.')




# ban/block user
@app.on_message(filters.private & filters.chat(admin) & filters.command('bblock'))
def bblock(client, message):
    usr = message.text.replace('/bblock', '').strip()

    with open('banned_users.txt', 'a+') as f:
        f.write(usr + '\n')
    banned_users.append(usr)
    app.send_message(admin, f'Usuário <code>{usr}</code> foi banido.')




# unban user
@app.on_message(filters.private & filters.chat(admin) & filters.command('unban'))
def unban(client, message):
    pass
    # TODO implement this function




# get bot metrics
@app.on_message(filters.private & filters.command('data') & filters.chat(admin))
def dt(client, message):
    r = requests.get('') # paste a link here

    dat = {
        'activeusers': len(users),
        'bannedusers': len(banned_users),
        'downloadedvideos': videosdownloaded,
        'status': r.status_code,
    }

    app.send_message(admin, dat)




# update channel
@app.on_message(filters.private & filters.chat(admin) & filters.command('updatech'))
def upd(client, message):
    global defchannel
    nch = message.text.replace('/updatech', '').strip()
    defchannel = nch
    app.send_message(admin, f'O canal foi alterado para {defchannel}')




# update group
@app.on_message(filters.private & filters.chat(admin) & filters.command('updategp'))
def updgp(client, message):
    # format: t.me/groupusername
    global defgroup
    ngp = message.text.replace('/updategp', '').strip()
    with open('defgroup.txt', 'w') as f:
        f.write(ngp)
    defgroup = ngp

    app.send_message(admin, f'O grupo foi alterado para {defgroup}')




# download and send video
@app.on_message(filters.private)
def download(client, message):
    global videosdownloaded
    # check if user time has passed or if a new user is using: assign the default settings
    if message.chat.id not in user_time:
        user_time[message.chat.id] = True

    elif message.chat.id not in users:
        save_new_user(message.chat.id)
        users[message.chat.id] = default_conf
    
    which_option = ''

    option_video = {
        'format': f"b[ext=mp4][height={users[message.chat.id]['quality']}] / mp4",
        'outtmpl': f'./downloads/{message.chat.id}/' + '%(id)s.%(ext)s',
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            }
        ],
        'tbr': 500,
        'fps': 60,
    }

    option_audio = {
        'format': 'b*[ext=m4a]',
        'outtmpl': f'./downloads/{message.chat.id}/' + '%(title)s.%(ext)s',
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            }
        ],
        'height': users[message.chat.id]['quality'],
    }


    if users[message.chat.id]['type'] == 'audio':
        which_option = option_audio

    else:
        which_option = option_video

    match = re.match(regex, message.text)

    if message.chat.id in banned_users:
        app.send_message(message.chat.id, 'Você foi banido.')

    elif match and user_time[message.chat.id] == True:
        link = match.group(0)

        with YoutubeDL(which_option) as ydl:
            meta = ydl.extract_info(link, download=False)

            try:
                if users[message.chat.id]['type'] == 'audio':
                    # downloading audio
                    app.send_message(message.chat.id, f'Baixando: {meta["title"]}')
                    ydl.download([link])
                    videosdownloaded = videosdownloaded + 1

                    mus_name = unidecode(meta['title']).replace('"', '').replace("'", '')
                    old_name = f'./downloads/{message.chat.id}/' + f'{meta["title"]}.{meta["ext"]}'
                    new_name = f'./downloads/{message.chat.id}/' + f'{mus_name}.{meta["ext"]}'
                    os.rename(old_name, new_name)
                    save_location = new_name
                
                elif users[message.chat.id]['type'] == 'video':
                    # downloading video
                    app.send_message(message.chat.id, f'Baixando: {meta["title"]}')
                    ydl.download([link])
                    videosdownloaded = videosdownloaded + 1
                    save_location = f'./downloads/{message.chat.id}/' + meta['id'] + '.' + meta['ext']
            
            except Exception as err:
                app.send_message(admin, f'Erro: {err}')
                if 'DownloadError' in err:
                    app.send_message(message.chat.id, f'{meta["title"]}: Vídeo indisponível para download.')
                else:
                    app.send_message(message.chat.id, f'Erro desconhecido ao baixar o arquivo:{meta["title"]}\nOs logs de erro foram enviados para o desenvolvedor.')
            
            finally:
                if users[message.chat.id]['type'] == 'audio':
                    app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                    app.send_audio(message.chat.id, save_location)
                    videosdownloaded += 1

                    if users[message.chat.id]['premium'] == False and users[message.chat.id]['wmsg'] == 'sim':
                        user_time[message.chat.id] = False
                        sleep(time)
                        user_time[message.chat.id] = True
                        app.send_message(message.chat.id, wmsgtxt)

                    elif users[message.chat.id]['premium'] == False and users[message.chat.id]['wmsg'] == 'não':
                        user_time[message.chat.id] = False
                        sleep(time)
                        user_time[message.chat.id] = True

                elif users[message.chat.id]['type'] == 'video' and users[message.chat.id]['caption'] == 'não':
                    app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_VIDEO)
                    app.send_video(message.chat.id, save_location)

                    if users[message.chat.id]['premium'] == False and users[message.chat.id]['wmsg'] == 'sim':
                        user_time[message.chat.id] = False
                        sleep(time)
                        user_time[message.chat.id] = True
                        app.send_message(message.chat.id, wmsgtxt)

                    elif users[message.chat.id]['premium'] == False and users[message.chat.id]['wmsg'] == 'não':
                        user_time[message.chat.id] = False
                        sleep(time)
                        user_time[message.chat.id] = True
                
                elif users[message.chat.id]['type'] == 'video' and users[message.chat.id]['caption'] == 'sim':
                    app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_VIDEO)
                    app.send_video(message.chat.id, save_location, caption=meta['title'])

                    if users[message.chat.id]['premium'] == False and users[message.chat.id]['wmsg'] == 'sim':
                        user_time[message.chat.id] = False
                        sleep(time)
                        user_time[message.chat.id] = True
                        app.send_message(message.chat.id, wmsgtxt)

                    elif users[message.chat.id]['premium'] == False and users[message.chat.id]['wmsg'] == 'não':
                        user_time[message.chat.id] = False
                        sleep(time)
                        user_time[message.chat.id] = True
    
    elif not match:
        # add reply markup with button to ask the dev
        app.send_message(message.chat.id, "Serviço não suportado.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Requisitar serviço', url='t.me/skynetdevbots')],
        ]))

    elif user_time[message.chat.id] == False:
        app.send_message(message.chat.id, time_text)
    
    else:
        app.send_message(admin, message.text)




if __name__ == '__main__':
    app.run()
