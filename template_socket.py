from bots.templatebot import TemplateBot
import selectors
import socket
import traceback
from client_message import ClientMessage
from server_message import ServerMessage
from services import Services

HOST = '127.0.0.1'
PORT = 65432

def main():
    """
    main function for the socket-controller
    :return:
    """
    bot = TemplateBot("LucaTopBot")

    item = {'action': 'MEOW',
            'ip': '127.0.0.1',
            'name': 'LucaTopBot',
            'type': 'bot'}

    print(f'Registration service {item["type"]} {item["ip"]}')
    try:
        port1 = int(send_request(item))  # Convert to int here
        host1 = '127.0.0.1'

        sel = selectors.DefaultSelector()
        services = Services()

        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host1, port1))
        lsock.listen()
        print(f'Listening on {(port1, host1)}')
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
            
    except ValueError as e:
        print(f"Error: {e}")
        return

def process_action(message, services):
    """
    process the action from the client
    :param message: the message object
    :param services: the services object
    """
    if message.event == 'READ':
        action = message.request['action']
        message.response = 'TODO Response from the method'
        message.set_selector_events_mask('w')

def accept_wrapper(sel, sock):
    """
    accept a connection
    """
    conn, addr = sock.accept()
    print(f'Accepted connection from {addr}')
    conn.setblocking(False)
    message = ServerMessage(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)

def send_request(action):
    """
    sends a request to the server
    :param action: the action to send
    :return: the port number received from server
    """
    sel = selectors.DefaultSelector()
    request = create_request(action)
    start_connection(sel, HOST, PORT, request)
    
    return_port = None
    
    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                    if message.response is not None:
                        # Assuming the response contains just the port number
                        return_port = message.response
                except Exception:
                    print(
                        f'Main: Error: Exception for {message.ipaddr}:\n'
                        f'{traceback.format_exc()}'
                    )
                    message._close()
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print('Caught keyboard interrupt, exiting')
    finally:
        sel.close()
    
    if return_port is None:
        raise ValueError("No port received from server")
    return return_port

def create_request(action_item):
    return dict(
        type='text/json',
        encoding='utf-8',
        content=action_item,
    )

def start_connection(sel, host, port, request):
    addr = (host, port)
    print(f'Starting connection to {addr}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = ClientMessage(sel, sock, addr, request)
    sel.register(sock, events, data=message)

if __name__ == '__main__':
    main()