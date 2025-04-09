""" Implements a simple discovery service that listens for incoming connections """

import selectors
import socket
import traceback

from server_message import ServerMessage
from services import Services

HOST = '127.0.0.1'
PORT = 65432


def main():
    """
    main entry point for the discovery service
    """
    sel = selectors.DefaultSelector()
    services = Services()

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print(f'Listening on {(HOST, PORT)}')
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(sel, key.fileobj)
                else:
                    message = key.data
                    try:
                        message.process_events(mask)
                        process_action(message, services)
                    except Exception:
                        print(
                            f'Main: Error: Exception for {message.ipaddr}:\n'
                            f'{traceback.format_exc()}'
                        )
                        message._close()
    except KeyboardInterrupt:
        print('Caught keyboard interrupt, exiting')
    finally:
        sel.close()


def process_action(message, services):
    """
    process the action from the client
    :param message: the message object
    :param services: the services object
    """

    if message.event == 'READ':
        action = message.request['action']
        # TODO call the methods on the Services-object depending on the action
        message.response = 'TODO Response from the method'
        message.set_selector_events_mask('w')


def accept_wrapper(sel, sock):
    """
    accept a connection
    """
    conn, addr = sock.accept()  # Should be ready to read
    print(f'Accepted connection from {addr}')
    conn.setblocking(False)
    message = ServerMessage(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)


if __name__ == '__main__':
    main()
