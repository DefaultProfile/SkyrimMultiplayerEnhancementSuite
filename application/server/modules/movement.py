class Movement:
    def __init__(self):
        self.positions = {}

    def update_position(self, player_id, position):
        self.positions[player_id] = position

    def get_position(self, player_id):
        return self.positions.get(player_id, None)
