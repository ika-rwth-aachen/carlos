# System imports
import glob
import os
import sys
import time
import yaml

# Differentiate between windows and linux
try:
    sys.path.append(
        glob.glob(
            "../carla/dist/carla-*%d.%d-%s.egg"
            % (
                sys.version_info.major,
                sys.version_info.minor,
                "win-amd64" if os.name == "nt" else "linux-x86_64",
            )
        )[0]
    )
except IndexError:
    pass

# Carla Import
import carla
from carla import VehicleLightState as vls

# System imports
import argparse
import logging
from numpy import random

# Set Default Values for parameters that can not be set by arguments
DFAULT_ACTOR_ACTIVE_DISTANCE = 1000.0
DEFAULT_RESPAWN_LOWER_BOUND = 25.0
DEFAULT_RESPAWN_UPPER_BOUND = 700.0
DEFAULT_PHYSICS_ENABLE_RADIUS = 70.0
DEFAULT_GLOBAL_DISTANCE_TO_LEADING_VEHICLE = 2.5
DEFAULT_GLOBAL_PERCENTAGE_SPEED_DIFFERENCE = 0.0
DEFAULT_PERCENTAGE_PEDESTRIANS_RUNNING = 0.0
DEFAULT_PERCENTAGE_PEDESTRIANS_CROSSING = 0.0


