import os

import launch
import launch_ros.actions
from ament_index_python.packages import get_package_share_directory

def launch_target_speed_publisher(context, *args, **kwargs):
    topic_name = "/carla/" + launch.substitutions.LaunchConfiguration('role_name').perform(context) + "/target_speed"
    data_string = "{'data': " + launch.substitutions.LaunchConfiguration('target_speed').perform(context) + "}"
    return [
        launch.actions.ExecuteProcess(
            output="screen",
            cmd=["ros2", "topic", "pub", topic_name,
                 "std_msgs/msg/Float64", data_string, "--qos-durability", "transient_local"],
            name='topic_pub_target_speed')]

def generate_launch_description():

    # Args that can be set from CLI

    # carla-simualtor args
    host_launch_arg = launch.actions.DeclareLaunchArgument(
        name='host',
        default_value='carla-simulator'
    )

    port_launch_arg = launch.actions.DeclareLaunchArgument(
        name='port',
        default_value='2000'
    )

    timeout_launch_arg = launch.actions.DeclareLaunchArgument(
        name='timeout',
        default_value='10'
    )

    synchronous_mode_wait_launch_arg = launch.actions.DeclareLaunchArgument(
        name='synchronous_mode_wait_for_vehicle_control_command',
        default_value='False'
    )

    fixed_delta_seconds_launch_arg = launch.actions.DeclareLaunchArgument(
        name='fixed_delta_seconds',
        default_value='0.05'
    )

    town_launch_arg = launch.actions.DeclareLaunchArgument(
        name='town',
        default_value='Town10HD'
    )

    # ego_vehicle args
    role_name_launch_arg = launch.actions.DeclareLaunchArgument(
        name='role_name',
        default_value="ego_vehicle"
    )
    
    objects_definition_file_launch_arg = launch.actions.DeclareLaunchArgument(
        name='objects_definition_file',
        default_value=os.path.join(
        '/sensors.json'
        )
    )

    target_speed_launch_arg = launch.actions.DeclareLaunchArgument(
        name='target_speed',
        default_value='8.33' # in m/s
    )

    # include launch files

    ros_bridge_launch_include = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('carla_ros_bridge'),
                'carla_ros_bridge.launch.py'
            )
        ),
        launch_arguments={
            'host': launch.substitutions.LaunchConfiguration('host'),
            'port': launch.substitutions.LaunchConfiguration('port'),
            'town': launch.substitutions.LaunchConfiguration('town'),
            'timeout': launch.substitutions.LaunchConfiguration('timeout'),
            'synchronous_mode_wait_for_vehicle_control_command': launch.substitutions.LaunchConfiguration('synchronous_mode_wait_for_vehicle_control_command'),
            'fixed_delta_seconds': launch.substitutions.LaunchConfiguration('fixed_delta_seconds')
        }.items()
    )

    carla_spawn_objects_launch_include = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('carla_spawn_objects'),
                'carla_example_ego_vehicle.launch.py'
            )
        ),
        launch_arguments={
            'role_name': launch.substitutions.LaunchConfiguration('role_name'),
            'objects_definition_file': launch.substitutions.LaunchConfiguration('objects_definition_file')
        }.items()
    )

    carla_manual_control_launch_include = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(
                'carla_manual_control'), 'carla_manual_control.launch.py')
        ),
        launch_arguments={
            'role_name': launch.substitutions.LaunchConfiguration('role_name')
        }.items()
    )
    
    carla_ad_agent_launch_include = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(
                'carla_ad_agent'), 'carla_ad_agent.launch.py')
        ),
        launch_arguments={
            'role_name': launch.substitutions.LaunchConfiguration('role_name')
        }.items()
    )

    carla_waypoint_publisher_launch_include = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(
                'carla_waypoint_publisher'), 'carla_waypoint_publisher.launch.py')
        ),
        launch_arguments={
            'host': launch.substitutions.LaunchConfiguration('host'),
            'port': launch.substitutions.LaunchConfiguration('port'),
            'timeout': launch.substitutions.LaunchConfiguration('timeout'),
            'role_name': launch.substitutions.LaunchConfiguration('role_name')
        }.items()
    )

    # Return full launch description

    return launch.LaunchDescription([
        host_launch_arg,
        port_launch_arg,
        timeout_launch_arg,
        synchronous_mode_wait_launch_arg,
        fixed_delta_seconds_launch_arg,
        town_launch_arg,
        objects_definition_file_launch_arg,
        role_name_launch_arg,
        target_speed_launch_arg,
        ros_bridge_launch_include,
        carla_spawn_objects_launch_include,
        carla_manual_control_launch_include,
        carla_ad_agent_launch_include,
        carla_waypoint_publisher_launch_include,
        launch.actions.OpaqueFunction(function=launch_target_speed_publisher)
    ])


if __name__ == '__main__':
    generate_launch_description()
