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
from google.api_core import retry
from dotenv import load_dotenv
import os
import io
import wget
load_dotenv()

PORT = int(os.environ.get('PORT', '5002'))
BUCKET_NAME = os.getenv("BUCKET_NAME")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
updater = Updater(os.getenv("TOKEN"))
dispatcher = updater.dispatcher


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Olá Amigo! Pode gravar o que quiser, eu irei transcrever!")


@retry.Retry(
    deadline=600)
@run_async
def voice_to_text(bot, update):
    chat_id = update.message.chat.id
    file_name = str(update.message.document.get_file()['file_path']).split('/')
    file_name = file_name[int(len(file_name)) - 1]
    print(file_name)
    wget.download(update.message.document.get_file()['file_path'])

    tag = TinyTag.get(file_name)

    speech_client = speech.SpeechClient()

    storage_client = storage.Client()

    bucket = storage_client.get_bucket(BUCKET_NAME)

    blob = bucket.blob(file_name)
    
    blob.upload_from_filename(file_name)
    print(blob.upload_from_filename(file_name))
    audio = types.RecognitionAudio(uri='gs://' + BUCKET_NAME + '/' + file_name)
    
    print(tag.samplerate)
    #else:
    #    with io.open(file_name, 'rb') as audio_file:
    #        content = audio_file.read()
    #        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=tag.samplerate,
        language_code='pt-BR'
        )

    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    operation = speech_client.long_running_recognize(config, audio)
    update.message.reply_text("Aguarde... Estou transcrevendo o áudio.")
    
    response = operation.result(timeout=1000000)
    
    message_text = ''
    for result in response.results:
        print(result)
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