#########################################################
##################### Main Function #####################
#########################################################
def main():
    # Parse arguments
    args = parseArguments()

    # Parse config file
    if args.config_file != "":
        config = parseConfigFile(args.config_file)
        if config is None:
            logging.error("Can not parse config file")
            sys.exit()

        # As we removed any explicitly given arguments from the config, we can merge the config with the arguments without overwriting any intentional arguments
        args_dict = vars(args).copy()
        args_dict.update(config)
        args = argparse.Namespace(**args_dict)

    # Configure logging
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    # Set up actor lists
    vehicles_list = []
    walkers_list = []
    all_id = []

    # Set up the carla client
    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)
    synchronous_master = False
    random.seed(args.seed if args.seed is not None else int(time.time()))

    ###########################################
    # Try to spawn the actors
    ###########################################
    try:
        # Get the world
        world = client.get_world()

        ###########################################
        # Set up the weather
        ###########################################

        # Get available weather presets from carla
        weather_presets = {
            name: getattr(carla.WeatherParameters, name)
            for name in dir(carla.WeatherParameters)
            if not name.startswith("_")
        }

        # Check if weather config is used (config file only)
        if hasattr(args, "generate_weather") and args.generate_weather:
            print("Generating weather...")

            # Save current weather conditions
            saved_weather = world.get_weather()

            # Set weather by preset
            if args.use_weather_preset:
                print("Setting weather to preset: " + args.weather_preset_name + "\n")
                selected_weather = weather_presets[args.weather_preset_name]

            # Set weather by parameters
            else:
                print("Setting Weather to custom parameters" + "\n")
                selected_weather = carla.WeatherParameters(
                    cloudiness=args.cloudiness,
                    precipitation=args.precipitation,
                    precipitation_deposits=args.precipitation_deposits,
                    sun_altitude_angle=args.sun_altitude_angle,
                    sun_azimuth_angle=args.sun_azimuth_angle,
                    wind_intensity=args.wind_intensity,
                    fog_density=args.fog_density,
                    fog_distance=args.fog_distance,
                    wetness=args.wetness,
                    fog_falloff=args.fog_falloff,
                    dust_storm=args.dust_storm,
                )

            # Apply weather
            world.set_weather(selected_weather)

        ###########################################
        # Set up the traffic behavior
        ###########################################

        # Get the traffic manager
        traffic_manager = client.get_trafficmanager(args.tm_port)

        # All vehicles have to be at least a certain distance apart
        global_distance_to_leading_vehicle = getattr(
            args,
            "global_distance_to_leading_vehicle",
            DEFAULT_GLOBAL_DISTANCE_TO_LEADING_VEHICLE,
        )
        traffic_manager.set_global_distance_to_leading_vehicle(
            global_distance_to_leading_vehicle
        )

        # All vehicles can only differ a certain percentage from their set speed
        global_percentage_speed_difference = getattr(
            args,
            "global_percentage_speed_difference",
            DEFAULT_GLOBAL_PERCENTAGE_SPEED_DIFFERENCE,
        )
        traffic_manager.global_percentage_speed_difference(
            global_percentage_speed_difference
        )

        # Enable hybrid physics mode
        if args.hybrid:
            if not args.hero:
                logging.warning(
                    "You are using hybrid physics mode. However none of the spawned"
                    " vehicles is a hero vehicle. This will result in no vehicles being"
                    " simulated, unless you define a separate hero vehicle."
                )
            traffic_manager.set_hybrid_physics_mode(
                True
            )  # Only actors in a given radius around a hero vehicle are simulated, if there is no hero vehicle, no actors are simulated.

            # Set the spawn radius
            traffic_manager.set_hybrid_physics_radius(
                getattr(args, "physics_enable_radius", DEFAULT_PHYSICS_ENABLE_RADIUS)
            )  # The radius in meters around the hero vehicle in which other actors are simulated

            # Set the actor active distance
            settings = world.get_settings()
            settings.actor_active_distance = getattr(
                args, "actor_active_distance", DFAULT_ACTOR_ACTIVE_DISTANCE
            )
            # Apply world settings
            world.apply_settings(settings)


            # Set Spawn Boundaries
            lower_bound = getattr(args, "respawn_lower_bound", DEFAULT_RESPAWN_LOWER_BOUND)
            upper_bound = getattr(args, "respawn_upper_bound", DEFAULT_RESPAWN_UPPER_BOUND)
            traffic_manager.set_boundaries_respawn_dormant_vehicles(lower_bound, upper_bound)

        # Respawn vehicles that are dormant (outside the range of the hero vehicle)
        if args.respawn:
            traffic_manager.set_respawn_dormant_vehicles(True)

        # Set the seed for the random
        if args.seed is not None:
            traffic_manager.set_random_device_seed(args.seed)
            msg = (
                "Random seed set to %s. This will result in the same traffic every"
                " time."
            )
            logging.warning(msg, str(args.seed))

        # Get world settings
        settings = world.get_settings()

        # Set synchronous or asynchronous mode
        if not args.asynch:
            logging.warning(
                "You are currently in synchronous mode. If you want to use the"
                " traffic manager alogside the ros-bridge (active ticking part)"
                " make sure to start this script with the --asynch argument."
            )
            traffic_manager.set_synchronous_mode(True)
            if not settings.synchronous_mode:
                synchronous_master = True
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = 0.025
            else:
                synchronous_master = False
        else:
            logging.warning(
                "You are currently in asynchronous mode. If this is a traffic"
                " simulation, you could experience some issues. If it's not"
                " working correctly, switch to synchronous mode by using"
                " traffic_manager.set_synchronous_mode(True) or see documentation for"
                " help."
            )

        # Set render mode
        if args.no_rendering:
            settings.no_rendering_mode = True
            logging.info(
                "No rendering mode is enabled. The Scene will not be rendered."
            )

        # Apply world settings
        world.apply_settings(settings)

        # Get blueprints for vehicles and walkers TODO: More fine grained control over the blueprints
        blueprints = get_actor_blueprints(world, args.filterv, args.generationv)
        blueprintsWalkers = get_actor_blueprints(world, args.filterw, args.generationw)

        # Set safe spawning for vehicles
        if args.safe:
            blueprints = [
                x for x in blueprints if x.get_attribute("base_type") == "car"
            ]

        # Sort the blueprints by id
        blueprints = sorted(blueprints, key=lambda bp: bp.id)

        # Check if distribution is requested
        vehicle_distribution_absolute = dict()
        if hasattr(args, 'filter_by_type') and args.filter_by_type:
            # Check if distribution is valid
            if hasattr(args, 'vehicle_distribution') and args.vehicle_distribution is not None:
                if sum(args.vehicle_distribution.values()) != 100:
                    logging.warning("Your Vehicle distribution does not sum to 100%. Vehicles will be spawned in following Priority: Car, Truck, Motorcycle, Bicycle")

                # Get the number of vehicles to spawn from the distribution
                vehicle_distribution_absolute.update((x, round(float(y)/100*args.number_of_vehicles)) for x, y in args.vehicle_distribution.items())
            else:
                raise ValueError(
                    "You have specified a vehicle distribution, but no distribution"
                    " was given. Please specify a distribution."
                )

        # Get spawn points for vehicles
        spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(spawn_points)

        if args.number_of_vehicles < number_of_spawn_points:
            random.shuffle(spawn_points)
        elif args.number_of_vehicles > number_of_spawn_points:
            msg = "requested %d vehicles, but could only find %d spawn points"
            logging.warning(msg, args.number_of_vehicles, number_of_spawn_points)
            args.number_of_vehicles = number_of_spawn_points

        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor

        ###########################################
        # Spawn vehicles
        ###########################################

        # Set up the batch and hero
        batch = []
        hero = args.hero

        # Iterator for vehicle distribution
        current_type_id = 0
        current_type_count = 0

        # Iterate over the spawn points and spawn the vehicles
        for n, transform in enumerate(spawn_points):
            # Spawn only the requested number of vehicles
            if n >= args.number_of_vehicles:
                break

            # If Distribution is requested, get the blueprint from the class
            if hasattr(args, 'filter_by_type') and hasattr(args, 'vehicle_distribution') and args.filter_by_type and args.vehicle_distribution is not None:

                while current_type_id < len(args.vehicle_distribution):
                    # Get the current type
                    current_type = list(args.vehicle_distribution.keys())[current_type_id]

                    # Check if the current type has been spawned enough
                    if current_type_count >= vehicle_distribution_absolute[current_type]:
                        current_type_id += 1
                        current_type_count = 0
                    else:
                        break # Found a type that can be spawned

                # Filter Blueprints by Type
                selected_blueprints = [x for x in blueprints if x.get_attribute("object_type") == current_type]

                if selected_blueprints == []:
                    raise ValueError(
                        "The vehicle distribution is not compatible with the filter."
                    )
                              
                # Increase the current type count
                current_type_count += 1
            else:
                # If no distribution is requested, select all blueprints
                selected_blueprints = blueprints
                
            # Chose a random blueprint and configure it
            blueprint = random.choice(selected_blueprints)

            if blueprint.has_attribute("color"):
                color = random.choice(
                    blueprint.get_attribute("color").recommended_values
                )
                blueprint.set_attribute("color", color)
            if blueprint.has_attribute("driver_id"):
                driver_id = random.choice(
                    blueprint.get_attribute("driver_id").recommended_values
                )
                blueprint.set_attribute("driver_id", driver_id)
            if hero:
                blueprint.set_attribute(
                    "role_name", "hero"
                )  # ATTENTION: Role Name has to be set to hero for the hero to work
                hero = False
            else:
                blueprint.set_attribute("role_name", "generated_vehicle")

            # Spawn the cars and set their autopilot and light state all together
            batch.append(
                SpawnActor(blueprint, transform).then(
                    SetAutopilot(FutureActor, True, traffic_manager.get_port())
                )
            )

        # Apply the batch
        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                logging.error(response.error)
            else:
                vehicles_list.append(response.actor_id)

        # Set automatic vehicle lights update if specified
        if args.car_lights_on:
            all_vehicle_actors = world.get_actors(vehicles_list)
            for actor in all_vehicle_actors:
                traffic_manager.update_vehicle_lights(actor, True)

        ###########################################
        # Spawn Walkers
        ###########################################

        # Specify pedestrian behavior
        percentagePedestriansRunning = getattr(
            args, "percentagePedestriansRunning", DEFAULT_PERCENTAGE_PEDESTRIANS_RUNNING
        )  # how many pedestrians will run
        percentagePedestriansCrossing = getattr(
            args,
            "percentagePedestriansCrossing",
            DEFAULT_PERCENTAGE_PEDESTRIANS_CROSSING,
        )  # how many pedestrians will walk through the road

        # Set Random seed if specified
        if args.seedw:
            world.set_pedestrians_seed(args.seedw)
            random.seed(args.seedw)
            msg = (
                "Random seed for pedestrians set to %s. This will result in the same"
                " pedestrian config all the time."
            )
            logging.warning(msg, str(args.seedw))

        # Define spawn points for walkers randomly
        spawn_points = []
        for i in range(args.number_of_walkers):
            spawn_point = carla.Transform()
            loc = world.get_random_location_from_navigation()
            if loc != None:
                spawn_point.location = loc
                spawn_points.append(spawn_point)

        # Setup batch and walker speed lists
        batch = []
        walker_speed = []

        # Iterate over the spawn points and spawn the walkers
        for spawn_point in spawn_points:
            walker_bp = random.choice(blueprintsWalkers)
            # Set pedestrians to be not invincible
            if walker_bp.has_attribute("is_invincible"):
                walker_bp.set_attribute("is_invincible", "false")
            # Set speed of pedestrians (walking and running)
            if walker_bp.has_attribute("speed"):
                if random.random() > percentagePedestriansRunning:
                    # walking
                    walker_speed.append(
                        walker_bp.get_attribute("speed").recommended_values[1]
                    )
                else:
                    # running
                    walker_speed.append(
                        walker_bp.get_attribute("speed").recommended_values[2]
                    )
            else:
                print("Walker has no speed")
                walker_speed.append(0.0)
            batch.append(SpawnActor(walker_bp, spawn_point))

        # Apply Batch
        results = client.apply_batch_sync(batch, True)

        # Remove walkers, that result in errors
        walker_speed2 = []
        for i in range(len(results)):
            if results[i].error:
                logging.error(results[i].error)
            else:
                walkers_list.append({"id": results[i].actor_id})
                walker_speed2.append(walker_speed[i])
        walker_speed = walker_speed2

        # Get AI walker controllers
        batch = []
        walker_controller_bp = world.get_blueprint_library().find(
            "controller.ai.walker"
        )
        for i in range(len(walkers_list)):
            batch.append(
                SpawnActor(
                    walker_controller_bp, carla.Transform(), walkers_list[i]["id"]
                )
            )
        results = client.apply_batch_sync(batch, True)
        for i in range(len(results)):
            if results[i].error:
                logging.error(results[i].error)
            else:
                walkers_list[i]["con"] = results[i].actor_id

        # Match walker controllers with walkers
        for i in range(len(walkers_list)):
            all_id.append(walkers_list[i]["con"])
            all_id.append(walkers_list[i]["id"])
        all_actors = world.get_actors(all_id)

        # Wait for a tick to ensure client receives the last transform of the walkers we have just created
        if args.asynch or not synchronous_master:
            world.wait_for_tick()
        else:
            world.tick()

        # Initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
        # Set how many pedestrians can cross the road
        world.set_pedestrians_cross_factor(percentagePedestriansCrossing)
        for i in range(0, len(all_id), 2):
            # Start walker
            all_actors[i].start()
            # Set walk to random point
            all_actors[i].go_to_location(world.get_random_location_from_navigation())
            # Max speed
            all_actors[i].set_max_speed(float(walker_speed[int(i / 2)]))

        ###########################################
        # Finish up traffic generation
        ###########################################
        print(
            "Spawned %d vehicles and %d walkers, press Ctrl+C to exit."
            % (len(vehicles_list), len(walkers_list))
        )

        # Run until interrupted by the user
        while True:
            if not args.asynch and synchronous_master:
                world.tick()
            else:
                world.wait_for_tick()

    ###########################################
    # Remove all spawned actors before we quit.
    ###########################################
    finally:
        # Reset weather conditions
        if hasattr(args, "generate_weather") and args.generate_weather:
            print("Resetting Weather")
            world.set_weather(saved_weather)

        # Restore synchronous mode if needed.
        if not args.asynch and synchronous_master:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.no_rendering_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)

        # Destroy vehicles
        print("\ndestroying %d vehicles" % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        # Stop walker controllers (list is [controller, actor, controller, actor ...])
        for i in range(0, len(all_id), 2):
            all_actors[i].stop()

        # Destroy walkers
        print("\ndestroying %d walkers" % len(walkers_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

        time.sleep(0.5)


#########################################################
#################### Helper Functions ###################
#########################################################
def parseArguments():
    """
    Function to parse the arguments from the user

    :return: parsed arguments as namespace
    """

    # Initialize argument parser
    argparser = argparse.ArgumentParser(description=__doc__)

    # Add all possible arguments
    argparser.add_argument(
        "-f",
        "--config_file",
        metavar="F",
        default="",
        help=(
            "Path to the optional config file (json). Set arguments override the"
            " corresponding value in the config file."
        ),
    )
    argparser.add_argument(
        "--host",
        metavar="H",
        default="127.0.0.1",
        help="IP of the host server (default: 127.0.0.1)",
    )
    argparser.add_argument(
        "-p",
        "--port",
        metavar="P",
        default=2000,
        type=int,
        help="TCP port to listen to (default: 2000)",
    )
    argparser.add_argument(
        "-n",
        "--number-of-vehicles",
        metavar="N",
        default=30,
        type=int,
        help="Number of vehicles (default: 30)",
    )
    argparser.add_argument(
        "-w",
        "--number-of-walkers",
        metavar="W",
        default=10,
        type=int,
        help="Number of walkers (default: 10)",
    )
    argparser.add_argument(
        "--safe", action="store_true", help="Avoid spawning vehicles prone to accidents"
    )
    argparser.add_argument(
        "--filterv",
        metavar="PATTERN",
        default="vehicle.*",
        help='Filter vehicle model (default: "vehicle.*")',
    )
    argparser.add_argument(
        "--generationv",
        metavar="G",
        default="All",
        help=(
            'restrict to certain vehicle generation (values: "1","2","All" - default:'
            ' "All")'
        ),
    )
    argparser.add_argument(
        "--filterw",
        metavar="PATTERN",
        default="walker.pedestrian.*",
        help='Filter pedestrian type (default: "walker.pedestrian.*")',
    )
    argparser.add_argument(
        "--generationw",
        metavar="G",
        default="2",
        help=(
            'restrict to certain pedestrian generation (values: "1","2","All" -'
            ' default: "2")'
        ),
    )
    argparser.add_argument(
        "--tm-port",
        metavar="P",
        default=8000,
        type=int,
        help="Port to communicate with TM (default: 8000)",
    )
    argparser.add_argument(
        "--asynch", action="store_true", help="Activate asynchronous mode execution"
    )
    argparser.add_argument(
        "--hybrid", action="store_true", help="Activate hybrid mode for Traffic Manager"
    )
    argparser.add_argument(
        "-s",
        "--seed",
        metavar="S",
        type=int,
        help="Set random device seed and deterministic mode for Traffic Manager",
    )
    argparser.add_argument(
        "--seedw",
        metavar="S",
        default=0,
        type=int,
        help="Set the seed for pedestrians module",
    )
    argparser.add_argument(
        "--car-lights-on",
        action="store_true",
        default=False,
        help="Enable automatic car light management",
    )
    argparser.add_argument(
        "--hero",
        action="store_true",
        default=False,
        help="Set one of the vehicles as hero",
    )
    argparser.add_argument(
        "--respawn",
        action="store_true",
        default=False,
        help="Automatically respawn dormant vehicles (only in large maps)",
    )
    argparser.add_argument(
        "--no-rendering",
        action="store_true",
        default=False,
        help="Activate no rendering mode",
    )

    return argparser.parse_args()


def parseConfigFile(config_file_path):
    """
    Function to load the config file and parse it

    :param config_file_path: Path to the config file
    :return: failure code
    """

    # Check if filepath is global or relative
    if not config_file_path.startswith("/"):
        config_file_path = os.path.join(os.getcwd(), config_file_path)

    # Check if file exists
    if not os.path.exists(config_file_path):  #
        logging.error("Config file not found")
        return None

    # Check if file is a yml file
    if not config_file_path.endswith(".yml"):
        logging.error("Config file is not a yml file")
        return None

    # Parse config file
    config = yaml.safe_load(open(config_file_path, "r"))

    # Get arguments with sys.argv to check which arguments were explicitly set
    given_args = sys.argv[1:]
    given_args_dict = dict()
    flag = None

    # Set arguments to True if they do not have any value
    for arg in given_args:
        if arg.startswith('-'):
            flag = arg.lstrip('-')
            given_args_dict[flag] = True
        else:
            if flag:
                given_args_dict[flag] = arg
                flag = None

    # catch special cases: replace p with port, n with number-of-vehicles, w with number-of-walkers and s with seed
    if "p" in given_args_dict.keys():
        given_args_dict["port"] = given_args_dict["p"]
        del given_args_dict["p"]
    if "n" in given_args_dict.keys():
        given_args_dict["number-of-vehicles"] = given_args_dict["n"]
        del given_args_dict["n"]
    if "w" in given_args_dict.keys():
        given_args_dict["number-of-walkers"] = given_args_dict["w"]
        del given_args_dict["w"]
    if "s" in given_args_dict.keys():
        given_args_dict["seed"] = given_args_dict["s"]
        del given_args_dict["s"]

    # Prettyprint config dict, mark explicitly set arguments in red
    print("\nParsed config file:")
    for key, value in config.items():
        if key in given_args_dict.keys():
            print(
                "\033[91m {:<20} {:<20} {:<20} \033[0m".format(
                    key,
                    str(given_args_dict[key]),
                    "[argument overwrites config_file value]",
                )
            )
        else:
            print(" {:<20} {:<20}".format(key, str(value)))
    print("\n")

    # Delete keys from config dict if they were explicitly set by user
    for key in given_args_dict.keys():
        if key in config.keys():
            del config[key]

    return config


def get_actor_blueprints(world, filter, generation):
    """
    Function to get actor blueprints

    :param world: Carla world object
    :param filter: Filter for actor types
    :param generation: Generation of the actors (1,2 or "all")
    :return: List of actor blueprints
    """
    bps = world.get_blueprint_library().filter(filter)

    if str(generation).lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [
                x for x in bps if int(x.get_attribute("generation")) == int_generation
            ]
            return bps
        else:
            logging.warning("Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        logging.warning("Actor Generation is not valid. No actor will be spawned.")
        return []


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("\ndone.")
