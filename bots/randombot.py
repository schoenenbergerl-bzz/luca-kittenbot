import json
import random

class RandomBot():
    """
    This is a helper class to run the bot in the local environment
    """
    def __init__(self, name):
        self.name = name
        self._bot = RandomKitten(name)

    def request(self, data):
        """
        Request for a response
        :param data:
        :return:
        """
        payload = json.loads(data)
        action = payload['action']
        if action == 'START ':
            return self._bot.start_round(payload)
        elif action == 'PLAY':
            return self._bot.play()
        elif action == 'DRAW':
            return self._bot.add_card(payload['card'])
        elif action == 'INFORM':
            return self._bot.inform(payload['botname'], payload['event'], payload['data'])
        elif action == 'DEFUSE':
            return self._bot.handle_exploding_kitten(payload['decksize'])
        elif action == 'FUTURE':
            return self._bot.see_the_future(payload['cards'])
        return None

class RandomKitten():
    def __init__(self, name):
        self.name = name
        self._hand = []


    def start_round(self, data):
        """
        A new round has started
        :param data:
        :return:
        """
        self._hand = []

    def add_card(self, cardname):
        """
        Add a card to my hand
        """
        self._hand.append(cardname)

    def inform(self, botname, action, response):
        """
        Get information about the action a bot that was taken
        :param botname:
        :param action:
        :param response:
        :return:
        """
        #print(f'Rando-Info: {response}')
        if botname == self.name:
            # I don't care about my own actions
            pass
        pass

    def play(self):
        """
        Play a card from my hand or don't
        :return:
        """
        if random.random() < 0.5:
            return None
        playable_cards = [card for card in self._hand if card != 'DEFUSE']
        if playable_cards:
            index = random.randint(0, len(playable_cards) - 1)
            card = self._hand.pop(index)
            return card
        return None

    def handle_exploding_kitten(self, deck_size):
        """
        I defused an exploding kitten, choose where to put it
        :param deck_size: The size of the card deck
        :return:
        """
        return random.randint(0, deck_size)

    def see_the_future(self, top_three):
        """
        I have seen the future
        :param top_three: A list of the top three cards
        :return:
        """
        pass