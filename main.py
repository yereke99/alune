#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from load import bot, dp
from aiogram import types
from FormaAdmin import *
from keyboard import*
from database import*
from config import*
from Forma import*
import asyncio
from traits import*
import time
from FormaAdmin import*
from aiogram.types import InputMediaPhoto, InputMediaVideo
import os
from tests import*

generator = Generator()
btn = Button()
db = Database()



@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def pdf_received_handler(message: types.Message, state: FSMContext):
    # Проверяем, что отправленный файл — это PDF
    if message.document.mime_type == 'application/pdf':
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
            # Убедитесь, что округление и деление выполнены корректно
            data['count'] = int(convert_currency_to_int(result[3]) / 1000)
            sum = 1000 * data['count']
            data['sum'] = sum

        print(f"Expected sum: {data['sum']}, Actual sum: {convert_currency_to_int(data['pdf_result'][3])}")

        if convert_currency_to_int(data['pdf_result'][3]) != data['sum']: 
            await bot.send_message(
                message.from_user.id,
                text="*Төленетін сумма қате!\nҚайталап көріңіз*",
                parse_mode="Markdown",
                reply_markup=btn.menu()
            ) 
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
                    reply_markup=btn.menu()
                )   
                return

            await Forma.s3.set()
            await bot.send_message(
                message.from_user.id,
                text="*Аты жөніңізді жазыңыз*",
                parse_mode="Markdown",

            )
            return
    
        await bot.send_message(
                message.from_user.id,
                text="*Дұрыс емес счетқа төледіңіз!\nҚайталап көріңіз*",
                parse_mode="Markdown",
                reply_markup=btn.menu_not_paid()
            )  

    else:
        # Если отправлен не PDF-файл, можно уведомить пользователя
        await message.reply("Тек, PDF файл жіберу керек!")
    


@dp.message_handler(commands=['admin'])
async def handler(message: types.Message):
    print(message.from_user.id)
    

    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        await bot.send_message(
        message.from_user.id,
        text="😊 *Сәлеметсіз бе %s !\nСіздің статусыңыз 👤 Админ(-ка-)*"%message.from_user.first_name,
        parse_mode="Markdown",
        reply_markup=btn.admin()
    )
        

@dp.message_handler(Text(equals="📈 Статистика"), content_types=['text'])
async def handler(message: types.Message):
    if message.from_user.id in {admin, admin2, admin3}:
        # Получаем статистику из базы данных
        tik_tok_count = db.get_tiktok_count()
        instagram_count = db.get_instagram_count()
        
        # Форматируем сообщение
        stats_message = (
            f"📊 <b>Статистика:</b>\n\n"
            f"🔹 TikTok: {tik_tok_count} заходов\n"
            f"🔹 Instagram: {instagram_count} заходов\n"
        )
        
        # Отправляем сообщение
        await message.reply(stats_message, parse_mode="HTML")

@dp.message_handler(commands=['start', 'go'])
async def start_handler(message: types.Message):
    
    args = message.get_args()

    if args == "TikTok":
        # Логика для TikTok
        db.tiktok_counter()
        await Forma.s1.set()
        await bot.send_message(
            message.from_user.id,
            text="*Қанша косметика жинақ алғыңыз келеді? Билет саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
        ) 
        return
    elif args == "Instagram":
        # Логика для Instagram
        db.instagram_counter()
        await Forma.s1.set()
        await bot.send_message(
            message.from_user.id,
            text="*Қанша косметика жинақ келеді? Билет саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
        )
        return 

    print(message.from_user.id)

    from datetime import datetime
    fileId = "AgACAgIAAxkBAAMEZ12dAAFvprcfkSLlfunyQiNcAAHC5gACLeYxGxZu8UqeVspKQ5ihVgEAAwIAA3kAAzYE"

    user_id = message.from_user.id
    user_name = f"@{message.from_user.username}"
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    db.JustInsert(user_id, user_name, time_now)  
    
    if db.CheckUserPaid(message.from_user.id) == True:
        await bot.send_photo(
            message.from_user.id,
            fileId,
            caption="""*Сәлееем😍

Әлемдік бренд ALUNE люкс сападағы косметика наборын 40 000 теңгеге алу арқылы автоматты түрде сіз АЛМАТЫ қаласындағы 150.000.000 теңгелік 2 этажды коттеждің және әртүрлі құнды, бренд заттардың иесі атанасыз ❤️*""",
            parse_mode="Markdown",
            protect_content=True,
            reply_markup=btn.buy_cosmetic(),
        )
        return
    

    await bot.send_photo(
        message.from_user.id,
        fileId,
        caption="""*Сәлееем😍

1. Әлемдік бренд ALUNE люкс сападағы косметика наборын 40 000 теңгеге алу арқылы автоматты түрде сіз АЛМАТЫ қаласындағы 150.000.000 теңгелік 2 этажды коттеждің және әртүрлі құнды, бренд заттардың иесі атанасыз ❤️

2. Ссылка беріледі сайттың
3. Договор-офертамен танысуыңызды сұраймыз! Танысып болған соң ары қарай жалғастыру үшін “📃 Оффертамен ✔️ таныстым” батырмасын басыңыз*""",        
        parse_mode="Markdown",
        protect_content=True,
        reply_markup=btn.offertas(),
    )


