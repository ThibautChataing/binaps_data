import tqdm
import random
import os

from binaps_data.utils.logs import log


class LineManager:
    nbr_of_one = 0
    lines = []
    labels = []

    def compile_lines(self,
                      nbr_of_rows: int,
                      patterns_manager: object,
                      max_pat_by_line: int,
                      noise: float,
                      split: int,
                      suffix: str,
                      output_dir):
        log.info("Compile line")
        for r in tqdm.trange(nbr_of_rows):
            label = 0 if random.random() <= (split / 100) else 1  # unused if unecessary.
            nbr_pattern = random.randint(1, max_pat_by_line)
            patterns = patterns_manager.get_patterns(nbr_pattern, label)  # only the values

            indice_noise = random.sample(range(1, nbr_of_rows), round(noise*nbr_of_rows))

            line = self.merge_noise_pat(indice_noise, patterns)
            self.nbr_of_one += len(line)

            self.lines.append(line)
            self.labels.append(label)
        return self.save_data(output_dir, suffix)

    def save_data(self, output_dir, suffix: str):
        data_file = os.path.join(output_dir, f"synthetic_data_{suffix}.dat")
        log.info(f"Saving data to {data_file}")
        data_descriptor = open(data_file, 'w')
        for line in tqdm.tqdm(self.lines):
            data_descriptor.write(' '.join(list(map(str, line))) + '\n')

        data_descriptor.close()
        log.info("Saving done")
        return data_file

    @staticmethod
    def merge_noise_pat(noise: list, patterns: list):
        ret = []
        n_set = set(noise)
        p_set = set(patterns)
        p_set.symmetric_difference_update(n_set)  # will keep only the elements that are NOT present in both sets
        return sorted([*p_set])


class LineManagerWithCat(LineManager):
    def save_data(self, output_dir: str, suffix: str):
        data_file = os.path.join(output_dir, f"synthetic_data_{suffix}.dat")
        data_label_file = os.path.join(output_dir, f"synthetic_data_{suffix}.label")

        log.info(f"Saving data to {data_file} and {data_label_file}")
        data_descriptor = open(data_file, 'w')
        data_label_descriptor = open(data_label_file, 'w')
        for i in tqdm.trange(len(self.lines)):
            data_descriptor.write(' '.join(list(map(str, self.lines[i]))) + '\n')
            data_label_descriptor.write(str(self.labels[i]) + '\n')

        data_descriptor.close()
        log.info("Saving done")
        return data_file, data_label_file
