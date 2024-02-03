import telebot
from telebot import types
import random
import time
from PIL import Image, ImageDraw, ImageFont
bot = telebot.TeleBot('6949454086:AAFd6U73U_Ng-aG2-EB2I5tuCah9ZkKN2wE')

# Словарь для хранения данных о валентинках
valentine_data = {}
is_valentine = 2
def delete_message(message, message_id, delay=0.5):
    bot.delete_message(message.chat.id, message_id)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Приветственный текст
    welcome_text = "Привет! Я ваш бот. Добро пожаловать!"

    # Создание InlineKeyboardMarkup
    markup = types.InlineKeyboardMarkup()

    # Добавление кнопок
    valentine_button = types.InlineKeyboardButton("Выберу валентинку", callback_data='valentine')
    bot_button = types.InlineKeyboardButton("Боту виднее", callback_data='bot')
    markup.row(valentine_button, bot_button)

    # Отправка приветственного текста с кнопками
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# Добавьте обработчик для обработки возвращаемых данных от кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    chat_id = call.message.chat.id

    if call.data == 'valentine':
        # Создание inline-клавиатуры с цифрами и кнопкой "назад"
        markup = types.InlineKeyboardMarkup()
        row = []
        for i in range(1, 11):
            button = types.InlineKeyboardButton(str(i), callback_data=f'number_{i}')
            row.append(button)
            if len(row) == 2:
                markup.add(*row)
                row = []

        back_button = types.InlineKeyboardButton("Назад", callback_data='back')
        markup.add(back_button)

        # Отправка фото и текста "Выберите изображение"
        bot.send_photo(chat_id, open('collage.jpg', 'rb'), caption="Выберите изображение", reply_markup=markup)

    elif call.data == 'bot':
        valentine_data[is_valentine] = 0
        delete_message(call.message, call.message.message_id)
        back_button = types.InlineKeyboardButton("Назад", callback_data='back')
        back_markup = types.InlineKeyboardMarkup().add(back_button)

        # Спрашиваем у пользователя от кого валентинка
        bot.send_message(chat_id, "Напишите, кому вы хотите отправить валентинку. Например, 'Александру'",
                         reply_markup=back_markup)
        rand = random.randint(1, 10)
        valentine_data[chat_id] = {'number': rand}
        valentine_data['number'] = rand

    elif call.data.startswith('number_'):
        # Обработка нажатия на кнопку с цифрой
        number = int(call.data.split('_')[1])

        valentine_data[is_valentine] = 1

        delete_message(call.message, call.message.message_id)

        # Сохраняем выбранное число в словаре valentine_data
        valentine_data[chat_id] = {'number': number}
        valentine_data['number'] = number

        # Добавление кнопки "Назад" под сообщением
        back_button = types.InlineKeyboardButton("Назад", callback_data='back')
        back_markup = types.InlineKeyboardMarkup().add(back_button)
        bot.send_message(chat_id, "Напишите, кому вы хотите отправить валентинку. Например, 'Александру'",
                         reply_markup=back_markup)

    elif call.data == 'back':
        delete_message(call.message, call.message.message_id)
        # Отправка приветственного сообщения после нажатия кнопки "назад"
        send_welcome(call.message)


# Добавим обработчик текстовых сообщений для сохранения информации о валентинках
@bot.message_handler(
    func=lambda message: message.text and message.chat.id in valentine_data and 'number' in valentine_data[
        message.chat.id])
def process_valentine_recipient(message):
    chat_id = message.chat.id

    # Сохраняем текст в словаре valentine_data
    valentine_data[chat_id] = {'recipient': message.text}

    # Спрашиваем у пользователя от кого валентинка
    bot.send_message(chat_id, "Напишите, от кого вы хотите отправить валентинку. Например, 'Александры'")

# Добавим обработчик текстовых сообщений для сохранения информации о валентинках
@bot.message_handler(func=lambda message: message.text and message.chat.id in valentine_data and 'recipient' in valentine_data[message.chat.id])
def process_valentine_sender(message):
    chat_id = message.chat.id

    # Сохраняем текст в словаре valentine_data
    valentine_data[chat_id]['sender'] = message.text

    number = valentine_data['number']
    # Отправка изображения после получения обоих ответов от пользователя
        # Создаем изображение
    image = Image.open(f"pic{number}.jpg")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 25)

    # Получаем текст от пользователя
    sender_text = valentine_data[chat_id]['sender']
    recipient_text = valentine_data[chat_id]['recipient']

    # Добавляем текст "От кого" на изображение
    draw.text((120, 650), f"{sender_text}", (0, 0, 0), font=font)

    # Добавляем текст "Кому" на изображение
    draw.text((140, 670), f"{recipient_text}", (0, 0, 0), font=font)

    # Сохраняем измененное изображение
    image.save(f"pic{number + chat_id}.jpg")
    bot.send_photo(chat_id, open(f"pic{number + chat_id}.jpg", 'rb'))

    # Очищаем данные по валентинке
    valentine_data.pop(chat_id)

    # Добавление кнопки "Назад" под сообщением
    back_button = types.InlineKeyboardButton("Назад", callback_data='back')
    back_markup = types.InlineKeyboardMarkup().add(back_button)

    # Отправка приветственного сообщения и текста пользователя
    bot.send_message(chat_id, "Вот ваша валентинка! Если хотите отправить еще, нажмите 'Назад'", reply_markup=back_markup)

# Запуск бота
bot.polling(non_stop=True)