import pickle
import re
import colorama
import os
import webbrowser
import subprocess

colorama.init()


# Helper functions for terminal formatting
def bold(s):
    return f"\x1b[1m{s}\x1b[0m"

def red(s):
    return f"\x1b[31m{s}\x1b[0m"


# Helper for loading andf saving
def load_pkl(filename, default):
    if os.path.exists(filename):
        print(f'Unpacking {filename}...')
        with open(filename, 'rb') as f:
            return pickle.load(f)
    else:
        print(f'{filename} not found. Initialising...')
        return default

def save_pkl(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)



# Parsing commands
# Parse takes a string and returns (keep_running, pickle_needed)
def parse(c):
    parts = c.split()
    if not parts:
        return True, False

    command, args = parts[0], parts[1:]

    match command:
        case 'q' | 'quit':
            return False, True
        case 'o' | 'open':
            return handle_open(args)
        case 'l' | 'list':
            return handle_list(args)
        case 'r' | 'register':
            return handle_register(args)
        case 'remove':
            return handle_remove(args)
        case 'add':
            return handle_add(args)
        case _:
            if args:
                print(f"{red(bold('Error:'))} Unknown command with extra arguments.")
                return True, False
            return handle_open([command])


def launch(entry):
    info = locations[entry]
    if info['type'] == 'site':
        webbrowser.open(info['loc'])
    else:
        try:
            subprocess.Popen(
                info['loc'],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"{red(bold('Launch failed:'))} {e}")



def handle_open(args):
    if len(args) != 1:
        print(f"{red(bold('Error:'))} open requires exactly one {bold('name')} (context or location).")
        return True, False

    name = args[0]

    if name in contexts:
        if not contexts[name]:
            print(f"{bold(name)} is empty.")
            return True, False
        for entry in contexts[name]:
            if entry not in locations:
                print(f"{red(bold('Warning:'))} {bold(entry)} is not registered.")
                continue
            launch(entry)
        return True, False

    elif name in locations:
        launch(name)
        return True, False

    else:
        print(f"{red(bold('Error:'))} {bold(name)} not found in either contexts or locations.")
        return True, False




def handle_list(args):
    if not args or args[0] == 'contexts':
        if not contexts:
            print("No contexts found.")
        else:
            for ctx, locs in contexts.items():
                if not locs:
                    print(f"{bold(ctx)}: Empty")
                else:
                    print(f"{bold(ctx)}: {', '.join(locs)}")
        return True, False

    elif args[0] == 'locations':
        if not locations:
            print("No locations registered.")
        else:
            for name, info in locations.items():
                print(f"{bold(name)}: {info['type']} → {info['loc']}")
        return True, False

    else:
        print(f"{red(bold('Error:'))} list accepts {bold('contexts')} or {bold('locations')}.")
        return True, False


def handle_register(args):
    if len(args) < 2:
        print(f"{red(bold('Error:'))} register requires at least two arguments: "
              f"{bold('app|site|context')} and {bold('name')} (plus {bold('location')} for app/site).")
        return True, False

    kind, name = args[0], args[1]

    match kind:
        case 'app' | 'site':
            if len(args) != 3:
                print(f"{red(bold('Error:'))} register {kind} requires a {bold('name')} and a {bold('location')}.")
                return True, False
            locations[name] = {'type': kind, 'loc': args[2]}
            print(f"Registered {bold(kind)} {bold(name)} at {args[2]}")
            return True, True

        case 'context':
            if len(args) != 2:
                print(f"{red(bold('Error:'))} register context only takes {bold('name')}.")
                return True, False
            contexts[name] = []
            print(f"Registered context {bold(name)}.")
            return True, True

        case _:
            print(f"{red(bold('Error:'))} register kind should be {bold('app')}, {bold('site')}, or {bold('context')}.")
            return True, False


def handle_remove(args):
    if len(args) == 0:
        print(f"{red(bold('Error:'))} remove requires at least a {bold('name')}.")
        return True, False

    name = args[0]

    if len(args) == 2:
        # Remove from a specific context
        context = args[1]
        if context not in contexts:
            print(f"{red(bold('Error:'))} Context {bold(context)} not found.")
            return True, False
        if name not in contexts[context]:
            print(f"{red(bold('Error:'))} {bold(name)} not found in context {bold(context)}.")
            return True, False

        confirm = input(f"Remove {bold(name)} from context {bold(context)}? (y/N): ").lower()
        if confirm == 'y':
            contexts[context].remove(name)
            print(f"Removed {bold(name)} from context {bold(context)}.")
            return True, True
        else:
            print("Cancelled.")
            return True, False

    else:
        removed = False
        if name in locations or name in contexts:
            confirm = input(f"Remove all entries named {bold(name)} from locations or contexts? (y/N): ").lower()
            if confirm == 'y':
                if name in locations:
                    del locations[name]
                    print(f"Removed from locations: {bold(name)}.")
                    removed = True
                    for ctx, vals in contexts.items():
                        contexts[ctx] = [i for i in vals if i != name]
                if name in contexts:
                    del contexts[name]
                    print(f"Removed context: {bold(name)}.")
                    removed = True
            else:
                print("Cancelled.")
        else:
            print(f"{red(bold('Error:'))} {bold(name)} not found in locations or contexts.")

        return True, removed


def handle_add(args):
    if len(args) != 2:
        print(f"{red(bold('Error:'))} add requires exactly two arguments: {bold('name')} and {bold('context')}.")
        return True, False

    name, context = args

    if name not in locations:
        print(f"{red(bold('Error:'))} {bold(name)} not found in locations.")
        return True, False

    if context not in contexts:
        print(f"{red(bold('Error:'))} Context {bold(context)} not found.")
        return True, False

    if name in contexts[context]:
        print(f"{red(bold('Error:'))} {bold(name)} is already in context {bold(context)}.")
        return True, False

    contexts[context].append(name)
    print(f"Added {bold(name)} to context {bold(context)}.")
    print(f"{bold(context)} now contains: {', '.join(contexts[context])}")
    return True, True




# Setup
os.system('cls')
print("Welcome to Concher!")
locations = load_pkl("locations.pkl", {})
contexts = load_pkl("contexts.pkl", {})



print(f"Type {bold('help')} to learn more...")
running = True


while running:
    command = input("> ")
    running, pickle_needed = parse(command)
    if pickle_needed:
        save_pkl('locations.pkl', locations)
        save_pkl('contexts.pkl', contexts)