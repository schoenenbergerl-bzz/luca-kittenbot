""" Socket-controller for the RandomBot """
from bots.randombot import RandomBot


def main():
    """
    main function for the socket-controller
    :return:
    """
    bot = RandomBot("RandomBot")
    # register the bot with the clowder => you get a port number
    # open a socket with the port number
    # listen for incoming connections from the arena
    # analyse the incoming connections
    # call the relevant bot method depending on the action
    # send the response back to the arena

    # close the socket


if __name__ == '__main__':
    main()
