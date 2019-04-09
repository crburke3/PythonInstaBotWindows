from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin
from enum import Enum
from time import sleep


class ManagementLocations(Enum):
    email = "email_verification"
    phone = "phone_verification"
    verifier = "verifier_text"
    verifier_method = "verifier_method"


class Fire:
    db = ""
    bot = ""
    watcher = ""

    def on_verifier_snapshot(self, doc_snapshot, changes, read_time):
        values = self.get_management_values()
        if values[ManagementLocations.verifier_method.value] != "":
            verifier_method = values[ManagementLocations.verifier_method.value]
            self.bot.__verifier_click__(verifier_method)  # click the correct method
            self.set_management_value(ManagementLocations.verifier_method, "")  # set it to empty after login
        if values[ManagementLocations.email.value] != "":
            # User has entered the email verification Code
            print("Receieved Email verification Code: " + values[ManagementLocations.email.value])
            self.set_management_value(ManagementLocations.email, "")  # set it to empty after login
        if values[ManagementLocations.phone.value] != "":
            # User has entered the Text verification Code
            phone_value = values[ManagementLocations.phone.value]
            print("Recieved Text verification Code: " + phone_value)
            self.bot.__verifier_code_enter__(phone_value)
            self.set_management_value(ManagementLocations.phone, "")  # set it to empty after login

    def __init__(self, bot):
        cred = credentials.Certificate('instabot-bee53-firebase-adminsdk-uuob3-43254d1074.json')
        firebase_admin.initialize_app(cred, {
          'projectId': "instabot-bee53",
        })
        self.db = firestore.client()
        self.bot = bot
        self.watcher = self.db.collection(bot.username).document(u'management').on_snapshot(self.on_verifier_snapshot)

    def set_whitelist(self, users: [str]):
        user_dict = {"users": users}
        if not self.db.collection(self.bot.username).document(u'whitelist').get().exists:
            self.db.collection(self.bot.username).document(u'whitelist').set(user_dict)
        else:
            self.db.collection(self.bot.username).document(u'whitelist').update(user_dict)

    def get_whitelist(self)->[str]:
        users = self.db.collection(self.bot.username).document(u'whitelist').get().to_dict()
        return users["users"]

    def set_post_queue(self, post_list: [str]):
        post_dict = {"posts": post_list}
        if not self.db.collection(self.bot.username).document(u'post_queue').get().exists:
            self.db.collection(self.bot.username).document(u'post_queue').set(post_dict)
        else:
            self.db.collection(self.bot.username).document(u'post_queue').update(post_dict)

    def get_post_queue(self)->[str]:
        users = self.db.collection(self.bot.username).document(u'post_queue').get().to_dict()
        return users["posts"]

    def remove_from_queue(self, post_link: str):
        curr_queue: [str] = self.get_post_queue()
        for i in range(curr_queue.count(post_link)): curr_queue.remove(post_link)  # filter
        self.set_post_queue(curr_queue)

    def set_management_value(self, case: ManagementLocations, text: str):
        post_dict = {str(case.value): text}
        if not self.db.collection(self.bot.username).document(u'management').get().exists:
            self.db.collection(self.bot.username).document(u'management').set(post_dict)
        else:
            self.db.collection(self.bot.username).document(u'management').update(post_dict)

    def get_management_values(self)->dict:
        values = self.db.collection(self.bot.username).document(u'management').get().to_dict()
        return values