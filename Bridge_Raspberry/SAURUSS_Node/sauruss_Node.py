class Node:
    node_id = None
    MAC = None
    lat, lon = 0, 0
    dist_x = 0
    dist_y = 0

    def __init__(self, node_id):
        self.node_id = node_id

    def get_id(self):
        return self.node_id

    def set_MAC(self, MAC):
        self.MAC = MAC

    def get_MAC(self):
        return self.MAC

    def get_distances(self):
        return self.dist_x, self.dist_y

    def get_coordinates(self):
        return self.lat, self.lon

    def set_coordinates(self):
        pass

    def set_distances(self,user_name, password, mac):
        pass
