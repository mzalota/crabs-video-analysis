from timeit import default_timer as timer

class MyTimer:

    __start_comment = None  # type: str

    def __init__(self, from_comment = ""):
        self.__start_comment = from_comment
        self.__start_time = timer()
        self.__last_lap_time = self.__start_time

    def lap (self, lap_comment=""):
        this_lap_time = timer()
        since_start = (this_lap_time - self.__start_time)*1000 #in milliseconds
        since_last_lap = (this_lap_time - self.__last_lap_time)*1000 #in milliseconds

        comment = (self.__start_comment + ' ' + lap_comment).strip()
        print("timer: "+comment, str(int(round(since_start,0)))+"ms", str(int(round(since_last_lap,0)))+"ms")

        self.__last_lap_time = this_lap_time



