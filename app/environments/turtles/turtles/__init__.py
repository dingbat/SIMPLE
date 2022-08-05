from gym.envs.registration import register

register(
    id='Turtles-v0',
    entry_point='turtles.envs:TurtlesEnv',
)
