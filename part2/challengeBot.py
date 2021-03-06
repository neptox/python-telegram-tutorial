import json
import requests
import urllib
import datetime
import time
import config
from dbhelper import DBHelper

db = DBHelper()

#-----------------------

# set arguments for Telegram bot: @ChaIIengeBot
TOKEN = config.token
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
END = "26.07.18"
DAYS_LEFT = 0
COMMAND = ""

#-----------------------

newRulesComing = False
newNavElementsComing = False

#function push and pull Telegram bot api
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

#function get json from ap request
def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

#function get updates from bot
def get_updates(offset=None):
    #url = URL + "getUpdates?timeout=100"
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

#function asks for latest update in group
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

#handle updates
def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            rules = db.get_rules(chat)
            nav = db.get_nav(chat)
            if text == "/keyboard":
                keyboard = build_keyboard(nav)
                send_message("What to do?", chat, keyboard)
            elif text == "/rules":
                #test = [[rule] for rule in rules]
                rules = db.get_rules(chat)
                message = "\n".join(rules)
                send_message("Here are your rules: " + message, chat)
            elif text == "/setrules":
                newRulesComing = True
                print(newRulesComing)
                send_message("Welcome! Please tell me each rule as a single message and then type /done", chat)

            elif newRulesComing == True:
                print("test")
                db.add_rule(text, chat)
                send_message("Ok, type another one or /done", chat)

            elif text == "/done":
                newRulesComing = False
                #newNavElementsComing = False
                send_message("Perfect, thank you!", chat)

            elif text == "/setend":
                send_message("Which will be the last day of this challenge (dd.mm.yy): ", chat)

                send_message("Ok this challenge will go until: " + text, chat)
            elif text == "/setnav":
                send_message("Welcome! Please tell me each /command as a single message", chat)

            elif text.startswith("/"):
                db.add_nav(text, chat)
                #continue
            elif text in nav:
                #db.delete_nav(text, chat)
                nav = db.get_nav(chat)
                keyboard = build_keyboard(nav)
                send_message("Select a command", chat, keyboard)
            #else:
        except KeyError:
            pass

"""

#function to reply all messages
def echo_all(updates):
       for update in updates["result"]:
               try:
                       text = update["message"]["text"]
                       send_message(text)
               except Exception as e:
                       print(e)

"""

#function asks for text in group chat
def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

# function label keys in Telegram
def build_keyboard(rules):
    keyboard = [[rule] for rule in rules]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


#----------------------

#function remaining days in challenge
def days_until():
        today = datetime.datetime.today()
        end = datetime.datetime.strptime(END, "%d.%m.%y")
        delta = today - end

        if delta.days >= 0:
                left = 0
        else:
                left = delta.days

        return(abs(left))


#function concatenate api url
def set_chat_title(updates, text):
        for update in updates["result"]:
            chat = update["message"]["chat"]["id"]
        days_left = days_until()
        title = str(days_left) + " Tage – " + text
        title = urllib.parse.quote_plus(title)
        url = URL + "setChatTitle?chat_id={}&title={}".format(chat, title)
        get_url(url) #push api request
        print(url)

#-------------------

#function main
def main():
    db.setup()
    last_update_id = None
    daycount = days_until() + 1
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
            print("getting updates")

        DAYS_LEFT = days_until()
        if  DAYS_LEFT < daycount:
            print("counting days:")
            set_chat_title(updates, "Tu Dir Was Gutes")
            daycount = DAYS_LEFT
        time.sleep(1)


if __name__ == '__main__':
        main()
