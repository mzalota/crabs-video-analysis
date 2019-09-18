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

    KEY_MOUSE_CLICK_EVENT = 97
    KEY_A = 97


    def __init__(self, key_pressed):
        # type: (int) -> UserInput
        self.__key = key_pressed

    def is_quit_command(self):
        if self.__key == ord("q"):
            return True

        if self.__key == ord("Q"):
            return True

        return False

    def is_bad_frame_command(self):
        if self.__key == ord("b"):
            return True

        if self.__key == ord("B"):
            return True

        return False

    def is_next_seefloor_slice_command(self):
        if self.is_key_arrow_right():
            return True
        if self.__key == self.KEY_SPACE:
            return True
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