@dp.message_handler(Text(equals="💋 Косметика сатып алу"), content_types=['text'])
async def handler(message: types.Message):
    
    await Forma.s1.set()
    await bot.send_message(
            message.from_user.id,
            text="*Қанша 💋 косметика алғыңыз келеді? Косметика саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
    ) 

@dp.callback_query_handler(lambda c: c.data in ["buy_cosmetics", "accept"])
async def process_callback(callback_query: types.CallbackQuery):
    # Удаляем предыдущее сообщение
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)

    await bot.answer_callback_query(callback_query.id)

    if callback_query.data == "buy_cosmetics":
        # Логика для "buy_cosmetics"
        await Forma.s1.set()
        await bot.send_message(
            callback_query.from_user.id,
            text="*Қанша 💋 косметика жиынтық алғыңыз келеді? Косметика саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
        )
    elif callback_query.data == "accept":
        # Логика для "accept"
        await bot.send_message(
            callback_query.from_user.id,
            text="Сіз оффертаны қабылдадыңыз. Рахмет! 😊\n\nPDF - форматта чекті жіберіңіз 👇",
            reply_markup=btn.menu()
        )



# Новый хендлер для обработки отправки PDF-файла
@dp.message_handler(content_types=types.ContentType.DOCUMENT, state='*')
async def pdf_received_handler(message: types.Message, state: FSMContext):
    pass

@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO])
async def media_handler(message: types.Message, state: FSMContext):
    file_id = None

    # Проверяем тип контента
    if message.content_type == 'photo':
        # Получаем file_id самого большого размера фото
        file_id = message.photo[-1].file_id
    elif message.content_type == 'video':
        # Получаем file_id видео
        file_id = message.video.file_id

    if file_id:
        # Сохраняем file_id в состоянии
        async with state.proxy() as data:
            data['file_id'] = file_id

        # Отправляем file_id пользователю
        await bot.send_message(
            message.from_user.id,
            text=f"*FileID: {data['file_id']}*",
            parse_mode="Markdown",
        )
    else:
        await bot.send_message(
            message.from_user.id,
            text="Ошибка: неизвестный тип медиафайла.",
        ) 

@dp.message_handler(Text(equals="💸 Money"), content_types=['text'])
async def handler(message: types.Message):
    
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        sum = db.get_money_sum()
        await bot.send_message(
                message.from_user.id,
                text="""*💳 Жалпы қаражат: %d*"""%sum,
                parse_mode="Markdown",
                reply_markup=btn.admin()
            )    

