import random
import sqlite3


class Create:
    card = "400000"
    pin = ""

    def make_card(self):
        for i in range(9):
            self.card += str(random.randint(0, 9))

        check_sum = checksum(self.card)

        if check_sum % 10 == 0:
            self.card += "0"
        else:
            self.card += str(10 - (check_sum % 10))
        return self.card

    def make_pin(self):
        for i in range(4):
            self.pin += str(random.randint(0, 9))
        return self.pin


def checksum(card_number):
    check_sum = 0
    i = 1
    for letter in card_number:
        if i % 2 != 0:
            i += 1
            letter = int(letter) * 2
            if int(letter) > 9:
                letter = int(letter) - 9
                check_sum += int(letter)
            else:
                check_sum += int(letter)
        else:
            i += 1
            check_sum += int(letter)
    return check_sum


def luhn(card_number):
    tested = card_number[-1]
    card_number = card_number[:-1]
    check_sum = checksum(card_number)

    if check_sum % 10 == 0:
        value = "0"
    else:
        value = str(10 - (check_sum % 10))

    if value == tested:
        return True
    else:
        return False


def log(a_login, a_password):
    cur.execute('SELECT number, pin FROM card WHERE number == (?) AND pin == (?)', (a_login, a_password))

    if len(cur.fetchall()) == 0:
        print("Wrong card number or PIN!")
    else:
        print("You have successfully logged in!")

        while True:
            action = input("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
""")
            if action == "1":
                cur.execute('SELECT balance FROM card WHERE number == (?) AND pin == (?)', (a_login, a_password))
                print("Balance:", cur.fetchall())
            elif action == "2":
                income = int(input("Enter income:"))
                cur.execute('UPDATE card SET balance = balance + (?) WHERE number == (?) AND pin == (?)',
                            (income, a_login, a_password))
                conn.commit()
                print("Income was added!")
            elif action == "3":
                print("Transfer")
                card = input("Enter card number")
                cur.execute('SELECT number FROM card WHERE number == (?)', (card,))
                if card == a_login:
                    print("You can't transfer money to the same account!")
                elif luhn(card) is False:
                    print("Probably you made mistake in the card number. Please try again!")
                elif len(cur.fetchall()) == 0:
                    print("Such a card does not exist")
                else:
                    how_much = int(input("Enter how much money you want to transfer:"))
                    cur.execute('SELECT balance FROM card WHERE number == (?) AND pin == (?)', (a_login, a_password))
                    balance = cur.fetchall()
                    if how_much > int(balance[0][0]):
                        print("Not enough money!")
                    else:
                        cur.execute('UPDATE card SET balance = balance + (?) WHERE number == (?)',
                                    (how_much, card))
                        cur.execute('UPDATE card SET balance = balance - (?) WHERE number == (?)',
                                    (how_much, a_login))
                        conn.commit()
                        print("Success!")

            elif action == "4":
                cur.execute("DELETE FROM card WHERE number == (?) AND pin == (?)", (a_login, a_password))
                conn.commit()
                print("The account has been closed!")
            elif action == "5":
                return "back"
            elif action == "0":
                return "exit"


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
conn.commit()

while True:

    decision = input("""1. Create an account
2. Log into account
0. Exit""")

    if decision == "1":
        new = Create()
        new_id = len(cur.fetchall()) + 1
        cur.execute("INSERT INTO card VALUES (?, ?, ?, ?)", (new_id, new.make_card(), new.make_pin(), 0))
        conn.commit()
        print("Your card has been created")
        print("Your card number:")
        print(new.card)
        print("Your card PIN:")
        print(new.pin)

    elif decision == "2":
        login = input("Enter your card number:")
        password = input("Enter your PIN:")
        check = log(login, password)
        if check == "back":
            print("You have successfully logged out!")
            pass
        elif check == "exit":
            print("Bye!")
            break
    elif decision == "0":
        print("Bye!")
        break
