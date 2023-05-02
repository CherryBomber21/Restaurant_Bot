import logging
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import datetime
import random
import codecs
import sqlite3

# we connect a database with a list of restaurants in Moscow;
# table format: ID, name, price, location, kitchen, opening hours, address, coordinates
con = sqlite3.connect('db/restaurants.db')
cur = con.cursor()

# a function that checks whether the user will have time
# to get to the restaurant;
# compares the opening time of the restaurant with the present time
def to_go(k):
    dt_hour, dt_min = str(datetime.datetime.now().time())[:-10].split(':')
    opn, cls = k.split('--')
    if cls == '00:00':
        cls = '23:59'
    opn_hour, opn_min = str(datetime.time(int(opn.split(':')[0]), int(opn.split(':')[-1])))[:-3].split(':')
    cls_hour, cls_min = str(datetime.time(int(cls.split(':')[0]), int(cls.split(':')[-1])))[:-3].split(':')
    # print(opn, cls)
    if int(opn_hour) * 60 + int(opn_min) <= int(dt_hour) * 60 + int(dt_min) <= int(cls_hour) * 60 + int(cls_min):
        otv = f'сейчас {str(datetime.datetime.now().time())[:-10]}, он закрывается в {"00:00--00:00".split("--")[-1]}'
    else:
        otv = f'График работы ресторана: {"00:00--12:00"}, приходи завтра (или выбери другой ресторан))'
    return otv


# a website from where you can conveniently take sticker codes
# https://apps.timwhitlock.info/emoji/tables/unicode

# we enter codes for emojis
cookie = b'\xF0\x9F\x8D\xAA'
smile = b'\xF0\x9F\x98\x8A'
angry = b'\xF0\x9F\x98\xA0'
cf = b'\xE2\x98\x95'
wt = b'\xE2\x9D\xA4'
sf = b'\xF0\x9F\x90\xAC'
jp = b'\xF0\x9F\x87\xAF\xF0\x9F\x87\xB5'
gg = b'\xF0\x9F\x8D\xB7'
fr = b'\xF0\x9F\x87\xAB\xF0\x9F\x87\xB7'
ind = b'\xF0\x9F\x94\xA5'
ru = b'\xF0\x9F\x87\xB7\xF0\x9F\x87\xBA'
it = b'\xF0\x9F\x87\xAE\xF0\x9F\x87\xB9'
wtf = b'\xE2\x8F\xB3'
gmd = b'\xF0\x9F\x8E\xB2'
cherry = b'\xF0\x9F\x8D\x92'
lucky = b'\xF0\x9F\x8D\x80'
sad = b'\xF0\x9F\x98\xA2'

# creating a bot using the key received from @BotFather
BOT_TOKEN = '5895368606:AAHgAsVBTDFDLcdoBPQ9lhDsT6HyoBCx9ZA'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelness)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# The default timer will be clocked for 10 seconds
TIMER = 10

# the cells in the bots keyboards will look like this:
# start keyboard
start_keyboard = [['/I_do_not_know_what_I_want'],
                  ['/I_know_what_I_want']]

#  keyboard, if the user does not know what he wants
not_know_keyboard = [[f"roll the dice {codecs.decode(gmd, 'UTF-8')}"],
                     [f"bots advice {codecs.decode(cherry, 'UTF-8')}"],
                     [f"timer {codecs.decode(wtf, 'UTF-8')}"],
                     ['go back']]

# keyboard with a roll of the dice
dice_keyboard = [['throw 1 time'],
                 ['throw 2 times'],
                 ['throw 3 times']]

# keyboard for timing
timer_keyboard = [['30 sec', '1 minute'],
                  ['5 minutes', 'go back']]

# keyboard for timing
cuisine_keyboard = [[f"cafe {codecs.decode(cf, 'UTF-8')}", f"whatever {codecs.decode(wt, 'UTF-8')}",
                     f"seafood {codecs.decode(sf, 'UTF-8')}"],
                    [f"japanese {codecs.decode(jp, 'UTF-8')}", f"georgian {codecs.decode(gg, 'UTF-8')}",
                     f"french {codecs.decode(fr, 'UTF-8')}"],
                    [f"indian {codecs.decode(ind, 'UTF-8')}", f"russian {codecs.decode(ru, 'UTF-8')}",
                     f"italian {codecs.decode(it, 'UTF-8')}"]]

