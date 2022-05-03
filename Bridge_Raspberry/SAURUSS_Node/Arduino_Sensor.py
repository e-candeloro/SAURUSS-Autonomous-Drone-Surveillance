from SAURUSS_Node.sauruss_Node import Node
from HTTP_Session import Session_Service
import numpy as np
import json


class Arduino_Sensor(Node):
    dist_x = 0
    dist_y = 0

    def __init__(self, MAC):
        super().__init__(MAC)

    def get_distances(self):
        return self.dist_x, self.dist_y

    def get_MAC(self):
        return self.MAC

    def get_coordinates(self):
        return super(Arduino_Sensor, self).get_coordinates()


    def set_MAC(self, MAC):
        super().set_MAC(MAC)

    def get_id(self):
        return super(Arduino_Sensor, self).get_id()

    # This function ask to the SAURUSS server the distances between nodes and home.
    # Because the drone need it for fly at some relative coordinates.
    # The problem is that Tello can't obtains his geographical coordinates from GPS
    # so we need to store these relative distances in the SAURUSS database.
    def set_distances(self, user_name, password, mac):
        distances_matrix = np.array([])
        distances_vector = []
        try:
            if Session_Service.doLogin(user_name, password) == 200:

                JSONObject = json.loads(Session_Service.getDistances())['Distances']

                for i in JSONObject:  # i = {'sensor':x, 'x_axis':y, 'y_axis':z}
                    distances_vector.append(i['sensor'])
                    distances_vector.append(i['x_axis'])
                    distances_vector.append(i['y_axis'])

                distances_matrix = np.array(distances_vector)
                distances_matrix = distances_matrix.reshape(-1, 3)
        except NameError:
            print(NameError)

        print(distances_matrix)
        for i, ids in enumerate(distances_matrix[:, 0]):
            if ids == mac:
                self.dist_x = int(distances_matrix[i, 1]) + 150
                self.dist_y = int(distances_matrix[i, 2]) + 40
                break

    def set_coordinates(self):
        super().set_coordinates()
