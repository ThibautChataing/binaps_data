import tqdm
import random
import os

from binaps_data.utils.logs import log


class LineManager:
    nbr_of_one = 0
    lines = []

    def compile_lines(self,
                      nbr_of_rows: int,
                      patterns_manager: object,
                      max_pat_by_line: int,
                      noise: float,
                      data_file: str):
        log.info("Compile line")
        for r in tqdm.trange(nbr_of_rows):
            nbr_pattern = random.randint(1, max_pat_by_line)
            patterns = patterns_manager.get_patterns(nbr_pattern)  # only the values

            indice_noise = random.sample(range(1, nbr_of_rows), round(noise*nbr_of_rows))

            line = self.merge_noise_pat(indice_noise, patterns)
            self.nbr_of_one += len(line)

            self.lines.append(line)

        self.save_data(data_file)

    def save_data(self, data_file: str):
        log.info(f"Saving data to {data_file}")
        data_descriptor = open(data_file, 'w')
        for line in tqdm.tqdm(self.lines):
            data_descriptor.write(' '.join(list(map(str, line))) + '\n')

        data_descriptor.close()
        log.info("Saving done")

    @staticmethod
    def merge_noise_pat(noise: list, patterns: list):
        ret = []
        n_set = set(noise)
        p_set = set(patterns)
        p_set.symmetric_difference_update(n_set)  # will keep only the elements that are NOT present in both sets
        return sorted([*p_set])
