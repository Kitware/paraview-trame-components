import argparse


def cli(*args, prog="ParaView Tool"):
    parser = argparse.ArgumentParser(prog="ParaView State Loader")
    for arg in args:
        parser.add_argument(arg)
    options, _ = parser.parse_known_args()
    return options
