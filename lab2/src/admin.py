import redis


connection = redis.Redis(host="192.168.99.102", charset="utf-8", decode_responses=True)


def run_interface():
    while True:
        display_interface()
        command = int(input("$ "))

        if command == 1:
            online_users = connection.smembers("online:")
            print("Users online:")
            for user in online_users:
                print(user)

        elif command == 2:
            n = int(input("Which amount you want to see?\n$ "))
            active_users = connection.zrange("sent:", 0, n - 1, desc=True, withscores=True)
            print("Top %s of most active users: " % n)
            for index, user in enumerate(active_users):
                print(f"{user[0]} --- {int(user[1])} messages")

        elif command == 3:
            n = int(input("Which amount you want to see?\n $"))
            spammers = connection.zrange("spam:", 0, n - 1, desc=True, withscores=True)
            print("Top %s of most systematic spammers: " % n)
            for index, spammer in enumerate(spammers):
                print(f"{spammer[0]} - {int(spammer[1])} spam messages")

        elif command == 4:
            n = int(input("Which amount you want to see?\n $"))
            with open("events.log") as file:
                print("Newest %s lines of logs: " % n)
                for line in file.readlines()[-n:]:
                    print(line)

        elif command == 5:
            break

        else:
            print("No such operation\n")


def display_interface():
    print("\nYou are in admin mode. Available operations:")
    print("Get online users(1)")
    print("Get most active users(2)")
    print("Get most systematic spammers(3)")
    print("Get an activity list(4)")
    print("Close(5)")


if __name__ == '__main__':
    run_interface()
