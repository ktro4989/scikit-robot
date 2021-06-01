from cached_property import cached_property

from ..data import spot_urdfpath
from ..model import RobotModel
from .urdf import RobotModelFromURDF


class Spot(RobotModelFromURDF):

    """Spot Robot Model.

    
    """

    def __init__(self, *args, **kwargs):
        super(Spot, self).__init__(*args, **kwargs)
        self.reset_pose()

    @cached_property
    def default_urdf_path(self):
        return spot_urdfpath()

    @cached_property
    def rleg(self):
        pass

    @cached_property
    def lleg(self):
        pass

    @cached_property
    def rfoot(self):
        pass

    @cached_property
    def lfoot(self):
        pass

    def reset_pose(self):
        angle_vector = []
        for link
