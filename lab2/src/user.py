import redis
from src.logger import Logger
from src.controllers.authorisation import Authorisation
from src.controllers.messages import Messages

connection = redis.Redis(host="192.168.99.102", charset="utf-8", decode_responses=True)


def run_interface():
    auth = Authorisation()
    messages = Messages()
    user_id = -1
    logged_in = False
    listener = Logger(connection)
    listener.setDaemon(True)
    listener.start()

    while True:
        if not logged_in:
            display_start_menu()
            command = int(input("$ "))
            if command == 1:
                login = input("Enter your login: ")
                auth.signup(login)

            elif command == 2:
                login = input("Enter your login: ")
                user_id = auth.login(login)
                logged_in = user_id != -1

            elif command == 3:
                break

            else:
                print("No such operation")

        else:
            display_menu()
            command = int(input("$ "))

            if command == 1:
                msg = input("Write your message: ")
                receiver_login = input("Write the login of person you want to get this message: ")

                receiver = connection.hget("users:", receiver_login)
                if receiver is not None:
                    messages.create(msg, user_id, int(receiver))
                    print("Message sent!")
                else:
                    print("Receiver does not exist!")

            elif command == 2:
                messages.get_all(user_id)

            elif command == 3:
                current = connection.hmget("user:%s" % user_id,
                                           ['in_queue', 'checking', 'blocked', 'sent',
                                            'delivered'])
                print(
                    "In queue: %s\nIs checking: %s\nBlocked: %s\nSent: %s\nDelivered: %s" % tuple(current))

            elif command == 4:
                login = connection.hmget("user:%s" % user_id, ["login"])[0]
                auth.logout(login)
                logged_in = False
                user_id = -1

            else:
                print("No such operation\n")


def display_start_menu():
    print("Welcome to messaging tool! Sign up to start using! Or login if you already have an account")
    print("Sign up(1)")
    print("Log in(2)")
    print("Close(3)")


def display_menu():
    print("\nSend new message(1)")
    print("Received messages(2)")
    print("Messages' info(3)")
    print("Log out(4)")


if __name__ == '__main__':
    run_interface()
