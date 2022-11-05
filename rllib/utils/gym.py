import gymnasium as gym
from typing import Optional

from ray.util.annotations import DeveloperAPI


@DeveloperAPI
def check_old_gym_env(
    env: Optional[gym.Env] = None, *, step_results=None, reset_results=None
):
    # Check `reset()` results.
    if reset_results is not None:
        if (
            # Result is NOT a tuple?
            not isinstance(reset_results, tuple)
            # Result is a tuple of len!=2?
            or len(reset_results) != 2
            # The second item is a NOT dict (infos)?
            or not isinstance(reset_results[1], dict)
            # Result is a tuple of len=2 and the second item is a dict (infos) and
            # our env does NOT have obs space 2-Tuple with the second space being a
            # dict?
            or (
                env
                and isinstance(env.observation_space, gym.spaces.Tuple)
                and len(env.observation_space.spaces) >= 2
                and isinstance(env.observation_space.spaces[1], gym.spaces.Dict)
            )
        ):
            return True
    # Check `step()` results.
    elif step_results is not None:
        if len(step_results) == 4:
            return True
        elif len(step_results) == 5:
            return False
        else:
            raise ValueError(
                "The number of values returned from `gym.Env.step([action])` must be "
                "either 4 (old gym.Env API) or 5 (new gym.Env API including "
                "`truncated` flags)! Make sure your `step()` method returns: [obs], "
                "[reward], [done], ([truncated])?, and [infos]!"
            )

    else:
        raise AttributeError(
            "Either `step_results` or `reset_results` most be provided to "
            "`check_old_gym_env()`!"
        )
    return False


@DeveloperAPI
def try_import_gymnasium_and_gym():
    gym, old_gym = None, None

    try:
        import gymnasium as gym
    except (ImportError, ModuleNotFoundError) as e:
        pass

    try:
        import gym as old_gym
    except (ImportError, ModuleNotFoundError) as e:
        pass

    if gym is None:
        gym = old_gym

    if gym is None and old_gym is None:
        raise ImportError(
            "Neither `gymnasium` nor `gym` seem to be installed, but one of them is "
            "required for RLlib! Try running `pip install gymnasium` from the "
            "command line."
        )

    return gym if gym is not None else old_gym, old_gym