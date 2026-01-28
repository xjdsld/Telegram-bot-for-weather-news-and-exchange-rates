import telebot
import requests
from telebot import types

bot = telebot.TeleBot('')
Weather_API = ''
GNEWS_API = ''
EXCANGE_API = ''
last_city = {}
faves = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Hello! Type /weather to get weather, /news for news and /exchange for the exchange rate')

@bot.message_handler(commands = ['weather'])
def get_city(message):
    bot.send_message(message.chat.id, 'Enter the city to get weather for in this format "/city Kyiv"')

@bot.message_handler(commands= ['city'])
def get_weather_for_the_city(message):
    chat_id = message.chat.id
    city = message.text.replace('/city ', '', 1).strip()  
    if not city:  
        bot.send_message(chat_id, 'Please provide a city after /city, e.g., /city Kyiv') 
        return
    last_city[chat_id] = city

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={Weather_API}"
    params = {
        "lang": "en",
        "units": "metric",
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        temp = data["main"]["temp"]
        weather = data["weather"][0]["description"]
        bot.send_message(message.chat.id, f"city: {city}, temp: {temp}, weather: {weather}")
    else:
        bot.send_message(message.chat.id, 'No results found')

    bot.send_message(message.chat.id, 'Do you want to save this city to your favorites, type "/save" to confirm')

@bot.message_handler(commands= ['save'])
def save_city(message):
    chat_id = message.chat.id
    if chat_id in last_city:
        city = last_city[chat_id]
        if chat_id not in faves:
            faves[chat_id] = []
        faves[chat_id].append(city)
        bot.send_message(chat_id, f"{city} saved to your favorites!")
    else:
        bot.send_message(chat_id, "No city to save. Please check weather first.")

@bot.message_handler(commands= ['favourites'])
def get_favourites(message):
    chat_id = message.chat.id
    if chat_id  not in faves:
        bot.send_message(chat_id, 'You have no cities saved')
        return

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = []
    for city in faves[chat_id]:
        button = types.KeyboardButton(city)
        buttons.append(button)    
    keyboard.add(*buttons)

    bot.send_message(chat_id, "Your favorite cities:", reply_markup=keyboard)

def is_favourite_city(message):
    chat_id = message.chat.id
    if chat_id not in faves:
        return False
    if message.text not in faves[chat_id]:
        return False
    return True

@bot.message_handler(func=is_favourite_city)
def get_wheather_for_favourit_city(message):
    city = message.text

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={Weather_API}"
    params = {
        "lang": "en",
        "units": "metric",
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        temp = data["main"]["temp"]
        weather = data["weather"][0]["description"]
        bot.send_message(message.chat.id, f"city: {city}, temp: {temp}, weather: {weather}")
    else:
        bot.send_message(message.chat.id, 'No results found')
    
    
        
@bot.message_handler(commands = ['news'])
def get_news_category(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Enter the category for the news like this: /topic Ukraine')

@bot.message_handler(commands= ['topic'])
def send_news(message):
    chat_id = message.chat.id
    category = message.text.replace('/topic ', '', 1).strip()
    if not category:  
        bot.send_message(chat_id, 'Please provide a category after /topic, e.g., /topic Ukraine')  
        return

    endpoint = "search"
    parameters = {
        "q": category,
        "lang": "en",
        "max": 5,
        "nullable": "description,content"
    }
    url = 'https://gnews.io/api/v4/search'
    parameters["apikey"] = GNEWS_API

    response = requests.get(url, params=parameters)
    data = response.json()

    if response.status_code != 200:
        bot.send_message(chat_id, "No information found.")
        return

    data = response.json()
    articles = data.get("articles", [])
    if not articles:
        bot.send_message(chat_id, "No news found for this keyword.")  
        return

    for article in articles:
        bot.send_message(chat_id, f"Title: {article['title']}\n{article['url']}")  

@bot.message_handler(commands = ['exchange'])
def get_exchange_rate(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Enter the currency you want to compare to UAH like this: /currency USD')

@bot.message_handler(commands= ['currency'])
def send_exchange_rate(message): 
    chat_id = message.chat.id
    currency = message.text.replace('/currency ', '', 1).strip()
    if not currency:  
        bot.send_message(chat_id, 'Please provide a currency after /currency, e.g., /currency USD')  
        return

    url = f'https://v6.exchangerate-api.com/v6/{EXCANGE_API}/latest/UAH'


    response = requests.get(url)
    data = response.json()
    rates = data.get("conversion_rates", {})
    rate = rates.get(currency.upper())

    if not rate:
        bot.send_message(chat_id, "Currency not found.")
        return

    bot.send_message(chat_id, f"1 UAH = {rate} {currency.upper()}")

    if response.status_code != 200:
        bot.send_message(chat_id, "No information found.")
        return
        
bot.polling()
