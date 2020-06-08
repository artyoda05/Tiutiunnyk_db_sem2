import redis
from random import randint
from threading import Thread
from faker import Faker
from src.controllers.authorisation import Authorisation
from src.controllers.messages import Messages
import time


class Generator(Thread):
    def __init__(self, redis_connection, login, users_list, users_total, authorization: Authorisation):
        Thread.__init__(self)
        self.connection = redis_connection
        self.users_list = users_list
        self.users_total = users_total
        authorization.signup(login)
        self.user_id = authorization.login(login)
        self.user_login = login

    def run(self):
        messages = Messages()
        while True:
            content = users_set.sentence(nb_words=15, variable_nb_words=True, ext_word_list=None)
            receiver = users[randint(0, 9)]
            messages.create(content, self.user_id, self.connection.hget("users:", receiver))
            print("User %s sent message to %s" % (self.user_login, receiver))
            time.sleep(randint(1, 10))


if __name__ == '__main__':
    threads = []
    users_set = Faker()
    users = [users_set.profile(fields=['username'], sex=None)['username'] for u in range(10)]
    auth = Authorisation()
    for i in range(10):
        print(users[i])
        threads.append(Generator(
            redis.Redis(host="192.168.99.102", charset="utf-8", decode_responses=True),
            users[i], users, 10, auth))
    for thread in threads:
        thread.start()

    connection = redis.Redis(host="192.168.99.102", charset="utf-8", decode_responses=True)
    online = connection.smembers("online:")
    for user in online:
        connection.srem("online:", user)
