import tqdm
import random
import os
import logging

log = logging.getLogger('main')


class LineManager:
    """
    Manage lines for the synthetic DB
        nbr_of_one : count the number of one put inside the DB to calculate sparsity later
        lines      : hold created lines
        labels     : hold associated labels if needed
    """
    nbr_of_one = 0
    lines = []
    labels = []

    def __init__(self):
        self.nbr_of_one = 0
        self.lines = []
        self.labels = []

    def compile_lines(self,
                      nbr_of_rows: int,
                      nbr_of_feature: int,
                      patterns_manager: object,
                      max_pat_by_line: int,
                      noise: float,
                      split: int,
                      suffix: str,
                      output_dir,
                      disable_tqdm: bool) -> str:
        """

        :param nbr_of_rows: number of rows/lines to create
        :param patterns_manager: pattern manager to reach pattern
        :param max_pat_by_line: maximum number of pattern inside one line
        :param noise: noise to add to each line. Noise can be addition of one or switching one to zero
        :param split: percentage(0-100) of the 0 categorty
        :param suffix: suffixe for output's files
        :param output_dir: output directory
        :return: string or tuple of string, name(s) or output files
        """
        log.info("Compile line")
        for r in tqdm.trange(nbr_of_rows, disable=disable_tqdm):
            label = 0 if random.random() <= (split / 100) else 1  # unused if unecessary.
            nbr_pattern = random.randint(1, max_pat_by_line+1)
            patterns = patterns_manager.get_patterns(nbr_pattern, label)  # only the values

            indice_noise = random.sample(range(1, nbr_of_feature+1), round(noise*nbr_of_feature))

            line = self.merge_noise_pat(indice_noise, patterns)
            self.nbr_of_one += len(line)

            self.lines.append(line)
            self.labels.append(label)
        return self.save_data(output_dir, suffix, disable_tqdm)

    def save_data(self, output_dir: str, suffix: str, disable_tqdm: bool) -> str:
        """
        Save lines inside a file
        :param output_dir: path to output directory
        :param suffix: suffix to add to output files
        :return: name of output file
        """
        data_file = os.path.join(output_dir, f"synthetic_data_{suffix}.dat")
        log.info(f"Saving data to {data_file}")
        data_descriptor = open(data_file, 'w')
        for line in tqdm.tqdm(self.lines, disable=disable_tqdm):
            data_descriptor.write(' '.join(list(map(str, line))) + '\n')

        data_descriptor.close()
        log.info("Saving done")
        return data_file

    @staticmethod
    def merge_noise_pat(noise: list, patterns: list) -> list:
        """
        Merge noise and pattern to form a complete line
        :param noise: list of int where a noise will be applied (adding 1 if it was 0 or switching a 1 to a 0 is it was a 1)
        :param patterns: list of int where 1 has been put in the line by patterns
        :return: the line
        """
        ret = []
        n_set = set(noise)
        p_set = set(patterns)
        p_set.symmetric_difference_update(n_set)  # will keep only the elements that are NOT present in both sets
        return sorted([*p_set])


class LineManagerWithCat(LineManager):
    """
    Son of LineManager, created to manage categories for supervised learning
    """
    def save_data(self, output_dir: str, suffix: str, disable_tqdm: bool) -> tuple:
        data_file = os.path.join(output_dir, f"synthetic_data_{suffix}.dat")
        data_label_file = os.path.join(output_dir, f"synthetic_data_{suffix}.label")

        log.info(f"Saving data to {data_file} and {data_label_file}")
        data_descriptor = open(data_file, 'w')
        data_label_descriptor = open(data_label_file, 'w')
        for i in tqdm.trange(len(self.lines), disable=disable_tqdm):
            data_descriptor.write(' '.join(list(map(str, self.lines[i]))) + '\n')
            data_label_descriptor.write(str(self.labels[i]) + '\n')

        data_descriptor.close()
        log.info("Saving done")
        return data_file, data_label_file
