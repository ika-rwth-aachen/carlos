import sys
import subprocess
import random
import glob
import os
import sys
import json
import argparse
import time

import carla

def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='carla-simulator',
        help='IP of the host server (default: carla-simulator)')
    argparser.add_argument(
        '--spawn_point',
        metavar='S',
        default=None,
        help='')
    argparser.add_argument(
        '--town',
        metavar='T',
        default='Town01',
        help='')
    argparser.add_argument(
        '--weather',
        metavar='W',
        default=None,
        help='')
    argparser.add_argument(
        '--vehicle_number',
        metavar='N',
        default=None,
        help='')
    argparser.add_argument(
        '--vehicle_occupancy',
        metavar='P',
        default=None,
        help='')
    argparser.add_argument(
        '--walker_number',
        metavar='W',
        default=None,
        help='')
    
    args = argparser.parse_args()

    config_list = ["--host", args.host]
    tm_list = ["--host", args.host]
    if args.weather:
        config_list.extend(["--weather", args.weather])
    if args.vehicle_number:
        tm_list.extend(["--number-of-vehicles", args.vehicle_number])
    if args.walker_number:
        tm_list.extend(["--number-of-walkers", args.walker_number])

    actor_list = []
    try:
        client = carla.Client(args.host, 2000)
        client.set_timeout(10.0)

        # check if right map is used
        while True:
            time.sleep(0.02)
            world = client.get_world()
            print("Waiting for Town {}...".format(args.town))
            if world.get_map().name == args.town or world.get_map().name == "Carla/Maps/{}".format(args.town):
                break

        # --- set weather ---
        # setup the carla simulation config
        res = subprocess.call(["python", "util/config.py"] + config_list)
        print("Setups in config.py done")

        # --- enable autopilot for main vehicles in sensors.json ---
        # get vehicle info from sensors.json
        if not os.path.exists("/sensors.json"):
            raise RuntimeError(
                "Could not read object definitions from {}".format("/sensors.json"))
        with open("/sensors.json") as handle:
            json_actors = json.loads(handle.read())

        # save all vehicles in list
        vehicles = []
        for actor in json_actors["objects"]:
            actor_type = actor["type"].split('.')[0]
            if actor_type == "vehicle":
                vehicles.append(actor)

        # iterate over vehicles and set autopilot true
        for i, vehicle in enumerate(vehicles):
            # get spawned vehicle
            for actor in world.get_actors():
                if actor.attributes.get('role_name') == vehicle["id"]:
                    player = actor
                    break
            print("{} found - Setting autopilot: True".format(vehicle["id"]))
            player.set_autopilot(True)

        # --- spawn random traffic ---
        spawn_points = world.get_map().get_spawn_points()
        print("Map has {} spawnpoints".format(len(spawn_points)))

        # use vehicle_occupancy if it is set correctly and overwrite vehicle_number from list if it is also set
        if args.vehicle_occupancy:
            vehicle_occupancy = float(args.vehicle_occupancy)
            if 0 < vehicle_occupancy < 1:
                if "--number-of-vehicles" in tm_list:
                    index = tm_list.index("--number-of-vehicles")
                    tm_list[index + 1] = str(int(len(spawn_points)*vehicle_occupancy))
                else:
                    tm_list.extend(["--number-of-vehicles", str(int(len(spawn_points)*vehicle_occupancy))])

        # spawn traffic if it is set (filter out twowheeled vehicle which have no boundingbox)
        if "--number-of-vehicles" in tm_list or "--number-of-walkers" in tm_list:
            subprocess.run(["python", "set_environment.py", "--asynch", "--filterv", 'vehicle.*[!vehicle.bh.crossbike][!vehicle.diamondback.century][!vehicle.harley-davidson.low_rider][!vehicle.gazelle.omafiets][!vehicle.kawasaki.ninja][!vehicle.yamaha.yzf]'] + tm_list)

        while True:
            world.wait_for_tick()
    
    except:
        print('error destroying actors ...')
        for actor in actor_list:
            actor.destroy()
        print('done.')


if __name__ == '__main__':
    try:
        exit(main())

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
    except RuntimeError as e:
        print(e)