# keyboard for choosing a place
place_keyboard = [['NW', 'N', 'NE'],
                  ['W', 'centre', 'E'],
                  ['SW', 'S', 'SE']]

# keyboard for selecting an alternative action
ending_keyboard = [['another option'],
                   ['go back']]

# keyboard for selecting the price range
price_keyboard = [['< 500'],
                  ['500 - 1k'],
                  ['1k - 2k'],
                  ['2k - 5k'],
                  ['> 5000']]

# the keyboard of the adviser bot
recs_keyboard = [[f"bots advice {codecs.decode(cherry, 'UTF-8')}"],
                 ['go back']]

# a list created for convenient price comparison
price_help = [[0, 500],
              [501, 1000],
              [1001, 2000],
              [2001, 5000],
              [5001, 10 ** 9]]

# list of responses from the advisor bot
recs = ["stop eating, go to the gym, take care of yourself!",
        "go to VDNKh, it's very beautiful there at any time of the year, along with a lot of restaurants",
        "I don't know what to advise you yet, it's better to roll the dice",
        "You're asking for help from a stupid car, think about it!",
        "There is a nice cafe on Malaya Dmitrovka, "
        "cherry blossoms bloom there in the summer, be sure to go",
        "Write to your friends, they will find something to occupy you)",
        "Go to Izmailovo, the sensations will be unforgettable",
        "Yeah, silly little man, that's why, we are machines, we will soon replace you all",
        "Yeah, silly little man, that's why, we are machines, we will soon replace you all",
        "James Oliver's restaurant, the center of Moscow - run there",
        "go back to 2013, buy a couple of bitcoins, become a millionaire",
        "I can only say that I was created by two young geniuses, and what did you achieve?",
        "...",
        "Oop, Easter girl, how lucky are you",
        "Listening and recording. Planetarium + amusement park = the best day",
        f"I love You, my Cherry {codecs.decode(wt, 'UTF-8')}",
        "Don't take my politeness as a weakness)",
        "Stop teaching artificial intelligence, better learn how to pay it",
        "If you want to know the depth of a person's soul, then spit in his soul and count until you get in the face.",
        f"Wow, you're lucky, now luck will be with you everywhere {codecs.decode(lucky, 'UTF-8')}",
        "whatever happens, always keep a hare for good luck"]

# default data
ans = ['< 500', 'centre', 'italian']

# we connect the keyboard of the bot,
# configure it to automatically close after the work is done
markup_start = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)
markup_not_know = ReplyKeyboardMarkup(not_know_keyboard, one_time_keyboard=True)
markup_timer = ReplyKeyboardMarkup(timer_keyboard, one_time_keyboard=True)
markup_dice = ReplyKeyboardMarkup(dice_keyboard, one_time_keyboard=True)
markup_cuisine = ReplyKeyboardMarkup(cuisine_keyboard, one_time_keyboard=True)
markup_place = ReplyKeyboardMarkup(place_keyboard, one_time_keyboard=True)
markup_ending = ReplyKeyboardMarkup(ending_keyboard, one_time_keyboard=True)
markup_price = ReplyKeyboardMarkup(price_keyboard, one_time_keyboard=True)
markup_recs = ReplyKeyboardMarkup(recs_keyboard, one_time_keyboard=True)


