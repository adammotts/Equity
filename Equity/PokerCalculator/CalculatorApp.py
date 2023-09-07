import kivy
kivy.require('2.2.1')
from kivy.app import App as KIVYAPP
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
import Elements
import CalculatorBackend


RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SUITS = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
HAND_HIERARCHY = {1:"High Card", 2:"Pair", 3:"Two-Pair", 4:"Three of a Kind", 5:"Straight", 6:"Flush", 7:"Full House", 8:"Four of a Kind", 9:"Straight Flush", 10:"Royal Flush"}


CARD_DIMENSIONS = (48/Window.width, 70/Window.height)
FIRST_CARD_POS = (Window.width * 0.05, Window.height * 0.85)


def create_card_posns(first_card_posn):
    list_of_card_posns = []
    for k in range(13):
        list_of_card_posns.append([first_card_posn[0] + Window.width*0.071*k, first_card_posn[1]])
        
    return list_of_card_posns


class RootWidget(RelativeLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.dropdown_manager = Elements.DropdownManager()
        self.calculator_backend = CalculatorBackend.Calculations()
        self.snapzones = self.create_snapzones()
        self.home_screen()
        
    def home_screen(self, instance = None):
        self.clear_widgets()
        
        for snapzone in self.snapzones:
            self.add_widget(snapzone)

        self.drop_down_suits = self.dropdown_manager.create_dropdown(
            'suits_dropdown', size_hint=(0.4, 0.15),
            pos_hint={'center_x': 0.7, 'center_y': 0.72},
            dropdown_option_height=40, options=SUITS,
            on_select=self.update_cards
        )
        self.add_widget(self.drop_down_suits)

        self.stats_window = Label(
                text = "",
                pos_hint={'center_x': 0.15, 'center_y': 0.15},
                size_hint=(0.25,0.18)
            )
        self.add_widget(self.stats_window)

        self.outs_window = Label(
            text = "",
            pos_hint={'center_x': 0.75, 'center_y': 0.15},
            size_hint=(0.25,0.18)
        )
        self.add_widget(self.outs_window)

        reset_button = Button(
            text="Reset All",
            pos_hint={'center_x': 0.3, 'center_y': 0.72},
            size_hint=(0.1,0.1),
            on_release = self.reset_all_cards
        )
        #reset_button.bind(on_release=lambda reset_button: self.home_screen)
        self.add_widget(reset_button)


    def reset_all_cards(self, instance = None):
        for child in self.children[:]:
            if isinstance(child, Elements.DragImage):
                self.reset_card(child)

    def reset_card(self, card):
        if self.isActiveCard(card.value): #this should only ever be called on active cards
            parent_snapzone = card.attached_snap_widget
            card.attached_snap_widget = None
            parent_snapzone.attached_button = None
            card.return_to_default_position()
            

    def create_snapzones(self):
        table1 = Elements.SnapWidget(
                text="1",
                pos_hint={'center_x': 0.3, 'center_y': 0.45},
                size_hint=CARD_DIMENSIONS,
                objname='T1'
            )
        table2 = Elements.SnapWidget(
                text="2",
                pos_hint={'center_x': 0.4, 'center_y': 0.45},
                size_hint=CARD_DIMENSIONS,
                objname='T2'
            )
        table3 = Elements.SnapWidget(
                text="3",
                pos_hint={'center_x': 0.5, 'center_y': 0.45},
                size_hint=CARD_DIMENSIONS,
                objname='T3'
            )
        table4 = Elements.SnapWidget(
                text="4",
                pos_hint={'center_x': 0.6, 'center_y': 0.45},
                size_hint=CARD_DIMENSIONS,
                objname='T4'
            )
        table5 = Elements.SnapWidget(
                text="5",
                pos_hint={'center_x': 0.7, 'center_y': 0.45},
                size_hint=CARD_DIMENSIONS,
                objname='T5'
            )
        hand1 = Elements.SnapWidget(
                text="1",
                pos_hint={'center_x': 0.45, 'center_y': 0.15},
                size_hint=CARD_DIMENSIONS,
                objname='H1'
            )
        hand2 = Elements.SnapWidget(
                text="2",
                pos_hint={'center_x': 0.55, 'center_y': 0.15},
                size_hint=CARD_DIMENSIONS,
                objname='H2'
            )

        return [table1, table2, table3, table4, table5, hand1, hand2]
    
    def isActiveCard(self, value):
        for sz in self.snapzones:
            if sz.attached_button is None:
                continue
            if value == sz.attached_button.value:
                return True
        return False
    
    def create_all_cards_of_one_suit(self, suit):
        if (suit == "Select Option"):
            return
        card_pos_list = create_card_posns(FIRST_CARD_POS)
        for r in range(13):
            x=r+1
            if r == 0:
                x = 14
            if (not self.isActiveCard((x, suit[:-1]))):
                self.add_widget(Elements.DragImage(source=f'../PokerCalculator/Assets/{RANKS[r]}_of_{suit.lower()}.png', snap_widgets=self.snapzones, value = (x, suit[:-1]), size_hint=CARD_DIMENSIONS, original_pos=card_pos_list[r], pos=card_pos_list[r]))

    def update_cards(self, instance, suit):
        # Clear all the current card widgets
        for child in self.children[:]:
            if isinstance(child, Elements.DragImage):
                if not self.isActiveCard(child.value):
                    self.remove_widget(child)
                    
        # Create and add the new card widgets
        self.create_all_cards_of_one_suit(suit)

    def process_snapzone_data(self):
        snapzone_data = {}
        # get current data
        for snapzone in self.snapzones:
            if snapzone.attached_button:
                snapzone_data[snapzone.objname] = snapzone.attached_button.value
            else:
                snapzone_data[snapzone.objname] = None
        hand_data = [snapzone_data["H1"], snapzone_data["H2"], snapzone_data["T1"], snapzone_data["T2"], snapzone_data["T3"], snapzone_data["T4"], snapzone_data["T5"]]

        # if hand is not there, don't calc
        if hand_data[0] is None or hand_data[1] is None:
            self.stats_window.text = ""
            self.outs_window.text = ""
            return

        self.calculator_backend.update_current_cards(hand_data)
        _win, _tie, _loss, _total = self.calculator_backend.calculate_current_hand_statistics()
        _winP = round(_win*100/_total, 1)
        _tieP = round(_tie*100/_total, 1)
        self.stats_window.text = f"Hands Beaten: {_winP}%\nHands Chopped: {_tieP}%"
        
        outs = self.calculator_backend.calculate_draws()
        if outs is None:
            self.outs_window.text = ""
        else:
            outs_text = ""
            for hand in outs:
                if hand[1] == 0:
                    continue
                outs_text += f"{HAND_HIERARCHY.get(hand[0])}: {round(100 * hand[1] / hand[2],1)}%\n"
            self.outs_window.text = outs_text



class MyApp(KIVYAPP):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MyApp().run()