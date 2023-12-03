import uuid

class Defaults:
    DEFAULT_DISTANCE_BETWEEN_REDDOTS_MM = 200
    DEFAULT_DRIFTS_STEP_SIZE = 2

    def generateUUID(self):
        return str(uuid.uuid4().fields[-1])[:5]
