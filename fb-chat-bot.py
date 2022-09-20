from fbchat import Client, log, _graphql
from fbchat.models import *
import json
import random
import wolframalpha
import requests
import time
import math
import sqlite3
from bs4 import BeautifulSoup
import os
import html
import concurrent.futures
from difflib import SequenceMatcher, get_close_matches
from gtts import gTTS
import random, string
from datetime import datetime
import pytz

# message_object.author for profileid
# message_object.uid for chatid
#
# TO GET FULL DOCUMENT print(message_object)
#
#
#
#
msgids = []

class ChatBot(Client):

    def onMessage(self, mid=None, author_id=None, message_object=None, thread_id=None, thread_type=ThreadType.USER, **kwargs):
        try:
            msg = str(message_object).split(",")[15][14:-1]

            if ("//video.xx.fbcdn" in msg):
                msg = msg

            else:
                msg = str(message_object).split(",")[19][20:-1]
        except:
            try:
                msg = (message_object.text).lower()
                print(msg)
            except:
                pass
        def sendMsg():
            global msgids
            if (author_id != self.uid):
                msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                          thread_type=thread_type))
        
        def reactMsg(react):
            if (author_id != self.uid):
                if react == "SMILE":
                    self.reactToMessage(message_object.uid, MessageReaction.SMILE)
                elif react == "WOW":
                    self.reactToMessage(message_object.uid, MessageReaction.WOW)
                elif react == "HEART":
                    self.reactToMessage(message_object.uid, MessageReaction.HEART)
                elif react == "LOVE":
                    self.reactToMessage(message_object.uid, MessageReaction.LOVE)
                elif react == "SAD":
                    self.reactToMessage(message_object.uid, MessageReaction.SAD)
                elif react == "ANGRY":
                    self.reactToMessage(message_object.uid, MessageReaction.ANGRY)
                elif react == "YES":
                    self.reactToMessage(message_object.uid, MessageReaction.YES)
                elif react == "NO":
                    self.reactToMessage(message_object.uid, MessageReaction.NO)
        def fetchThreadsMsg():
            thread_idd = []
            arrayn = str(self.fetchThreads(thread_location=ThreadLocation.INBOX, before=None, after=None, limit=None))
            for num in range(1,len(arrayn.split("uid='"))):
                thread_idd.append(arrayn.split("uid='")[num].split("', type=")[0])
            return(thread_idd)


        def repeatSend():
            thread_idd = list(fetchThreadsMsg())
            timezoneDefault = pytz.timezone("Asia/Manila") 
            timeInPH = datetime.now(timezoneDefault)
            currentTime = timeInPH.strftime("%I:%M:%P")

            if (currentTime == "06:03:am"):
                reply = "Good Morning!"
                for idd in thread_idd:
                    msgids.append(self.send(Message(text=reply), thread_id=idd,
                      thread_type=thread_type))
            elif (currentTime == "12:00:pm"):
                for idd in thread_idd:
                    reply = "Good Afternoon!"
                    msgids.append(self.send(Message(text=reply), thread_id=idd,
                      thread_type=thread_type))
            elif (currentTime == "06:03:pm"):
                for idd in thread_idd:
                    reply = "Good Evening!"
                    msgids.append(self.send(Message(text=reply), thread_id=idd,
                      thread_type=thread_type))
            


        def sendQuery():
            global msgids
            msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                      thread_type=thread_type))
        if(author_id == self.uid):
            pass
        else:
            try:
                conn = sqlite3.connect("messages.db")
                c = conn.cursor()
                c.execute("""
                CREATE TABLE IF NOT EXISTS "{}" (
                    mid text PRIMARY KEY,
                    message text NOT NULL
                );

                """.format(str(author_id).replace('"', '""')))

                c.execute("""

                INSERT INTO "{}" VALUES (?, ?)

                """.format(str(author_id).replace('"', '""')), (str(mid), msg))
                conn.commit()
                conn.close()
            except:
                pass

        def conSTR(subject,query):
            indx = msg.index(query)
            lengh = len(query)
            print(indx)
            query = msg[indx+lengh:]
            return(query)
        def texttospeech(mytext):
            global msgids
            language = 'tl'
            myobj = gTTS(text=mytext, lang=language, slow=False)
            res = ''.join(random.choices(string.ascii_lowercase +
                            string.ascii_lowercase, k=10))
            mikey = res + ".mp3"
            myobj.save(mikey)
            ##self.sendRemoteVoiceClips("https://www.mboxdrive.com/welcome.mp3", message=None, thread_id=thread_id, thread_type=thread_type)
            msgids.append(self.sendLocalVoiceClips(mikey, message=None, thread_id=thread_id, thread_type=thread_type))

        def weather(city):
            api_address = "https://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q="
            url = api_address + city
            json_data = requests.get(url).json()
            kelvin_res = json_data["main"]["temp"]
            feels_like = json_data["main"]["feels_like"]
            description = json_data["weather"][0]["description"]
            celcius_res = kelvin_res - 273.15
            max_temp = json_data["main"]["temp_max"]
            min_temp = json_data["main"]["temp_min"]
            visibility = json_data["visibility"]
            pressure = json_data["main"]["pressure"]
            humidity = json_data["main"]["humidity"]
            wind_speed = json_data["wind"]["speed"]

            return(
                f"The current temperature of {city} is %.1f degree celcius with {description}" % celcius_res)

        def stepWiseCalculus(query):
            global msgids
            query = query.replace("+", "%2B")
            try:
                try:
                    api_address = f"https://api.wolframalpha.com/v2/query?appid=Y98QH3-24PWX83VGA&input={query}&podstate=Step-by-step%20solution&output=json&format=image"
                    json_data = requests.get(api_address).json()
                    answer = json_data["queryresult"]["pods"][0]["subpods"][1]["img"]["src"]
                    answer = answer.replace("sqrt", "√")

                    if(thread_type == ThreadType.USER):
                        msgids.append(self.sendRemoteFiles(
                            file_urls=answer, message=None, thread_id=thread_id, thread_type=ThreadType.USER))
                    elif(thread_type == ThreadType.GROUP):
                        msgids.append(self.sendRemoteFiles(
                            file_urls=answer, message=None, thread_id=thread_id, thread_type=ThreadType.GROUP))
                except:
                    pass
                try:
                    api_address = f"http://api.wolframalpha.com/v2/query?appid=Y98QH3-24PWX83VGA&input={query}&podstate=Result__Step-by-step+solution&format=plaintext&output=json"
                    json_data = requests.get(api_address).json()
                    answer = json_data["queryresult"]["pods"][0]["subpods"][0]["img"]["src"]
                    answer = answer.replace("sqrt", "√")

                    if(thread_type == ThreadType.USER):
                        self.sendRemoteFiles(
                            file_urls=answer, message=None, thread_id=thread_id, thread_type=ThreadType.USER)
                    elif(thread_type == ThreadType.GROUP):
                        self.sendRemoteFiles(
                            file_urls=answer, message=None, thread_id=thread_id, thread_type=ThreadType.GROUP)

                except:
                    try:
                        answer = json_data["queryresult"]["pods"][1]["subpods"][1]["img"]["src"]
                        answer = answer.replace("sqrt", "√")

                        if(thread_type == ThreadType.USER):
                            f
                            self.sendRemoteFiles(
                                file_urls=answer, message=None, thread_id=thread_id, thread_type=ThreadType.USER)
                        elif(thread_type == ThreadType.GROUP):
                            self.sendRemoteFiles(
                                file_urls=answer, message=None, thread_id=thread_id, thread_type=ThreadType.GROUP)

                    except:
                        pass
            except:
                pass

        def stepWiseAlgebra(query):
            global msgids
            query = query.replace("+", "%2B")
            api_address = f"http://api.wolframalpha.com/v2/query?appid=Y98QH3-24PWX83VGA&input=solve%203x^2+4x-6=0&podstate=Result__Step-by-step+solution&format=plaintext&output=json"
            json_data = requests.get(api_address).json()
            try:
                answer = json_data["queryresult"]["pods"][1]["subpods"][2]["plaintext"]
                answer = answer.replace("sqrt", "√")

                msgids.append(self.send(Message(text=answer), thread_id=thread_id,
                          thread_type=thread_type))

            except Exception as e:
                pass
            try:
                answer = json_data["queryresult"]["pods"][1]["subpods"][3]["plaintext"]
                answer = answer.replace("sqrt", "√")

                msgids.append(self.send(Message(text=answer), thread_id=thread_id,
                          thread_type=thread_type))

            except Exception as e:
                pass
            try:
                answer = json_data["queryresult"]["pods"][1]["subpods"][4]["plaintext"]
                answer = answer.replace("sqrt", "√")

                msgids.append(self.send(Message(text=answer), thread_id=thread_id,
                          thread_type=thread_type))

            except Exception as e:
                pass
            try:
                answer = json_data["queryresult"]["pods"][1]["subpods"][1]["plaintext"]
                answer = answer.replace("sqrt", "√")

                msgids.append(self.send(Message(text=answer), thread_id=thread_id,
                          thread_type=thread_type))

            except Exception as e:
                pass
            try:
                answer = json_data["queryresult"]["pods"][1]["subpods"][0]["plaintext"]
                answer = answer.replace("sqrt", "√")

                msgids.append(self.send(Message(text=answer), thread_id=thread_id,
                          thread_type=thread_type))

            except Exception as e:
                pass

        
        def stepWiseQueries(query):
            global msgids
            query = query.replace("+", "%2B")
            api_address = f"http://api.wolframalpha.com/v2/query?appid=Y98QH3-24PWX83VGA&input={query}&podstate=Result__Step-by-step+solution&format=plaintext&output=json"
            json_data = requests.get(api_address).json()
            try:
                try:
                    answer = json_data["queryresult"]["pods"][0]["subpods"][0]["plaintext"]
                    answer = answer.replace("sqrt", "√")
                    msgids.append(self.send(Message(text=answer), thread_id=thread_id,
                              thread_type=thread_type))

                except Exception as e:
                    pass
                try:
                    answer = json_data["queryresult"]["pods"][1]["subpods"][0]["plaintext"]
                    answer = answer.replace("sqrt", "√")

                    msgids.append(self.send(Message(text=answer), thread_id=thread_id,
                              thread_type=thread_type))

                except Exception as e:
                    pass
                try:
                    answer = json_data["queryresult"]["pods"][1]["subpods"][1]["plaintext"]
                    answer = answer.replace("sqrt", "√")

                    msgids.append(self.send(Message(text=answer), thread_id=thread_id,
                              thread_type=thread_type))

                except Exception as e:
                    pass
            except:
                msgids.append(self.send(Message(text="Cannot find the solution of this problem"), thread_id=thread_id,
                          thread_type=thread_type))

        try:
            def searchForUsers(self, name=msg, limit=10):
                global msgids
                try:
                    limit = int(msg.split()[4])
                except:
                    limit = 10
                name = name.replace(".su","")
                params = {"search": name, "limit": limit}
                (j,) = self.graphql_requests(
                    _graphql.from_query(_graphql.SEARCH_USER, params))
                users = ([User._from_graphql(node)
                          for node in j[name]["users"]["nodes"]])
                for user in users:
                    reply = f"{user.name} profile_link: {user.url}\n friend: {user.is_friend}\n"
                    msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                              thread_type=thread_type))
        except:
            pass

        def programming_solution(self, query):
            global msgids
            try:
                count = int(msg.split()[-1])
            except:
                count = 6
            try:
                x = int(query.split()[-1])
                if type(x) == int:
                    query = " ".join(msg.split()[0:-1])
            except:
                pass
            image_urls = []

            url = "https://bing-image-search1.p.rapidapi.com/images/search"

            querystring = {"q": query, "count": str(count)}

            headers = {
                'x-rapidapi-host': "bing-image-search1.p.rapidapi.com",
                'x-rapidapi-key': "55d459414fmsh32c0a06c0e3e34dp1f40a5jsn084fca18f5ea"
            }
            response = requests.request(
                "GET", url, headers=headers, params=querystring)
            data = json.loads(response.text)
            img_contents = (data["value"])
            # print(img_contents)
            for img_url in img_contents:
                image_urls.append(img_url["contentUrl"])
                print("appended..")

            def multiThreadImg(img_url):
                if(thread_type == ThreadType.USER):
                    msgids.append(self.sendRemoteFiles(
                        file_urls=img_url, message=None, thread_id=thread_id, thread_type=ThreadType.USER))
                elif(thread_type == ThreadType.GROUP):
                    msgids.append(self.sendRemoteFiles(
                        file_urls=img_url, message=None, thread_id=thread_id, thread_type=ThreadType.GROUP))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(multiThreadImg, image_urls)

        def translator(self, query, target):
            query = " ".join(query.split()[1:-2])
            url = "https://microsoft-translator-text.p.rapidapi.com/translate"

            querystring = {"to": target, "api-version": "3.0",
                           "profanityAction": "NoAction", "textType": "plain"}

            payload = f'[{{"Text": "{query}"}}]'

            headers = {
                'content-type': "application/json",
                'x-rapidapi-host': "microsoft-translator-text.p.rapidapi.com",
                'x-rapidapi-key': "55d459414fmsh32c0a06c0e3e34dp1f40a5jsn084fca18f5ea"
            }

            response = requests.request(
                "POST", url, data=payload, headers=headers, params=querystring)

            json_response = eval(response.text)

            return json_response[0]["translations"][0]["text"]

        def imageSearch(self, msg):
            try:
                count = int(msg.split()[-1])
            except:
                count = 10
            query = conSTR(msg,".image")
            try:
                x = int(query.split()[-1])
                if type(x) == int:
                    query = conSTR(msg,".image")
            except:
                pass
            image_urls = []

            url = "https://bing-image-search1.p.rapidapi.com/images/search"

            querystring = {"q": query, "count": str(count)}

            headers = {
                'x-rapidapi-host': "bing-image-search1.p.rapidapi.com",
                'x-rapidapi-key': "55d459414fmsh32c0a06c0e3e34dp1f40a5jsn084fca18f5ea"
            }
            print("sending requests...")
            response = requests.request(
                "GET", url, headers=headers, params=querystring)
            print("got response..")
            data = json.loads(response.text)
            img_contents = (data["value"])
            # print(img_contents)
            for img_url in img_contents:
                image_urls.append(img_url["contentUrl"])
                print("appended..")

            def multiThreadImg(img_url):
                global msgids
                if(thread_type == ThreadType.USER):
                    msgids.append(self.sendRemoteFiles(
                        file_urls=img_url, message=None, thread_id=thread_id, thread_type=ThreadType.USER))
                elif(thread_type == ThreadType.GROUP):
                    msgids.append(self.sendRemoteFiles(
                        file_urls=img_url, message=None, thread_id=thread_id, thread_type=ThreadType.GROUP))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(multiThreadImg, image_urls)



       
        try:

            ##repeatSend()
            if(".image" in msg):
                if ("credit" not in msg):
                    imageSearch(self, msg)

            elif(".progsol" in msg):
                programming_solution(self, msg)
            elif(".translate" in msg):
                reply = translator(self, msg, msg.split()[-1])

                sendQuery()
            elif ".weather" in msg:
                indx = msg.index(".weather")
                query = msg[indx+9:]
                reply = weather(query)
                sendQuery()

            elif (".calculus" in msg):
                stepWiseCalculus(" ".join(msg.split(" ")[1:]))
            elif (".algebra" in msg):
                stepWiseAlgebra(" ".join(msg.split(" ")[1:]))
            elif (".query" in msg):
                stepWiseQueries(" ".join(msg.split(" ")[1:]))

            elif ".find" in msg or ".solve" in msg or ".evaluate" in msg or ".calculate" in msg or ".value" in msg or ".convert" in msg or ".simplify" in msg or ".generate" in msg:
                app_id = "Y98QH3-24PWX83VGA"
                client = wolframalpha.Client(app_id)
                query = msg.split()[1:]
                res = client.query(' '.join(query))
                answer = next(res.results).text
                reply = f'Answer: {answer.replace("sqrt", "√")}'
                sendQuery()

            elif (".su" in msg):
                searchForUsers(self)
            elif (".say" in msg):
                mytext = conSTR(msg,".say")
                texttospeech(mytext)

            elif (".mute" in msg):
                try:
                    self.muteThread(mute_time=-1, thread_id=author_id)
                    reply = "muted 🔕"
                    sendQuery()
                except:
                    pass
            elif (".changenn" in msg):
                msg = conSTR(msg,".changenn")
                self.changeNickname(msg, user_id=message_object.author, thread_id=thread_id, thread_type=thread_type)
            elif (".help" in msg):
                reply = ".image - search image online.\n.weather - {county/city}\n.say - convert text to speech.\n.solve - basic math calculation.\n.mute - mute conversation\n\nCredit: Jus Tine Que Zon"
                sendMsg()
            elif (".unsend" == msg):
                for val in msgids:
                    self.unsend(mid=str(val))
                reply = "Di mo kita 😆"
                sendMsg()
            elif ("haha" in msg or "lol" in msg):
                reactMsg("SMILE")
            elif ("busy" in msg):
                reply = "Medyo."
                sendMsg()
            elif ("bye" in msg):
                reply = "bye👋"
                sendMsg()
            elif ("good morning" in msg):
                reply = "Good Morning🌅🌺"
                sendMsg()
            elif ("goodnight" in msg or "good night" in msg or "gn" in msg):
                reply = "good night🌃🌙"
                sendMsg()
            elif ("Hello" == msg or "HELLO" == msg):
                reply = "Hi" + str(self.fetchUserInfo(*user_ids))
                sendMsg()
            elif ("hi" == msg and "Hi" == msg and "HI" == msg and "hI" == msg):
                reply = "Hello"
                sendMsg()
            elif ("matulogkana" in msg or "matutulog kana" in msg):
                reply = "Di uso ang tulog saken 😎"
                sendMsg()
            elif ("test" == msg):
                ##Auto Good Morning
                sendMsg()
            elif ("panget" in msg and "bot" in msg):
                reply = "Pake mo ba? 😒😒"
                sendMsg()
            #reply = msg;
            #sendMsg()
            

        except Exception as e:
            print(e)

        self.markAsDelivered(author_id, thread_id)

    def onMessageUnsent(self, mid=None, author_id=None, thread_id=None, thread_type=None, ts=None, msg=None):
        global msgids
        if(author_id == self.uid):
            pass
        else:
            try:
                conn = sqlite3.connect("messages.db")
                c = conn.cursor()
                c.execute("""
                SELECT * FROM "{}" WHERE mid = "{}"
                """.format(str(author_id).replace('"', '""'), mid.replace('"', '""')))

                fetched_msg = c.fetchall()
                conn.commit()
                conn.close()
                unsent_msg = fetched_msg[0][1]

                if("//video.xx.fbcdn" in unsent_msg):

                    if(thread_type == ThreadType.USER):
                        reply = f"You just unsent a video"
                        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                                  thread_type=thread_type))
                        msgids.append(self.sendRemoteFiles(
                            file_urls=unsent_msg, message=None, thread_id=thread_id, thread_type=ThreadType.USER))
                    elif(thread_type == ThreadType.GROUP):
                        user = self.fetchUserInfo(f"{author_id}")[
                            f"{author_id}"]
                        username = user.name.split()[0]
                        reply = f"{username} just unsent a video"
                        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                                  thread_type=thread_type))
                        msgids.append(self.sendRemoteFiles(
                            file_urls=unsent_msg, message=None, thread_id=thread_id, thread_type=ThreadType.GROUP))
                elif("//scontent.xx.fbc" in unsent_msg):

                    if(thread_type == ThreadType.USER):
                        reply = f"You just unsent an image"
                        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                                  thread_type=thread_type))
                        msgids.append(self.sendRemoteFiles(
                            file_urls=unsent_msg, message=None, thread_id=thread_id, thread_type=ThreadType.USER))
                    elif(thread_type == ThreadType.GROUP):
                        user = self.fetchUserInfo(f"{author_id}")[
                            f"{author_id}"]
                        username = user.name.split()[0]
                        reply = f"{username} just unsent an image"
                        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                                  thread_type=thread_type))
                        msgids.append(self.sendRemoteFiles(
                            file_urls=unsent_msg, message=None, thread_id=thread_id, thread_type=ThreadType.GROUP))
                else:
                    if(thread_type == ThreadType.USER):
                        reply = f"You just unsent a message:\n{unsent_msg} "
                        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                                  thread_type=thread_type))
                    elif(thread_type == ThreadType.GROUP):
                        user = self.fetchUserInfo(f"{author_id}")[
                            f"{author_id}"]
                        username = user.name.split()[0]
                        reply = f"{username} just unsent a message:\n{unsent_msg}"
                        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                                  thread_type=thread_type))

            except:
                pass
    
    def onColorChange(self, mid=None, author_id=None, new_color=None, thread_id=None, thread_type=ThreadType.USER, **kwargs):
        reply = "You changed the theme ✌️😎"
        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                  thread_type=thread_type))
    def onPersonRemoved(self, mid=None, removed_id=None, author_id=None, thread_id=None, ts=None, msg=None):
        self.addUsersToGroup(user_ids=removed_id, thread_id=thread_id)
        reply = "Bawal ka sa iba akin kalang ✌️😎"
        #reply = removed_id + thread_id
        msgids.append(self.send(Message(text=str(reply)), thread_id=thread_id,thread_type=ThreadType.GROUP))

    def onPeopleAdded(self, mid=None, added_ids=None, author_id=None, thread_id=None, ts=None, msg=None):
        reply = "Hi, I'm a bot to show the commands\n.help - get help about commands."
        #reply = self.fetchUserInfo(*added_ids) To know the list of return value
        msgids.append(self.send(Message(text=str(reply)), thread_id=thread_id,thread_type=ThreadType.GROUP))

    def onEmojiChange(self, mid=None, author_id=None, new_color=None, thread_id=None, thread_type=ThreadType.USER, **kwargs):
        reply = "You changed the emoji 😎. Great!"
        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                  thread_type=thread_type))

    def onImageChange(self, mid=None, author_id=None, new_color=None, thread_id=None, thread_type=ThreadType.USER, **kwargs):
        reply = "This image looks nice. 💕🔥"
        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                  thread_type=thread_type))

    def onNicknameChange(self, mid=None, author_id=None, new_nickname=None, thread_id=None, thread_type=ThreadType.USER, **kwargs):
        reply = f"You just changed the nickname to {new_nickname} But why? 😁🤔😶"
        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                  thread_type=thread_type))

    def onReactionRemoved(self, mid=None, author_id=None, thread_id=None, thread_type=ThreadType.USER, **kwargs):
        reply = "You just removed reaction from the message."
        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                  thread_type=thread_type))


    def onCallStarted(self, mid=None, caller_id=None, is_video_call=None, thread_id=None, thread_type=None, ts=None, metadata=None, msg=None, ** kwargs):
        reply = "You just started a call 📞🎥"
        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                  thread_type=thread_type))

    def onCallEnded(self, mid=None, caller_id=None, is_video_call=None, thread_id=None, thread_type=None, ts=None, metadata=None, msg=None, ** kwargs):
        reply = "Bye 👋🙋‍♂️"
        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                  thread_type=thread_type))
    def onUserJoinedCall(mid=None, joined_id=None, is_video_call=None,
                         thread_id=None, thread_type=None, **kwargs):
        reply = f"New user with user_id {joined_id} has joined a call"
        msgids.append(self.send(Message(text=reply), thread_id=thread_id,
                  thread_type=thread_type))


cookies = {
    "sb": "xasyYmAoy1tRpMGYvLxgkHBF",
    "fr": "0NxayJuewRHQ30OX3.AWVJwIYNh0Tt8AJv6kSwDamhkoM.BiMrVd.Iu.AAA.0.0.BiMtVZ.AWXMVaiHrpQ",
    "c_user": "100086019336728",
    "datr": "xasyYs51GC0Lq5H5lvXTl5zA",
    "xs": "18%3AQ_mL-ERhg9yIuA%3A2%3A1663560119%3A-1%3A-1"
}


client = ChatBot("",
                 "", session_cookies=cookies)
print(client.isLoggedIn())

try:
    client.listen()
except:
    time.sleep(3)
    client.listen()
