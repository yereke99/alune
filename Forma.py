from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import Message
from load import dp, bot
from aiogram import types 
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import logging
from keyboard import*
from database import Database
import datetime
from main import*
import asyncio
from config import admin, admin2, admin3
from datetime import datetime
from traits import *
import time
from traits import*
from config import*
import os
from aiogram.types import InputMediaPhoto, InputMediaVideo
from tests import *

generator = Generator()
btn = Button()
db = Database()

# Dont touch!
#file_id = "BAACAgIAAxkBAAIBfmZVvFgHXNy6dEjDe2rDHuGlC3jrAALaTQAC1jOpSiMaJlO20CwKNQQ"  

c1 = "AgACAgIAAxkBAAMVZyYg7KuSuN_IPDYgM5ULXX7AzhkAAqzhMRvQzjBJDkg8df7HrdYBAAMCAAN5AAM2BA"
c2 = "AgACAgIAAxkBAAMXZyYg7ivtTtgaTt3uOn_SthmgAqQAAq3hMRvQzjBJKU9TV6vMYh4BAAMCAAN5AAM2BA"
c3 = "AgACAgIAAxkBAAMZZyYg8clEejb320N0ZrK_Jb5YAV8AAq7hMRvQzjBJhxNPNuDLOMkBAAMCAAN5AAM2BA"

# Ensure the directory exists
os.makedirs('./pdf/', exist_ok=True)

class Forma(StatesGroup):
    s1 = State()  # Косметика саны
    s2 = State()  # Read PDF
    s3 = State()  # FIO
    s4 = State()  # Контакт
    s5 = State()  # Қала


@dp.message_handler(state='*', commands='🔕 Бас тарту')
@dp.message_handler(Text(equals='🔕 Бас тарту', ignore_case=True), state='*')
async def cancell_handler(message: types.Message, state: FSMContext):
    """
    :param message: Бастартылды
    :param state: Тоқтату
    :return: finish
    """
    
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Бас тарту!')
    
    await state.finish()
    await message.reply('Сіз тапсырыстан бас тарттыңыз.', reply_markup=btn.menu_not_paid())



@dp.message_handler(lambda message: not message.text.isdigit(), state=Forma.s1)
async def handler(message: types.Message):
    return await message.reply("Сандармен жазыңыз 🔢")


@dp.message_handler(lambda message: message.text.isdigit(), state=Forma.s1)
async def handler(message: types.Message, state: FSMContext):

    """
    state: number
    """
    try:
        await Forma.next()

        async with state.proxy() as data:
            data['count'] = int(message.text)

        sum = 1000 * data['count']

        async with state.proxy() as data:
            data['sum'] = sum


        await bot.send_message(
            message.from_user.id,
            text="""Инструкция:

Оплата жасау үшін сілтемеге өтіңіз: https://pay.kaspi.kz/pay/c8b6jc5o
Мұнде міндетті түрде 40 0000 теңге төлену керек. Басқа сумма төлеп қойсаңыз, бот оқымайды және ақшаңыз қайтпайды. Қателеспей төлеңіз!

1. Төлем жасап болған соң чекті ПДФ файл арқылы жіберіңіз( фотода көрсетілгендей)

2. Төленетін сумма 40 000 теңгенің біреуі болу керек

3. Төлем өткен соң бот сізге киноға билет нөмеріңізбен, киноларды жібереді

ПДФ файлымен чекті төменге жіберіңіз  👇"""
        )

        """"""

        await bot.send_message(
            message.from_user.id,
            text="*Kaspi Pay - төлем жүйесін қолдана отыра 💳 төлем жасаңыз\nКиноның 💳 бағасы: %d теңге*"%sum,
            parse_mode="Markdown",
            reply_markup=btn.payment()
        ) 
        
    except Exception as e:
        print(e) 
        await Forma.s1.set()
        await bot.send_message(
            message.from_user.id,
            text="*Қанша косметика жиынтық алғыңыз келеді? Косметика жиынтық саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
        )   

        await bot.send_message(
            admin,
            text="Error: %s"%str(e),
        )   

@dp.message_handler(lambda message: not (message.document and message.document.mime_type == 'application/pdf'), state=Forma.s2, content_types=types.ContentType.DOCUMENT)
async def pdf_validator(message: types.Message, state: FSMContext):
    await message.reply(".pdf файл форматымен жіберіңіз!")
    await Forma.s2.set()