@dp.message_handler(Text(equals="📨 Хабарлама жіберу"), content_types=['text'])
async def handler(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        await FormaAdmin.s1.set()
        await bot.send_message(
                message.from_user.id,
                text="""*✏️ Хабарлама типін таңдаңыз*""",
                parse_mode="Markdown",
                reply_markup=btn.typeMsg()
            )     



@dp.message_handler(commands=['help'])
@dp.message_handler(Text(equals="📨 Әкімшіге хабарлама"), content_types=['text'])
async def handler(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        text="""*+77005007032* - телеграм номер\n\n*+77786557207* - Айдана, БИЗНЕС ВАТСАП НОМЕР""",
        parse_mode="Markdown",
        reply_markup=btn.linkTelega()
    )


@dp.message_handler(Text(equals="📑 Лото"), content_types=['text'])
async def send_just_excel(message: types.Message):
    if message.from_user.id == admin:
        db.create_loto_excel('./excell/loto.xlsx')
        await bot.send_document(message.from_user.id, open('./excell/loto.xlsx', 'rb'))

@dp.message_handler(Text(equals="👥 Қолданушылар саны"), content_types=['text'])
async def send_client_excel(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        db.create_client_excel('./excell/clients.xlsx')
        await bot.send_document(message.from_user.id, open('./excell/clients.xlsx', 'rb'))

@dp.message_handler(Text(equals="👇 Just Clicked"), content_types=['text'])
async def send_loto_excel(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        db.create_just_excel('./excell/just_users.xlsx')
        await bot.send_document(message.from_user.id, open('./excell/just_users.xlsx', 'rb'))
    


@dp.message_handler(Text(equals="📨 Хабарлама жіберу"), content_types=['text'])
async def handler(message: types.Message):

    await bot.send_message(
        message.from_user.id,
        text="""*@senior_coffee_drinker*""",
        parse_mode="Markdown",
        reply_markup=btn.admin()
    ) 


@dp.message_handler(Text(equals="🧧 Ұтыс билеттерім"), content_types=['text'])
async def handler(message: types.Message):

    id_user = message.from_user.id            # Get the user ID from the message
    loto_ids = db.FetchIdLotoByUser(id_user)  # Fetch the list of id_loto for this user
    
    if loto_ids:
        ids_formatted = ", ".join(map(str, loto_ids))  # Format the list as a comma-separated string
        response_text = f"Сіздің ұтыс билеттеріңіздің ID-лары: {ids_formatted}"
    else:
        response_text = "Сіздің ұтыс билетіңіз жоқ."

    await bot.send_message(
        message.from_user.id,
        text=response_text,
        parse_mode="Markdown",
        reply_markup=btn.menu()
    )

@dp.message_handler(Text(equals="◀️ Кері"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id == admin or message.from_user.id == admin2:
        await bot.send_message(
        message.from_user.id,
        text="😊 *Сәлеметсіз бе %s !\nСіздің статусыңыз 👤 Админ(-ка-)*"%message.from_user.first_name,
        parse_mode="Markdown",
        reply_markup=btn.admin()
    )

async def send_pdf_with_caption(user_id, id_loto, caption):
    loto_info = db.fetch_loto_by_id(id_loto)
    if not loto_info:
        await bot.send_message(user_id, text="PDF not found.")
        return

    receipt = loto_info[3]  # Adjusted index for receipt column
    pdf_path = f"/home/cinema/pdf/{receipt}"
    
    if os.path.exists(pdf_path):
        await bot.send_document(
            user_id,
            document=open(pdf_path, 'rb'),
            caption=caption,
            reply_markup=btn.gift()
        )
    else:
        await bot.send_message(user_id, text="PDF file not found.")


from aiogram.types import InputFile


# Функция для поиска файла в нескольких директориях
def find_pdf_file(file_name: str) -> str:
    directories = ["/home/clone/pdf/", "/home/movie-alish/pdf/", "/home/movie/pdf/"]
    for directory in directories:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            return file_path
    return None

# Хэндлер для обработки текстового сообщения с ID
@dp.message_handler(content_types=['text'])
async def handle_gift_car_request(message: types.Message):
    user_input = message.text.strip()

    try:
        # Пробуем конвертировать ввод в целое число
        requested_id = int(user_input)

        # Получаем значение receipt из базы данных по id_loto
        receipt = db.get_receipt_by_id(requested_id)
        print(receipt)
        
        if not receipt:
            await message.reply("Файл с таким ID не найден в базе данных.")
            return

        file_name = f"{receipt}"
        file_path = find_pdf_file(file_name)

        if file_path:
            await message.reply_document(InputFile(file_path))
        else:
            await message.reply("Файл не найден в указанных директориях.")
    
    except ValueError:
        # Если не получилось преобразовать ввод в число
        await message.reply("Пожалуйста, введите ID в числовом формате.")