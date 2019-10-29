#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from tinytag import TinyTag
from google.cloud import speech
from google.cloud import storage
from google.cloud.speech import enums
from google.cloud.speech import types
import os
import io
import wget

TOKEN = '967137698:AAFnPBS4z-KsdKoTY0psSnKzkWoDIqBioNg'
PORT = int(os.environ.get('PORT', '5002'))
BUCKET_NAME = 'transctipy_bot'
ADMIN_CHAT_ID = 123456
updater = Updater(TOKEN)
dispatcher = updater.dispatcher


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Olá Amigo! Pode gravar o que quiser, eu irei transcrever!")


@run_async
def voice_to_text(bot, update):
    print('entrou')
    chat_id = update.message.chat.id
    #file_name = str(chat_id) + '_' + str(update.message.from_user.id) + str(update.message.message_id) + '.wav'

    #update.message.document.get_file().download(file_name)
    #update.message.document.get_file()['file_path']

    #file_name = 
    file_name = str(update.message.document.get_file()['file_path']).split('/')
    file_name = file_name[int(len(file_name)) - 1]
    print(file_name)
    wget.download(update.message.document.get_file()['file_path'])
    print(file_name)

    #tag = TinyTag.get(update.message.document.get_file()['file_path'])
    #length = tag.duration

    speech_client = speech.SpeechClient()

    #to_gs = length > 58



    #if to_gs:
     #   storage_client = storage.Client()

    bucket = storage_client.get_bucket(BUCKET_NAME)
    print(bucket)
    blob = bucket.blob(file_name)
    print(blob)
    blob.upload_from_filename(file_name)
    print(blob.upload_from_filename(file_name))
    audio = types.RecognitionAudio(uri='gs://' + BUCKET_NAME + '/' + file_name)
    print(audio)
    #else:
    #    with io.open(file_name, 'rb') as audio_file:
    #        content = audio_file.read()
    #        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.wav,
        sample_rate_hertz=tag.samplerate,
        language_code='pt-BR'
        )

    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    response = speech_client.long_running_recognize(config, audio).result(timeout=500) \
        #if to_gs else \
    speech_client.recognize(config, audio)
    
    message_text = ''
    for result in response.results:
        message_text += result.alternatives[0].transcript + '\n'

    update.message.reply_text(message_text)
    os.remove(file_name)


def ping_me(bot, update, error):
    if not error.message == 'Timed out':
        bot.send_message(chat_id=ADMIN_CHAT_ID, text=error.message)


start_handler = CommandHandler(str('start'), start)
oh_handler = MessageHandler(Filters.document, voice_to_text)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(oh_handler)
dispatcher.add_error_handler(ping_me)
updater.start_polling()
updater.idle()