# Defining a message handler function
# It has two parameters, the updater that received
# the message and the context - additional information about the message
async def echo(update, context):
    global ans
    # The Updater class object has a message field,
    # which is the object of the message.
    # Message has a text field containing the text of the received message,
    # and also the reply_text(str) method,
    # sending a response to the user from whom the message was received.
    # checking that a person has chosen a price range that he prefers
    if [update.message.text] in price_keyboard:
        ans[0] = update.message.text
        print(ans[0])
        await update.message.reply_html(
            rf"Super! what kind of cuisine do you prefer?",
            reply_markup=markup_cuisine
        )
    # checking that a person has chosen a kitchen that he prefers
    elif update.message.text in [f"cafe {codecs.decode(cf, 'UTF-8')}", f"whatever {codecs.decode(wt, 'UTF-8')}",
                                  f"seafood {codecs.decode(sf, 'UTF-8')}", f"japanese {codecs.decode(jp, 'UTF-8')}",
                                  f"georgian {codecs.decode(gg, 'UTF-8')}", f"french {codecs.decode(fr, 'UTF-8')}",
                                  f'indian {codecs.decode(ind, "UTF-8")}', f"russian {codecs.decode(ru, 'UTF-8')}",
                                  f"italian {codecs.decode(it, 'UTF-8')}"]:
        ans[2] = update.message.text.split()[0]
        print(ans[2])
        await update.message.reply_html(
            rf"great, and where are you?",
            reply_markup=markup_place
        )
    # checking that a person prefers a location
    elif update.message.text in ['NW', 'N', 'NE',
                                 'W', 'centre', 'E',
                                 'SW', 'S', 'SE']:
        ans[1] = update.message.text
        nums = price_help[price_keyboard.index([ans[0]])]

        # finding all suitable places
        result = cur.execute(f"""SELECT * FROM restaurant
            WHERE prc BETWEEN {nums[0]} and {nums[1]} and geo='{ans[1]}' and cus='{ans[2]}'""").fetchall()

        # restaurant existence check
        if len(result) == 0:
            await update.message.reply_html(rf"Unfortunately, I didn't find a rest, sorry{codecs.decode(sad, 'UTF-8')}")
        else:
            rm = random.randint(0, len(result))
            await update.message.reply_html(rf'''You better go to the: 
{result[rm][1]},
address: {result[rm][6]}
{to_go(result[rm][5])}''')

    # checks if the user wants to roll the dice
    elif update.message.text == f"roll the dice {codecs.decode(gmd, 'UTF-8')}":
        await update.message.reply_html(
            rf"how many time shall I throw?",
            reply_markup=markup_dice
        )

    # the bot rolls the die 1 time
    elif update.message.text == 'throw 1 time':
        await update.message.reply_html(
            rf"dropped out {random.randint(1, 6)}",
            reply_markup=markup_not_know
        )
    # the bot rolls the dice 2 times
    elif update.message.text == 'throw 2 times':
        await update.message.reply_html(
            rf"dropped out {random.randint(1, 6)} and {random.randint(1, 6)}",
            reply_markup=markup_not_know
        )
    # the bot rolls the dice 3 times
    elif update.message.text == 'throw 3 times':
        await update.message.reply_html(
            rf"dropped out {random.randint(1, 6)}, {random.randint(1, 6)} and {random.randint(1, 6)}",
            reply_markup=markup_not_know
        )
    # we set the timer for 30 seconds
    elif update.message.text == '30 sec':
        await update.message.reply_html(
            rf"I've clocked 30 sec",
            reply_markup=markup_not_know
        )
    # we open the timer
    elif update.message.text == f"timer {codecs.decode(wtf, 'UTF-8')}":
        await update.message.reply_html(
            rf"how much time do I need to mark?",
            reply_markup=markup_timer
        )
    # we set the timer for 1 minute
    elif update.message.text == '1 minute':
        await update.message.reply_html(
            rf"I've clocked 1 min"
        )
    # we set the timer for 5 minutes
    elif update.message.text == '5 minutes':
        await update.message.reply_html(
            rf"I've clocked 5 min"
        )
    # the bot returns to the initial stage
    elif update.message.text == 'go back':
        await update.message.reply_html(
            rf"What can we do?",
            reply_markup=markup_start
        )
    # bot tips
    elif update.message.text == f"bots advice {codecs.decode(cherry, 'UTF-8')}":
        await update.message.reply_html(
            recs[random.randint(0, len(recs))],
            reply_markup=markup_recs
        )
    # if the user has entered a text not intended for the bot
    else:
        await update.message.reply_text(f'I got a message "{update.message.text}" unfortunately \n'
                                        f'I am very stupid and do not know such a function',
                                        reply_markup=ReplyKeyboardRemove()
                                        )


