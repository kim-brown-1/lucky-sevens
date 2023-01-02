import random
import sys
import time

initial_balance = 0.0
balance = 0.0
bet = 0
multiplier = 0
menu_spaces = 5
symbols = ["7", "*", "$"]
typing_sleep = 0.04
roll_sleep = 1
jackpot_amt = 1000
dollar_sign_amt = 0
winners = []

# use tuples for easy indexing (when listing/
# first item is bet amt in $USD, second is multiplier
betToMultiplier = [
    (5, 1.0),
    (10, 1.2),
    (20, 1.5),
    (50, 2.0),
    (100, 3.0),
]


def save_winner(username: str, profit: float):
    # winners are only the top 10, in descending order
    changed = False
    for i in range(len(winners)):
        if profit > winners[i][1]:
            winners.insert(i, (username, profit))
            if len(winners) > 10:
                winners.pop()
            changed = True
            break

    if not changed and len(winners) < 10:
        # append onto end
        winners.append((username, profit))
        changed = True

    if changed:
        to_write = ""
        for winner in winners:
            to_write += winner[0] + "," + str(winner[1]) + "\n"

        f = open("winners.txt", "w")
        f.write(to_write)
        f.close()


def populate_and_print_winners():
    global winners

    f = open("winners.txt", "r")
    for line in f:
        split_line = line.split(",")
        user = split_line[0]
        amt_string = split_line[1]
        try:
            amt = float(amt_string)
            winners.append((user, amt))
        except ValueError:
            continue

    if len(winners) > 0:
        slow_type("Here are some previous winners' earnings:")
        for winner in winners:
            sys.stdout.write(winner[0] + ": " + get_money_string(winner[1]) + "\n")
            sys.stdout.flush()

        print("\n")


def get_money_string(amt: float):
    return f'${amt:.2f}'


def slow_type(text: str):
    try:
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(typing_sleep)
        sys.stdout.write('\n')
        sys.stdout.flush()
    except KeyboardInterrupt:
        exit()


def get_bet():
    global betToMultiplier
    global bet
    global multiplier
    global dollar_sign_amt

    if balance < betToMultiplier[0][0]:
        cash_out()

    print("Select your bet increment:\n")
    to_print = ""
    for i in range(len(betToMultiplier)):
        if betToMultiplier[i][0] > balance:
            if i == 0:
                # no options left
                cash_out()
            break
        to_print += str(i + 1) + "] " + str(betToMultiplier[i][0]) + " " * menu_spaces

    try:
        bet_str = input(to_print + "\n")
    except KeyboardInterrupt:
        return

    try:
        choice = int(bet_str)
        if choice < 1 or choice > len(betToMultiplier):
            # TODO: fix bug here when choices are abbreviated because of balance
            print("Invalid bet, please enter an integer 1-", len(betToMultiplier), "\n")
            return
        bet = betToMultiplier[choice - 1][0]
        multiplier = betToMultiplier[choice - 1][1]
        dollar_sign_amt = bet // 4
    except ValueError:
        print("Invalid bet, please enter an integer 1-", len(betToMultiplier), "\n")
        return


def print_status():
    to_print = "Balance: " + get_money_string(balance) + " " * menu_spaces + "Bet: " + get_money_string(bet) + \
               " " * menu_spaces + "Multiplier: " + str(multiplier)
    print(to_print)


def cash_out():
    if balance > initial_balance:
        slow_type("Congrats, you've won! You ended up making " + get_money_string(balance - initial_balance) + "!")
        try:
            username = input("Enter your username to boast about your earnings to everyone:\n")
            if username != "":
                username = username.replace(",", "")
                save_winner(username, balance - initial_balance)
        except KeyboardInterrupt:
            exit()

        slow_type("Now go put it back into another machine :)")
        exit()
    elif balance == initial_balance:
        slow_type("Okay nice, you broke even.")
        slow_type("Now that you have a clean slate, why not hop on another machine?")
        exit()
    else:
        slow_type("Aww, looks like you lost this time.")
        if balance != 0:
            slow_type("But good news, you still have " + get_money_string(balance) + ".")
        slow_type("Time to try and make back your losses, right?")
        exit()


def print_symbol(symbol: str):
    sys.stdout.write(symbol + "  ")
    sys.stdout.flush()
    time.sleep(roll_sleep)


def jackpot():
    global balance
    won = jackpot_amt * multiplier
    slow_type("JACKPOT!!")
    slow_type("You've won - get ready - " + get_money_string(won))
    balance += won


def roll():
    global balance
    global dollar_sign_amt

    if balance - bet <= 0:
        get_bet()
        return

    print()
    r1 = symbols[random.randrange(len(symbols))]
    print_symbol(r1)
    r2 = symbols[random.randrange(len(symbols))]
    print_symbol(r2)
    r3 = symbols[random.randrange(len(symbols))]
    print_symbol(r3)
    print()
    balance -= bet
    if r1 == r2 == r3 == "7":
        jackpot()

    # TODO: make more sophisticated / realistic
    money_sign_won = 0.0
    for symbol in [r1, r2, r3]:
        if symbol == "$":
            money_sign_won += dollar_sign_amt
    if money_sign_won != 0.0:
        print("Congrats, you won ", get_money_string(money_sign_won), " from the '$' symbol!")
    balance += money_sign_won


def show_menu():
    print()
    print()
    print()
    print_status()
    to_print = "1] Roll" + " " * menu_spaces + "2] Change bet" + " " * menu_spaces + "3] Cash out\n"
    try:
        choice_str = input(to_print)
    except KeyboardInterrupt:
        exit()

    try:
        choice = int(choice_str)
        if choice == 1:
            roll()
        elif choice == 2:
            get_bet()
        elif choice == 3:
            cash_out()
        else:
            print("Invalid selection, please enter an integer 1-3.\n")
            show_menu()
            return
    except ValueError:
        print("Invalid selection, please enter an integer 1-3.\n")
    return


def main():
    global initial_balance
    global balance

    # TODO: consider making board 9x9
    random.seed()
    try:
        skip = input("Skip intro? Y/N\n")
        show_intro = not (skip == "Y" or skip == "y")
    except KeyboardInterrupt:
        exit()

    if show_intro:
        slow_type("Welcome to lucky sevens! Take your time and be careful - if you run out of money, game over.")
        slow_type("If you cash out with net gain, then congrats, you've won!")
        slow_type("The rules are pretty simple- if you get three symbols in a row - jackpot!")
        slow_type("Cash symbols are also pretty good.")
        slow_type("Good luck! :)")

    populate_and_print_winners()

    try:
        starting_str = input("Enter your starting balance (in USD):\n")
    except KeyboardInterrupt:
        exit()

    try:
        balance = int(starting_str)
        initial_balance = balance
    except ValueError:
        print("Invalid starting balance, please enter an integer.\n")
        return

    get_bet()
    while True:
        show_menu()


if __name__ == '__main__':
    main()
