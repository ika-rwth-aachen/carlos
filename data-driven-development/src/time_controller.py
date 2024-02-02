#!/usr/bin/env python

import sys
import glob
import os
import sys
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
        '--max_simulation_time',
        metavar='T',
        default='300',
        help='Maximal simulation time before server is closed')
    argparser.add_argument(
        '--max_real_time',
        metavar='R',
        default='300',
        help='Maximal real time before server is closed')
    
    args = argparser.parse_args()

    start_time = time.time()

    # connect to server
    client = carla.Client(args.host, 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    world.wait_for_tick()
    delta_elapsed_seconds = world.get_snapshot().timestamp.elapsed_seconds

    while world.get_snapshot().timestamp.elapsed_seconds - delta_elapsed_seconds <= float(args.max_simulation_time) and time.time() - start_time  <= float(args.max_real_time):
        pass
    
    if not world.get_snapshot().timestamp.elapsed_seconds - delta_elapsed_seconds <= float(args.max_simulation_time):
        print("Maximum simulation time of {} reached. Stopping the run...".format(args.max_simulation_time))
    if not time.time() - start_time <= float(args.max_real_time):
        print("Maximum real time of {} reached. Stopping the run...".format(args.max_real_time))

    return 1

if __name__ == '__main__':
    sys.exit(main())