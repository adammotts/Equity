import numpy as np
import math

RANKS = {2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:"J", 12:"Q", 13:"K", 14:"A"}
SUITS = {'Club': "♣️", 'Diamond': "♦", 'Heart': "♥️", 'Spade': "♠️"}
DECK = [(rank, suit) for suit in SUITS for rank in RANKS]
HAND_HIERARCHY = {1:"High Card", 2:"Pair", 3:"Two-Pair", 4:"Three of a Kind", 5:"Straight", 6:"Flush", 7:"Full House", 8:"Four of a Kind", 9:"Straight Flush", 10:"Royal Flush"}

class Calculations:
    
    def __init__(self, cards = []):
        self.update_current_cards(cards)

    def update_current_cards(self, new_cards):
        self.cards = [card for card in new_cards if card is not None]
        self.remaining_deck = DECK.copy()
        for card in self.cards:
            self.remaining_deck.remove(card)
    
    def calculate_current_hand_statistics(self):
        number_of_total_hands = 0
        number_of_hands_beaten = 0
        number_of_hands_chopped = 0
        number_of_hands_lost = 0
        hand_strength = Calculations.compute_hand_strength(self.cards)
        
        for combination in Calculations.all_combinations(self.remaining_deck, 2):
            number_of_total_hands += 1
            
            random_hand_strength = Calculations.compute_hand_strength(combination + self.cards[2:])
            if random_hand_strength < hand_strength:
                number_of_hands_beaten += 1
                
            elif random_hand_strength == hand_strength:
                number_of_hands_chopped += 1
                
            else:
                number_of_hands_lost += 1
                    
        return [number_of_hands_beaten, number_of_hands_chopped, number_of_hands_lost, number_of_total_hands]
              
    @staticmethod
    def all_combinations(list_of_cards, num_cards_to_choose):
        if num_cards_to_choose == 0:
            yield []
            return

        for i in range(len(list_of_cards)):
            item = list_of_cards[i]
            remaining = list_of_cards[i + 1:]
            for combo in Calculations.all_combinations(remaining, num_cards_to_choose - 1):
                yield [item] + combo
    
    def calculate_draws(self, min_required_cards = 5):
        if (len(self.cards)) < min_required_cards:
            return
            
        hand_strength = Calculations.compute_hand_strength(self.cards)
        list_of_stronger_hand_strengths = []
        
        for hs in range(10):
            if math.floor(hand_strength) < hs+1:
                list_of_stronger_hand_strengths.append([hs+1, 0])
                
        number_of_blank_cards = 7 - len(self.cards)
        all_possible_runouts = list(Calculations.all_combinations(self.remaining_deck, number_of_blank_cards))
          
        for runout in all_possible_runouts:
            hypothetical_hand_strength = Calculations.compute_hand_strength(self.cards + runout)
            for hand_strength in list_of_stronger_hand_strengths:
                if math.floor(hypothetical_hand_strength) == hand_strength[0]:
                    hand_strength[1] += 1            
        
        return [stronger_hand_strength + [len(all_possible_runouts)] for stronger_hand_strength in list_of_stronger_hand_strengths]
    
    @staticmethod
    def compute_hand_strength(list_of_cards):
        
        # Collect a list of all cards' ranks
        list_of_ranks = [card[0] for card in list_of_cards]
        
        # Collect a list of unique ranks and their frequencies within the list of cards
        unique_ranks, unique_rank_frequencies = np.unique(np.array(list_of_ranks), return_counts = True)
        frequencies = sorted(zip(unique_ranks, unique_rank_frequencies))
        
        # Create a separate copy used for "kickers"
        kickers = sorted(unique_ranks).copy()
        
        # Collect a list of suits and their frequencies within the list of cards
        list_of_suits = [card[1] for card in list_of_cards]
        unique_suits, unique_suit_frequencies = np.unique(np.array(list_of_suits), return_counts = True)
        
        # Straight and Royal Flush
        for s in SUITS:
            higher_end_of_straight = 14
            while higher_end_of_straight >= 5:
                count = 0
                for c in range (len(list_of_cards)):
                    if higher_end_of_straight == 5:
                        if (list_of_ranks[c] == 14 and list_of_suits[c] == s):
                            count += 1  
                    else:
                        if (list_of_ranks[c] == higher_end_of_straight - 4 and list_of_suits[c] == s):
                            count += 1                    
                    if (list_of_ranks[c] == higher_end_of_straight - 3 and list_of_suits[c] == s):
                        count += 1
                    if (list_of_ranks[c] == higher_end_of_straight - 2 and list_of_suits[c] == s):
                        count += 1
                    if (list_of_ranks[c] == higher_end_of_straight - 1 and list_of_suits[c] == s):
                        count += 1
                    if (list_of_ranks[c] == higher_end_of_straight and list_of_suits[c] == s):
                        count += 1
                if count == 5:
                    if higher_end_of_straight == 14:
                        return 10.0
                    else:
                        return 9 + higher_end_of_straight / 100                    
                higher_end_of_straight -= 1
        
        # Quads and Full House
        for f in range (len(frequencies) -1, -1, -1):
            if frequencies[f][1] == 4:
                kickers.remove(frequencies[f][0])
                hand_strength = 8 + frequencies[f][0] / 100
                for k in range(min(len(kickers), 1)):
                    hand_strength += kickers[-(k+1)] / 100 ** (k+2)
                return hand_strength
            if frequencies[f][1] == 3:
                for kf in range (len(frequencies) -1, -1, -1):
                    if frequencies[kf][1] >= 2 and kf != f:
                        return 7 + frequencies[f][0] / 100 + frequencies[kf][0] / 10000
    
        # Flush
        for f in range (len(unique_suit_frequencies)):
            if unique_suit_frequencies[f] >= 5:
                flush_suit = unique_suits[f]
                flush_cards = []
                for c in range (len(list_of_cards)):
                    if list_of_cards[c][1] == flush_suit:
                        flush_cards.append(list_of_cards[c])
                flush_cards.sort()
                return 6 + flush_cards[-1][0] / 100 + flush_cards[-2][0] / 10000 + flush_cards[-3][0] / 1000000 + flush_cards[-4][0] / 100000000 + flush_cards[-5][0] / 10000000000
        
        # Straight
        higher_end_of_straight = 14
        while higher_end_of_straight >= 5:
            if higher_end_of_straight == 5:
                if 5 in list_of_ranks and 4 in list_of_ranks and 3 in list_of_ranks and 2 in list_of_ranks and 14 in list_of_ranks:
                    return 5.05
                
            else:
                if higher_end_of_straight in list_of_ranks and higher_end_of_straight-1 in list_of_ranks and higher_end_of_straight-2 in list_of_ranks and higher_end_of_straight-3 in list_of_ranks and higher_end_of_straight-4 in list_of_ranks:
                    return 5 + higher_end_of_straight / 100                    
            higher_end_of_straight -= 1
            
        # Trips, Two Pair, and Pair
        for f in range (len(frequencies) -1, -1, -1):
            if frequencies[f][1] == 3:
                kickers.remove(frequencies[f][0])
                hand_strength = 4 + frequencies[f][0] / 100
                for k in range(min(len(kickers), 2)):
                    hand_strength += kickers[-(k+1)] / 100 ** (k+2)
                return hand_strength
            if frequencies[f][1] == 2:
                kickers.remove(frequencies[f][0])
                for kf in range (len(frequencies) -1, -1, -1):
                    if frequencies[kf][1] == 2 and kf != f:
                        kickers.remove(frequencies[kf][0])
                        hand_strength = 3 + frequencies[f][0] / 100
                        for k in range(min(len(kickers), 1)):
                            hand_strength += kickers[-(k+1)] / 100 ** (k+2)
                        return hand_strength
                hand_strength = 2 + frequencies[f][0] / 100
                for k in range(min(len(kickers), 3)):
                    hand_strength += kickers[-(k+1)] / 100 ** (k+2)
                return hand_strength
                    
        # High Card
        hand_strength = 1
        for k in range(min(len(kickers), 5)):
            hand_strength += kickers[-(k+1)] / 100 ** (k+1)
        return hand_strength

"""
aces = Calculations([(14, 'Spade'), (13, 'Spade'), (12, 'Spade'), (11, 'Spade'), (9, 'Spade')])
hand_stats = aces.calculate_current_hand_statistics()
draw_stats = aces.calculate_draws()
print(draw_stats)
if draw_stats is not None:
    for hand in draw_stats:
        print(f'Chance of {HAND_HIERARCHY.get(hand[0])}: {100 * hand[1] / hand[2]}%')
"""