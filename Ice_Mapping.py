from shapely import Point
from shapely import Polygon
from shapely import LineString

from enum import Enum

neutral_zone = Polygon(((-25,42.5), (-25,-42.5), (25,42.5), (25,-42.5)))
left_high_danger_zone = Polygon(((-89,6),(-89,-6),(-69,-22),(-54,-22),(-54,22,),
    (-69,22)))
left_netfront_zone = Polygon(((-89,6),(-89,-6),(-83,-6),(-83,6)))
left_distance_shot_zone = Polygon(((-54,-22), (-25.5,-42.5),(-25.5,42.5),
    (-54,22)))
left_behind_net_zone = Polygon(((-89,6),(-100,6),(-100,-6),(-89,-6)))
left_corners_point = Point(-89,0)

right_high_danger_zone = Polygon(((89,6),(89,-6),(69,-22),(54,-22),(54,22,),
    (69,22)))
right_netfront_zone = Polygon(((89,6),(89,-6),(83,-6),(83,6)))
right_distance_shot_zone = Polygon(((54,-22), (25.5,-42.5),(25.5,42.5),
    (54,22)))
right_behind_net_zone = Polygon(((-89,6),(-100,6),(-100,-6),(-89,-6)))
right_corners_point = Point(-89,0)

class zone_id(Enum):
    NEUTRAL_ZONE = 0
    LEFT_DISTANCE = 1
    LEFT_HIGH_DANGER = 2
    LEFT_NETFRONT = 3
    LEFT_BEHIND_NET = 4
    LEFT_CORNERS = 5
    LEFT_OUTSIDE = 6
    RIGHT_DISTANCE = 7
    RIGHT_HIGH_DANGER = 8
    RIGHT_NETFRONT = 9
    RIGHT_BEHIND_NET = 10
    RIGHT_CORNERS = 11
    RIGHT_OUTSIDE = 12

def event_point_get_zone(point : Point=None) -> zone_id:

    # first determine left or right side of the ice, left being away start side.
    if point.x < -25.5:

        # now use greedy to determine zone starting with smallest closest to net
        if left_netfront_zone.contains(point):
            return zone_id.LEFT_NETFRONT
        if left_behind_net_zone.contains(point):
            return zone_id.LEFT_BEHIND_NET
        if left_high_danger_zone.contains(point):
            return zone_id.LEFT_HIGH_DANGER
        if left_distance_shot_zone.contains(point):
            return zone_id.LEFT_DISTANCE
        if point.x < left_corners_point.x:
            return zone_id.LEFT_CORNERS
        else:
            return zone_id.LEFT_OUTSIDE
        
    # right size (home side)
    elif point.x > 25.5:
        if right_netfront_zone.contains(point):
            return zone_id.RIGHT_NETFRONT
        if right_behind_net_zone.contains(point):
            return zone_id.RIGHT_BEHIND_NET
        if right_high_danger_zone.contains(point):
            return zone_id.RIGHT_HIGH_DANGER
        if right_distance_shot_zone.contains(point):
            return zone_id.RIGHT_DISTANCE
        if point.x < right_corners_point.x:
            return zone_id.RIGHT_CORNERS
        else:
            return zone_id.RIGHT_OUTSIDE
        
    # otherwise must be in neutral zone
    else:
        return zone_id.NEUTRAL_ZONE