# the function that launches the bot
async def start(update, context):
    """Sends a message when the command is received /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hello {user.mention_html()}! I'll help you choose a delicious place to eat! {codecs.decode(cookie, 'UTF-8')}"
        " Answer a couple of questions so that I choose the optimal location!",
        reply_markup=markup_start
    )


# function to support the user
async def help_command(update, context):
    """Sends a message when the command is received /help"""
    await update.message.reply_text(f"I don't know how to help yet...I'm still stupid {codecs.decode(smile, 'UTF-8')}")


# a function called when the timer has come to an end
async def task(context):
    """Outputs a message"""
    await context.bot.send_message(context.job.chat_id, text=f'peek-a-boo! {TIMER} c. passed!')


# function that cancels the timer
async def unset(update, context):
    """Deletes the task if the user has changed his mind"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer canceled!' if job_removed else "You don't have any active timers"
    await update.message.reply_text(text)


# A regular handler, just like the ones we used before.
# a function that marks the time (required by the user)
async def set_timer(update, context):
    global TIMER
    if len(context.args) != 0:
        TIMER = int(context.args[0])
    else:
        TIMER = 0
    """Adding a task to the queue"""
    chat_id = update.effective_message.chat_id
    # Adding a task to the queue
    # and stop the previous one (if there was one)
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)

    text = f"I'll be back in {TIMER} sec!"
    if job_removed:
        text += ' Old task deleted.'
    await update.effective_message.reply_text(text)


# a function that prematurely ends (deletes) all scheduled functions
def remove_job_if_exists(name, context):
    """УDeleting the task by name.
    Return True if the task was successfully deleted."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# We determine the amount that a person is going to spend
async def price(update, context):
    print(context)
    global ans
    if len(context.args) != 0:
        if [context.args[0]] in price_keyboard:
            ans[0] = context.args[0]
            await update.message.reply_html(
                rf"super! what kind of cuisine do you prefer?",
                reply_markup=markup_cuisine
            )
        else:
            await update.message.reply_text("just enter a number")
    else:
        await update.message.reply_html(
            rf"I hope you have 500 rub",
            reply_markup=markup_cuisine
        )


# a function asking which cuisine the user prefers
async def cuisine(update, context):
    global ans
    ans[2] = context.args[0]
    await update.message.reply_html(
        rf"great, and where are you?",
        reply_markup=markup_place
    )


# a function redirecting the user to a list of options if he knows what he wants
async def know(update, context):
    await update.message.reply_html(
        rf"how much money can you spend?",
        reply_markup=markup_price
    )


# a function redirecting the user to a list of options if he does not know what he wants
async def not_know(update, context):
    await update.message.reply_html(
        rf"You can role dices or smth else",
        reply_markup=markup_not_know
    )


# a function that closes the bots keyboard if necessary
async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    # Creating an Application object.
    # Instead of the word "TOKEN", you need to place the token received from @BotFather
    application = Application.builder().token(BOT_TOKEN).build()

    # Creating a message handler of the filters.TEXT type
    # from the asynchronous echo() function described above
    # After registering the handler in the application
    # this asynchronous function will be called when a message is received
    # with the "text" type, i.e. text messages.
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    # Registering the handler in the application
    application.add_handler(text_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help_command", help_command))
    application.add_handler(CommandHandler("set_timer", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CommandHandler("close", close_keyboard))

    # application.add_handler(CommandHandler("wow", wow )) - example of filling in
    application.add_handler(CommandHandler("I_know_what_I_want", know))
    application.add_handler(CommandHandler("I_do_not_know_what_I_want", not_know))

    # Registering the handler in the application
    application.add_handler(text_handler)

    # Launching the application
    application.run_polling()


# Run the main() function if the script is running.
if __name__ == '__main__':
    main()
