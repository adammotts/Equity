import kivy
kivy.require('2.2.1')
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.graphics import Color, Line

from kivy.core.window import Window

class SnapWidget(Label):
    def __init__(self, objname, **kwargs):
        super(SnapWidget, self).__init__(**kwargs)
        self.objname = objname
        self.attached_button = None
        self.border_color = (1,1,1,0.5)
        self.border_thickness = Window.width // 400
    
    def draw_border(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.border_color)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=self.border_thickness)
    
    def on_pos(self, *args):
        self.draw_border()
    def on_size(self, *args):   
        self.draw_border()
        
    def attach_drag_button(self, drag_button):
        parent = self.parent
        # Detach from the previously attached snap_widget, if any
        if self.attached_button:
            self.attached_button.attached_snap_widget = None
            self.attached_button = None

        # Attach to the new DragButton
        if drag_button.attached_snap_widget is not None:
            drag_button.attached_snap_widget.attached_button = None
        self.attached_button = drag_button
        drag_button.attached_snap_widget = self
        
        #change stat window everytime new card is attached
        parent.process_snapzone_data()

class DragImage(Image):
    def __init__(self, snap_widgets=None, value =None, original_pos=None, **kwargs): 
        super(DragImage, self).__init__(**kwargs)
        self.attached_snap_widget = None
        self.long_touch = False
        self.snap_widgets = snap_widgets or []
        self.recent_pos = None
        #self.original_pos = original_pos
        self.is_dragged_to_snap_widget = False
        self.value = value # number suit pair as tuple

    def return_to_default_position(self):
        # maybe this whole Original_pos thing was pointless lol
        #self.pos = self.original_pos
        parent = self.parent
        if parent:
            parent.remove_widget(self)
            DROPDOWN = parent.drop_down_suits
            parent.update_cards(parent, suit=DROPDOWN.text) #gets the suit

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self.recent_pos = self.center_x, self.center_y
            self.is_dragged_to_snap_widget = False
            self.long_touch = False
            return True
        return super(DragImage, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center_x = touch.x
            self.center_y = touch.y

            # Check if the button touches a snap_widget
            for widget in self.snap_widgets:
                if self.collide_widget(widget):
                    self.is_dragged_to_snap_widget = True
                    break
            else:
                self.is_dragged_to_snap_widget = False
            return True
        return super(DragImage, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # If not dragged to a snap_widget, reset to the original position
            if not self.is_dragged_to_snap_widget and self.recent_pos:
                self.center_x, self.center_y = self.recent_pos

            # If dragged to a snap_widget, snap to its center
            elif self.is_dragged_to_snap_widget:
                for widget in self.snap_widgets:
                    if self.collide_widget(widget):
                        touched_widget = widget

                if touched_widget:
                    if touched_widget.attached_button is not None: # replaces current DragImage in snapwidget if there is one
                        touched_widget.attached_button.return_to_default_position()
                    touched_widget.attach_drag_button(self)
                    self.center_x, self.center_y = touched_widget.center_x, touched_widget.center_y
                    


            touch.ungrab(self)
            ##########################################
            
            return True
        return super(DragImage, self).on_touch_up(touch)
    

class DropdownManager:
    def __init__(self):
        self.dropdowns = {}

    def create_dropdown(self, dropdown_id, size_hint, pos_hint, dropdown_option_height, options, on_select=None):
        _dropdown = DropDown()
        _options = options

        for opt in _options:
            btn = Button(text=opt, size_hint_y=None, height=dropdown_option_height)
            btn.bind(on_release=lambda btn: _dropdown.select(btn.text))
            _dropdown.add_widget(btn)

        main_button = Button(
            text="Select Suit",
            size_hint=size_hint,
            pos_hint=pos_hint
        )

        # Set the main_button's text to the selected option when an option is selected
        def set_main_button_text(instance, x):
            main_button.text = x
            if on_select:
                on_select(instance, x)

        main_button.bind(on_release=_dropdown.open)
        _dropdown.bind(on_select=set_main_button_text)

        # Store the dropdown instance with its identifier
        self.dropdowns[dropdown_id] = _dropdown

        return main_button