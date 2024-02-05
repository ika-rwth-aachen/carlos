import sys
import glob
import os
import sys
import argparse

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='carla-simulator',
        help='IP of the host server (default: carla-simulator)')
    argparser.add_argument(
        '--role_name',
        metavar='R',
        default='ego_vehicle',
        help='Name of vehicle to wait')
    argparser.add_argument(
        '--role_name_list',
        metavar='RL',
        default=None,
        help='List of vehicle to wait')
    
    args = argparser.parse_args()

    if args.role_name_list:
        role_names = args.role_name_list.split(",")
    else: 
        role_names = [args.role_name]

    client = carla.Client(args.host, 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    world.wait_for_tick()

    is_ego_vehicle_spawned = False
    for role_name in role_names:
        actor_list = world.get_actors().filter('vehicle.*')
        for actor in actor_list:
            if actor.attributes.get('role_name') == role_name:
                is_ego_vehicle_spawned = True

        if is_ego_vehicle_spawned:
            print("{} is spawned.".format(role_name))
        else:
            print("Waiting for {} ...".format(role_name))
            return 1
    
    return 0  

if __name__ == '__main__':
    sys.exit(main())