@dp.message_handler(state=Forma.s2, content_types=types.ContentType.DOCUMENT)
async def handler(message: types.Message, state: FSMContext):

    try:
        document = message.document

        # Generate a unique filename
        user_id = message.from_user.id
        timestamp = int(time.time())
        random_int = Generator.generate_random_int()
        file_name = f"{user_id}_{timestamp}_{random_int}.pdf"
        file_path = os.path.join('./pdf/', file_name)

        # Download the PDF file
        file_info = await bot.get_file(document.file_id)
        await bot.download_file(file_info.file_path, file_path)

        # Process the PDF file
        pdf_reader = PDFReaders(file_path)
        pdf_reader.open_pdf()
        #result = pdf_reader.extract_specific_info()
        result = pdf_reader.extract_detailed_info()
        pdf_reader.close_pdf()


        async with state.proxy() as data:
            data['data'] = message.text
            data['pdf_result'] = result
            data['fileName'] = file_name

        print(data['pdf_result'])
        
        if convert_currency_to_int(data['pdf_result'][3]) != data['sum']: 
            await bot.send_message(
                message.from_user.id,
                text="*Төленетін сумма қате!\nҚайталап көріңіз*",
                parse_mode="Markdown",
                reply_markup=btn.menu_not_paid()
            )  
            await state.finish() 
            return
        
        print(data['pdf_result'][3])
        print(data['pdf_result'][11])
       
        if data['pdf_result'][10] == "Сатушының ЖСН/БСН 040615601206" or data['pdf_result'][10] == "ИИН/БИН продавца 040615601206" or data['pdf_result'][10] == "Сатушының ЖСН/БСН 811103400721" or data['pdf_result'][10] == "ИИН/БИН продавца 811103400721":
            print(db.CheckLoto(data['pdf_result'][6]))
            if db.CheckLoto(data['pdf_result'][6]) == True:
                await bot.send_message(
                    message.from_user.id,
                    text="*ЧЕК ТӨЛЕНІП ҚОЙЫЛҒАН!\nҚайталап көріңіз*",
                    parse_mode="Markdown",
                    reply_markup=btn.menu_not_paid()
                )  
                await state.finish() 
                return

            await Forma.next()
            await bot.send_message(
                message.from_user.id,
                text="*Аты жөніңізді жазыңыз*",
                parse_mode="Markdown",
                reply_markup=types.ReplyKeyboardRemove()

            )
            return
    
        await bot.send_message(
                message.from_user.id,
                text="*Дұрыс емес счетқа төледіңіз!\nҚайталап көріңіз*",
                parse_mode="Markdown",
                reply_markup=btn.menu_not_paid()
            )  
        await state.finish() 

    except Exception as e:
        print(e)
        await bot.send_message(
            admin,
            text="Error: %s"%str(e),
        ) 

        username = message.from_user.username
        user_id = message.from_user.id
        # Формирование сообщения
        caption = f"Файл от пользователя:\n\n👤 Username: @{username if username else 'Нет username'}\n🆔 User ID: {user_id}"
        for admin_id in [admin, admin2, admin3]:
            try:
                # Отправляем PDF файл администратору
                file_path = "/home/alune/pdf/" +data['fileName']
                with open(file_path, 'rb') as file:
                    await bot.send_document(admin_id, document=file, caption=caption)
            except Exception as ex:
                print(f"Не удалось отправить файл администратору {admin_id}: {str(ex)}")
        
        await Forma.s2.set()
        await bot.send_message(
                message.from_user.id,
                text="Төлем жасаған соң чекті 📲 .pdf форматында жіберіңіз!\n\n*НАЗАР АУДАРЫҢЫЗ ЧЕКТІ МОДЕРАТОР ТЕКСЕРЕДІ\n\n ЕСКЕРТУ ❗️\nЖАЛҒАН ЧЕК ЖІБЕРУ НЕМЕСЕ БАСҚАДА ДҰЫРЫС ЕМЕС ЧЕКТЕР ЖІБЕРУ АВТОМАТТЫ ТҮРДЕ ҰТЫС ОЙЫННАН ШЫҒАРЫЛАДЫ*",
                parse_mode="Markdown",
                reply_markup=btn.cancel()
            ) 
        

@dp.message_handler(state=Forma.s3)
async def handler(message: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        data['fio'] = message.text
    
    await Forma.next()

    await bot.send_message(
        message.from_user.id,
        text="*Сізбен кері 📲 байланысқа шығу үшін байланыс нөміріңізді қалдырыңыз! Төменде тұрған \n\n📱 Контактімен бөлісу кнопкасын басыныз\n\nЕШҚАШАН САНДАРМЕН ЖАЗБАЙМЫЗ ‼️*",
        parse_mode="Markdown",
        reply_markup=btn.send_contact()
    )
    
    
    
@dp.message_handler(state=Forma.s4, content_types=types.ContentType.CONTACT)
async def handler(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['contact'] = message.contact.phone_number
    
    await Forma.next() 
    
    db.increase_money(data['sum'])

    await bot.send_message(
            message.from_user.id,
            text="""*11. Қалаңызды таңдаңыз👇🏻

Ескерту! Төмендегі бір адресті таңдап, товарды сол жерден алып кетесіз. Қалалардың үстінен басып таңдаңыз*""",
            parse_mode="Markdown",
            reply_markup=btn.city()
        )

    

@dp.message_handler(state=Forma.s5)
async def handler(message: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        data['city'] = message.text

    
    if db.InsertClient(message.from_user.id, message.from_user.username,  data['fio'], data['contact'], data['city'], datetime.now(), "paid", "true"):

        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for i in range(int(data['count'])):
            gen = generator.generate_random_int()
            db.InsertLoto(
                message.from_user.id,
                gen,
                data['pdf_result'][6],
                message.from_user.username,
                data['fileName'],  
                data['fio'],
                data['contact'],
                data['city'],
                time_now,
            )

        await bot.send_message(
            message.from_user.id,
            text="""Құттықтаймыз сіз 💋 косметика жинағына сәтті төлем жасадыңыз 👏\n\nАлып кету адрестері 30-желтоқсан бастап жүзеге асады

Оған дейін тарату, алып кету, жеткізу қызметі жоқ!

Қосымша сұрақтарыңыз болса👇🏻
/help - батырмасын басыңыз
""",
            parse_mode="Markdown",
            reply_markup=btn.menu()
        )

        await state.finish() 
        return
    else:
        await bot.send_message(
            message.from_user.id,
            text="*Ой 🤨 бір нәрседен қате кетті\nҚайталап көріңіз*",
            parse_mode="Markdown",
            reply_markup=btn.menu_not_paid()
        )  
        await state.finish() 


    await state.finish()
    
