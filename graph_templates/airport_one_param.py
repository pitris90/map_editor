import airport_generator
import random

def airport_one_param(num_halls, rnd_seed=0, rnd_values=False):
    # 3-terminal airport with 'num_halls' halls, at least one in each terminal
    if num_halls < 3:
        raise AttributeError(f"Error: wrong value for parameter num_halls = {num_halls}, not >=3.")
    num_halls -= 3  # one default edge for each terminal
    if rnd_seed is not None:
        random.seed(num_halls * rnd_seed)
    hall_sep = [random.randint(0, num_halls), random.randint(0, num_halls)]
    hall_sep.sort()
    halls_in_legs = [hall_sep[0], hall_sep[1]-hall_sep[0], num_halls - hall_sep[1]]
    halls_in_legs = [x+1 for x in halls_in_legs]  # returns the default edges back
    gate_att = dict(target=True, value=1, attack_len=1, blindness=0.0, memory=1)
    hall_att = dict(target=False, memory=4)
    return airport_generator(halls_in_legs, gate_att, hall_att, gates=2, seed=rnd_seed, rnd_values=rnd_values)
