from lib.ImageWindow import ImageWindow


class UserInput():

    KEY_HOME = 2359296
    KEY_END = 2293760
    KEY_PAGE_UP = 2162688
    KEY_PAGE_DOWN = 2228224
    KEY_ARROW_DOWN = 2621440
    KEY_ARROW_UP = 2490368
    KEY_ARROW_RIGHT = 2555904
    KEY_ARROW_LEFT = 2424832
    KEY_SPACE = 32
    KEY_BACKSPACE = 8
    KEY_MINUS = 45
    KEY_PLUS = 43

    #KEY_UNDERSCORE = 95
    #KEY_MOUSE_CLICK_EVENT = 95 #97
    #KEY_A = 97


    def __init__(self, key_pressed):
        # type: (int) -> UserInput
        self.__key = key_pressed

    def is_mouse_click(self):
        if self.__key == ImageWindow.KEY_MOUSE_CLICK_EVENT:
            return True
        return False

    def is_command_quit(self):
        if self.__key == ord("q"):
            return True

        if self.__key == ord("Q"):
            return True

        return False

    def is_command_bad_frame(self):
        if self.__key == ord("b"):
            return True

        if self.__key == ord("B"):
            return True

        return False

    def is_command_zoom(self):
        if self.__key == ord("z"):
            return True

        if self.__key == ord("Z"):
            return True

        return False

    def is_command_fix_red_dot(self):
        if self.__key == ord("r"):
            return True

        if self.__key == ord("R"):
            return True

        return False

    def is_command_contrast(self):
        if self.__key == ord("c"):
            return True

        if self.__key == ord("C"):
            return True

        return False

    def is_next_seefloor_slice_command(self):
        if self.is_key_arrow_right():
            return True
        #if self.__key == self.KEY_SPACE:
        #    return True
        if self.__key == ord("n"):
            return True
        if self.__key == ord("N"):
            return True

        return False

    def is_key_end(self):
        if self.__key == self.KEY_END:
            return True
        return False

    def is_key_home(self):
        if self.__key == self.KEY_HOME:
            return True
        return False

    def is_key_arrow_up(self):
        if self.__key == self.KEY_ARROW_UP:
            return True
        return False

    def is_key_arrow_down(self):
        if self.__key == self.KEY_ARROW_DOWN:
            return True
        return False

    def is_key_arrow_left(self):
        if self.__key == self.KEY_ARROW_LEFT:
            return True
        return False

    def is_key_arrow_right(self):
        if self.__key == self.KEY_ARROW_RIGHT:
            return True
        return False

    def is_key_page_down(self):
        if self.__key == self.KEY_PAGE_DOWN:
            return True
        return False

    def is_key_page_up(self):
        if self.__key == self.KEY_PAGE_UP:
            return True
        return False

    def is_small_step_forward(self):
        if self.__key == self.KEY_SPACE:
            return True
        return False

    def is_small_step_backward(self):
        if self.__key == self.KEY_BACKSPACE:
            return True
        return False

    def is_large_step_forward(self):
        if self.__key == self.KEY_PLUS:
            return True
        return False

    def is_large_step_backward(self):
        if self.__key == self.KEY_MINUS:
            return True
        return False