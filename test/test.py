import logging
import tqdm
import gc

from binaps_data.main import main
from binaps_data.utils.logs import set_logger
# nbr_rows, nbr_feature, nbr_pattern, noise, split
runs = [
    [1000, 1000, 10, 0.001, 50, "--no_intersections"],
    [10000, 1000, 10, 0.001, 50, "--no_intersections"],
    [100000, 1000, 10, 0.001, 50, "--no_intersections"],
    [10000, 10000, 10, 0.001, 50, "--no_intersections"],
    [100000, 10000, 10, 0.001, 50, "--no_intersections"],
    [100000, 100000, 10, 0.001, 50, "--no_intersections"],
    [1000, 1000, 10, 0.001, 50, "--no_intersections"],
    [100000, 100000, 500, 0.001, 50, "--no_intersections"],
    [1000, 1000, 10, 0.05, 50, "--no_intersections"],
    [100000, 100000, 500, 0.05, 50, "--no_intersections"],
    [1000, 1000, 10, 0.001, 75, "--no_intersections"],
    [100000, 100000, 500, 0.001, 75, "--no_intersections"],
    [1000, 1000, 10, 0.001, 50, "--categories_off"],
    [10000, 1000, 10, 0.001, 50, "--categories_off"],
    [100000, 1000, 10, 0.001, 50, "--categories_off"],
    [10000, 10000, 10, 0.001, 50, "--categories_off"],
    [100000, 10000, 10, 0.001, 50, "--categories_off"],
    [100000, 100000, 10, 0.001, 50, "--categories_off"],
    [1000, 1000, 10, 0.001, 50, "--categories_off"],
    [100000, 100000, 500, 0.001, 50, "--categories_off"],
    [1000, 1000, 10, 0.05, 50, "--categories_off"],
    [100000, 100000, 500, 0.05, 50, "--categories_off"],
    [1000, 1000, 10, 0.001, 75, "--categories_off"],
    [100000, 100000, 500, 0.001, 75, "--categories_off"]
]


if __name__ == '__main__':
    set_logger('../output/last_run.log', logging.DEBUG)
    log = logging.getLogger('main')
    for r in tqdm.tqdm(runs):
        argument = f"-o ../output --nbr_of_rows {r[0]} --nbr_of_feature {r[1]} --nbr_pattern {r[2]} --noise {r[3]} " \
                   f"--split {r[4]} {r[5]} --disable_tqdm"
        main(argument.split())


