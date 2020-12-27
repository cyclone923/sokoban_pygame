
class GameState(object):
    def __init__(self, boxes, worker, parent):
        self.boxes = boxes
        self.worker = worker
        self.parent = parent

    def __eq__(self, other):
        return self.boxes == other.boxes and self.worker == other.worker

    def __hash__(self):
        return hash( (self.worker, frozenset(self.boxes)))

    def get_history(self):
        history = []
        current = self
        while current is not None:
            history.append(current.worker)
            current = current.parent
        history.reverse()
        return history