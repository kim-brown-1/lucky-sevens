import random
import sys
import time

initial_balance = 0.0
balance = 0.0
bet = 0
multiplier = 0
menu_spaces = 5
symbols = ["7", "-", "$"]
typing_sleep = 0.04
roll_sleep = 1
jackpot_amt = 1000
dollar_sign_amt = 0
winners = []
max_free_rolls = 10
machine_width = 14
machine_height = 4

# use tuples instead of map for simple menu selection indexing
# (bet amt USD, winnings multiplier)
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
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(typing_sleep)
    sys.stdout.write('\n')
    sys.stdout.flush()


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

    bet_str = input(to_print + "\n")

    try:
        choice = int(bet_str)
    except ValueError:
        print("Invalid bet, please enter an integer 1-", len(betToMultiplier), "\n")
        get_bet()
        return

    if choice < 1 or choice > len(betToMultiplier):
        # TODO: fix bug here when choices are abbreviated because of balance
        print("Invalid bet, please enter an integer 1-", len(betToMultiplier), "\n")
        get_bet()
        return

    bet = betToMultiplier[choice - 1][0]
    multiplier = betToMultiplier[choice - 1][1]
    dollar_sign_amt = 0.4 * bet


def print_status():
    to_print = "Balance: " + get_money_string(balance) + " " * menu_spaces + "Bet: " + get_money_string(bet) + \
               " " * menu_spaces + "Multiplier: " + str(multiplier)
    print(to_print)


def cash_out():
    if balance > initial_balance:
        slow_type("Congrats, you've won! You ended up making " + get_money_string(balance - initial_balance) + "!")
        username = input("Enter your username to boast about your earnings to everyone:\n")
        if username != "":
            username = username.replace(",", "")
            save_winner(username, balance - initial_balance)

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


def free_rolls():
    num_rolls = random.randrange(2, max_free_rolls)
    slow_type("YOU'VE WON " + str(num_rolls) + " FREE ROLLS!")
    input("Any key to start")
    for i in range(num_rolls):
        roll(True)


def roll(is_free: bool):
    global balance
    global dollar_sign_amt

    if not is_free:
        if balance - bet <= 0:
            get_bet()
            return
        balance -= bet

    print('-' * machine_width)
    print("|" + " " * (machine_width - 1) + "|")
    print('-' * machine_width)
    print("\\ ", end="")
    r1 = symbols[random.randrange(len(symbols))]
    print_symbol(r1+" \\")
    r2 = symbols[random.randrange(len(symbols))]
    print_symbol(r2+" \\")
    r3 = symbols[random.randrange(len(symbols))]
    print_symbol(r3 + " \\\n")
    print('-' * machine_width)
    for i in range(machine_height):
        print("|" + " " * machine_width + "|")
    print("  " + '-' * machine_width)
    print()

    if r1 == r2 == r3 == "7":
        jackpot()
    if r1 == r2 == r3 == "-":
        free_rolls()

    # TODO: make more sophisticated / realistic
    money_sign_won = 0.0
    for symbol in [r1, r2, r3]:
        if symbol == "$":
            money_sign_won += dollar_sign_amt
    if money_sign_won != 0.0:
        print("+", get_money_string(money_sign_won))
    balance += money_sign_won


def show_menu():
    print()
    print_status()
    to_print = "1] Roll" + " " * menu_spaces + "2] Change bet" + " " * menu_spaces + "3] Cash out\n"
    choice_str = input(to_print)
    if choice_str == "":
        choice_str = "1"  # treat enter as roll

    try:
        choice = int(choice_str)
    except ValueError:
        print("Invalid selection, please enter an integer 1-3.\n")
        show_menu()
        return

    if choice == 1:
        roll(False)
    elif choice == 2:
        get_bet()
    elif choice == 3:
        cash_out()
    else:
        print("Invalid selection, please enter an integer 1-3.\n")
        show_menu()


def get_balance():
    global balance
    global initial_balance
    starting_str = input("Enter your starting balance (in USD):\n")
    try:
        balance = int(starting_str)
    except ValueError:
        print("Invalid starting balance, please enter an integer.")
        get_balance()
        return
    except MemoryError:  # extremely large string entered
        print("Invalid starting balance, please try again.")
        get_balance()
        return

    if balance < betToMultiplier[0][0]:
        print("Please enter a starting balance above " + str(betToMultiplier[0][0]) + ".")
        get_balance()
        return

    if balance > 1000000:
        print("Balance above max threshold (1,000,000). Please enter a smaller amount.")
        get_balance()
        return

    initial_balance = balance


def main():
    try:
        random.seed()
        skip = input("Skip intro? Y/N\n")
        show_intro = not (skip == "Y" or skip == "y")
        if show_intro:
            slow_type("Welcome to lucky sevens! Take your time and be careful - if you run out of money, game over.")
            slow_type("If you cash out with net gain, then congrats, you've won!")
            slow_type("The rules are pretty simple- if you get three symbols in a row - jackpot!")
            slow_type("Cash symbols are also pretty good.")
            slow_type("Good luck! :)")

        populate_and_print_winners()
        get_balance()
        get_bet()
        while True:
            show_menu()
    except KeyboardInterrupt:
        exit()


if __name__ == '__main__':
    main()
