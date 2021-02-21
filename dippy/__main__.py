from dippy import Client
import argparse
import os


def get_args():
    parser = argparse.ArgumentParser(description="Launch a Dippy bot for Discord")
    parser.add_argument(
        "--token", "-t", help="The token to use for the bot", default=None
    )
    parser.add_argument(
        "--tokenvar",
        "-v",
        help="The environment variable that stores the token to use for the bot",
        default="DISCORD_TOKEN",
    )
    parser.add_argument("--name", "-n", help="Name for the bot")
    parser.add_argument(
        "--prefix", "-p", help="The command prefix to use for bot commands", default="!"
    )

    return parser.parse_args()


args = get_args()
token = args.token if args.token else os.getenv(args.tokenvar)
Client.launch(token=token, command_prefix=args.prefix, name=args.name)
