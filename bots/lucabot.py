import json
import random


class TemplateBot():
    """
    Enhanced TemplateBot with strategies to handle Exploding Kittens.
    """

    def __init__(self, name):
        self.name = name
        self._bot = SmarterKitten(name)

    def request(self, data):
        """
        Handle requests for different actions in the game.
        """
        payload = json.loads(data)
        action = payload['action']
        if action == 'PLAY':
            return self._bot.play()
        elif action == 'START':
            return self._bot.start_round()
        elif action == 'DRAW':
            return self._bot.add_card(payload['card'])
        elif action == 'INFORM':
            return self._bot.inform(payload['botname'], payload['event'], payload['data'])
        elif action == 'DEFUSE':
            return self._bot.defuse(payload['decksize'])
        elif action == 'FUTURE':
            return self._bot.see_the_future(payload['cards'])
        return None


class SmarterKitten():
    """
    This class contains the strategic implementation of the TemplateBot.
    """

    def __init__(self, name):
        self.name = name
        self._hand = []
        self._future_cards = []

    def start_round(self):
        self._hand = []
        self._future_cards = []
        return 'ACK'

    def add_card(self, cardname):
        self._hand.append(cardname)
        return 'ACK'

    def inform(self, botname, event, data):
        return 'ACK'

    def play(self):
        if self._future_cards and self._future_cards[0] == 'EXPLODING_KITTEN':
            if 'SKIP' in self._hand:
                self._hand.remove('SKIP')
                self._future_cards = []
                return 'SKIP'
            elif 'SHUFFLE' in self._hand:
                self._hand.remove('SHUFFLE')
                self._future_cards = []
                return 'SHUFFLE'

        if self._hand:
            if 'NORMAL' in self._hand:
                return self._hand.pop()
            return self._hand.pop(0)
        return None

    def defuse(self, decksize):
        if 'EXPLODING_KITTEN' in self._hand:
            self._hand.remove('EXPLODING_KITTEN')
            position = random.randint(0, decksize)
            return position
        return 0

    def see_the_future(self, top_three):
        self._future_cards = top_three
        return 'ACK'
