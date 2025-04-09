import random
from typing import List, Optional

from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState


class LucaBot(Bot):
    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.future_cards = []

    def play(self, state: GameState) -> Optional[Card]:
        """
        Decide whether to play a card or skip based on game state and strategy.
        Prioritize "See the Future" cards and conserve others unless hand is large.

        :param state: GameState object
        :return: Card object or None
        """
        playable_cards = [card for card in self.hand if card.card_type != CardType.DEFUSE]
        if not playable_cards:
            return None

        see_future_cards = [card for card in playable_cards if card.card_type == CardType.SEE_THE_FUTURE]

        if see_future_cards and not self.future_cards:
            return see_future_cards[0]

        if self.future_cards and self.future_cards[0].card_type == CardType.EXPLODING_KITTEN:
            return random.choice(playable_cards)

        if len(self.hand) > 5:
            return random.choice(playable_cards)

        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        """
        Place the Exploding Kitten strategically in the draw pile.
        Prefer deeper placement to delay its reappearance.

        :param state: GameState object
        :return: int index of the draw pile
        """
        deck_size = state.cards_left_to_draw
        if deck_size <= 1:
            return 0

        if self.future_cards:
            safe_spots = list(range(deck_size))
            for i, card in enumerate(self.future_cards[:min(3, deck_size)]):
                if card.card_type == CardType.EXPLODING_KITTEN and i in safe_spots:
                    safe_spots.remove(i)
            if safe_spots:
                return random.choice(safe_spots[-len(safe_spots) // 5:])

        return random.randint(max(0, deck_size - deck_size // 5), deck_size - 1)

    def see_the_future(self, state: GameState, top_three: List[Card]) -> None:
        """
        Store the top three cards seen to inform future decisions.

        :param state: GameState object
        :param top_three: List of top three cards of the draw pile
        :return: None
        """
        self.future_cards = top_three.copy()

    def card_played(self, card_type: CardType, position: int) -> bool:
        """
        React to another bot playing a card. Track "See the Future" usage.

        :param card_type: CardType object
        :param position: int
        :return: bool
        """
        if card_type == CardType.SEE_THE_FUTURE:
            self.future_cards = []
        return True
