from dippy import Client
import argparse


def get_args():
    parser = argparse.ArgumentParser(description="Launch a Dippy bot for Discord")
    parser.add_argument("--token", "-t", help="The token to use for the bot")
    parser.add_argument("--name", "-n", help="Name for the bot")
    parser.add_argument(
        "--prefix", "-p", help="The command prefix to use for bot commands"
    )

    return parser.parse_args()


args = get_args()
Client.launch(token=args.token, command_prefix=args.prefix, name=args.name)
