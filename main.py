""" Main logic for the application. """
import importlib
import json
import os
import random
from typing import List

from game.arena import Arena
from game.bot import Bot


def main():
    bot_list = load_bots('bots')
    alive_count = len(bot_list)
    arena = Arena()
    start_round(arena, bot_list)

    print('----------- Game Start -----------')
    save_bot = -1
    while alive_count > 1:
        bot_number, action, data = arena.take_turn()
        active_bot = bot_list[bot_number]
        if bot_number != save_bot:
            print(f'Active bot: {active_bot.name}')
            save_bot = bot_number
        print(f'  - Action={action} / Data={data}')
        if action == 'PLAY':
            response = send_request(active_bot, action, data)
        elif action == 'DRAW':
            if data == 'EXPLODING_KITTEN':
                response = None
            else:
                response = send_request(active_bot, 'DRAW', {'card': data})
            print(f'=> {arena.read_hand(bot_number)}')
            inform_bots(active_bot.name, bot_list, 'DRAW', None)
        elif action == 'DEFUSE':
            response = send_request(active_bot, 'DEFUSE', {'decksize': arena.deck_size})
            print(f'  => Bot {active_bot.name} defused the exploding kitten')
            inform_bots(active_bot.name, bot_list, 'DEFUSE', '')
        elif action == 'EXPLODE':
            response = send_request(active_bot, 'EXPLODE', None)
            print(f'  => Bot {active_bot.name} exploded')
            alive_count -= 1
            inform_bots(active_bot.name, bot_list, 'EXPLODE', '')
        elif action == 'FUTURE':
            response = send_request(active_bot, 'FUTURE', {'cards': data})
        elif action == 'NEXTBOT':
            response = None
            # input('Press Enter to continue...')
        print(f'  - Response={response}')
        if arena.analyze_turn(response):
            inform_bots(active_bot.name, bot_list, action, response)

    finish_round(bot_list, arena)


def give_cards(arena: Arena, bot_list: List) -> None:
    """
    Give cards to the bots in the list.
    :param arena: Arena object
    :param bot_list: List of Bot objects
    :return: None
    """
    active_bot = 0
    for bot in bot_list:
        hand = arena.read_hand(active_bot)
        for card in hand:
            response = send_request(bot, 'DRAW', {'card': card})
        active_bot += 1


def load_bots(directory: str) -> List[Bot]:
    """
    Load all bots from a directory.
    :param directory:
    :return:
    """
    bots = []
    for filename in os.listdir(directory):
        if filename.endswith('.py') and \
                filename != '__init__.py' and \
                filename != 'bot.py':
            module_name = filename[:-3]
            module = importlib.import_module(f'{directory}.{module_name}')
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr_name.lower() == module_name:
                    bot_instance = attr(module_name)
                    bots.append(bot_instance)

    random.shuffle(bots)
    return bots


def start_round(arena, bot_list):
    """
    Start a new round.
    :param arena:
    :param bot_list:
    :return:
    """
    card_counts = arena.start_round(len(bot_list))
    give_cards(arena, bot_list)
    data = {
        'card_counts': [],
        'bots': [bot.name for bot in bot_list],
    }
    for card in dir(card_counts):
        if not card.startswith('__'):
            data['card_counts'].append(
                {
                    'name': card,
                    'count': getattr(card_counts, card),
                }
            )

    ''' Inform all the bots that the round has started. '''
    for bot in bot_list:
        send_request(bot, 'START', data)


def finish_round(bot_list: List[Bot], arena: Arena) -> None:
    """
    Finish the round.
    :param bot_list: List of Bot objects
    :param arena: Arena object
    :return: None
    """
    print('----------- Game Over -----------')

    ranking = []
    rank = 1
    for bot_number in arena.ranking:
        print(f'{rank}. {bot_list[bot_number].name}')
        ranking.append(bot_list[bot_number].name)
        rank += 1

    ''' Inform all the bots that the round has ended. '''
    for bot in bot_list:
        send_request(bot, 'OVER', {'ranks': ranking})



def inform_bots(botname, bot_list: List[Bot], action: str, response: str) -> None:
    """
    Inform all the bots of the action that just occurred.
    :param botname: str The name of the bot who took the action
    :param bot_list: List of Bot objects
    :param action: str action
    :param response: str the response from the bot
    :return: None
    """

    for bot in bot_list:
        data = {
            'botname': botname,
            'event': action,
            'data': response,
        }
        # bot.inform(botname, action, response)
        send_request(bot, 'INFORM', data)


def send_request(bot: Bot, action: str, data: dict) -> str:
    """
    Send a request to a bot.
    :param bot: Bot object
    :param action: str action
    :param data: str data
    :return: str response
    """
    if data is None:
        data = {}
    data['action'] = action

    return bot.request(json.dumps(data))


if __name__ == "__main__":
    main()