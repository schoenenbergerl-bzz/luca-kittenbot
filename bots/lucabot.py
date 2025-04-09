import random
from typing import List, Optional

from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState


class LucaBot(Bot):
    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.future_cards = []
        self.defuses_used_by_others = 0

    def play(self, state: GameState) -> Optional[Card]:
        """
        Play cards strategically based on deck size, hand, and future knowledge.

        :param state: GameState object
        :return: Card object or None
        """
        playable_cards = [card for card in self.hand if card.card_type != CardType.DEFUSE]
        if not playable_cards:
            return None

        deck_size = state.cards_left_to_draw
        see_future_cards = [card for card in playable_cards if card.card_type == CardType.SEE_THE_FUTURE]
        defuse_count = sum(1 for card in self.hand if card.card_type == CardType.DEFUSE)

        if see_future_cards and (not self.future_cards or deck_size < 5):
            return see_future_cards[0]

        if self.future_cards and self.future_cards[0].card_type == CardType.EXPLODING_KITTEN and defuse_count == 0:
            return random.choice(playable_cards)

        if deck_size < 5 and self.defuses_used_by_others < 2 and defuse_count > 0:
            return None

        if (len(self.hand) > 4 or deck_size < 3) and defuse_count > 0:
            return random.choice(playable_cards)

        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        """
        Place the Exploding Kitten optimally based on future knowledge.

        :param state: GameState object
        :return: int index of the draw pile
        """
        deck_size = state.cards_left_to_draw
        if deck_size <= 1:
            return 0

        if self.future_cards:
            deepest_ek = -1
            for i, card in enumerate(self.future_cards[:min(3, deck_size)]):
                if card.card_type == CardType.EXPLODING_KITTEN:
                    deepest_ek = i
            if deepest_ek >= 0 and deepest_ek + 1 < deck_size:
                return deepest_ek + 1

        return random.randint(max(0, deck_size - deck_size//4), deck_size - 1)

    def see_the_future(self, state: GameState, top_three: List[Card]) -> None:
        """
        Store and analyze top three cards for bomb density.

        :param state: GameState object
        :param top_three: List of top three cards
        :return: None
        """
        self.future_cards = top_three.copy()

    def card_played(self, card_type: CardType, position: int) -> bool:
        """
        Track opponent Defuse usage and clear future cards if deck changes.

        :param card_type: CardType object
        :param position: int
        :return: bool
        """
        if card_type == CardType.SEE_THE_FUTURE:
            self.future_cards = []
        elif card_type == CardType.DEFUSE:
            self.defuses_used_by_others += 1
        return True