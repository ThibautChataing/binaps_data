import enum
import random
import tqdm
import os

from binaps_data.utils.logs import log


class Category(enum.IntEnum):
    CAT0 = 0
    CAT1 = 1


class Pattern(object):
    values = []
    label = None
    used = 0

    def __init__(self, values: list = [], label=None):
        """
        Args:
            values (list): list of INT representing the pattern
            label: if existing, the label associated to this pattern
        """
        self.values = values
        self.label = label

    def __hash__(self):
        return hash((tuple(self.values), self.label))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.values == other.values and self.label == other.label

    def __repr__(self):
        return f"PATTERN.cat-{self.label}.{self.values}"

    def __str__(self):
        return f"PATTERN.cat-{self.label}.{self.values}"

    def to_write_values(self):
        return ' '.join(list(map(str, self.values)))

    def to_write_label(self):
        return str(self.label.value)

    def set_label(self, label_int: int):
        self.label = Category(label_int)

    def update_use(self, limit=0):
        """
        Update a compteur about the use of this pattern. If a limit is specified and the used is over it return true to alert.
        :rtype: object
        """
        self.used += 1
        if limit and self.used > limit:
            return True
        else:
            return False


class PatternWriter:
    @staticmethod
    def write_patterns_and_labels(pattern_set: set, pattern_file: str, label_file: str):
        log.info(f"Saving pattern to {pattern_file} and label to {label_file}")
        pattern_descriptor = open(pattern_file, 'w')
        label_descriptor = open(label_file, 'w')
        for pat in tqdm.tqdm(pattern_set):
            pattern_descriptor.write(pat.to_write_values() + '\n')
            label_descriptor.write(pat.to_write_label() + '\n')

        pattern_descriptor.close()
        label_descriptor.close()
        log.info("Saving done")

    @staticmethod
    def write_patterns_only(pattern_set: set, pattern_file: str):
        log.info(f"Saving pattern only to {pattern_file}")
        pattern_descriptor = open(pattern_file, 'w')
        for pat in tqdm.tqdm(pattern_set):
            pattern_descriptor.write(pat.to_write_values() + '\n')

        pattern_descriptor.close()
        log.info("Saving done")


class PatternDealerMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class PatternValueDealer(metaclass=PatternDealerMeta):
    nbr_feature = 0
    val = None

    def __init__(self, nbr_feature: int, no_intersections: bool = False):
        log.debug(f"Init pattern dealer with {nbr_feature} features and 'no_intersection' at {no_intersections}")

        self.nbr_feature = nbr_feature

        if no_intersections:
            self.val = [n for n in range(nbr_feature+1)]
            self.get_val = self.no_intersect
        else:
            self.get_val = self.all

    def all(self, size):
        """
        Get randomly with uniforme probability "size" numbre between 1 and "nbr_feature"
        """
        ret = sorted(random.sample(range(1, self.nbr_feature), size), reverse=False)
        return ret

    def no_intersect(self, size):
        """
        Get randomly with uniforme probability "size" numbre between 1 and "nbr_feature" without replacement
        """
        indices = random.sample(range(1, len(self.val)), size)
        ret = []
        for i in sorted(indices, reverse=True):  # remove from the list with pop so we take indice in descending order
            ret.append(self.val.pop(i))

        ret = sorted(ret, reverse=False)
        return ret

    def get_val(self):
        pass


def put_label(pattern, split):
    label = 0 if random.random() <= (split / 100) else 1
    pattern.set_label(label)
    return pattern


def no_label(pattern, split):
    return pattern


class PatternManager:
    patterns = []
    max_using_pattern = -1

    def __init__(self, max_using_pattern):
        self.max_using_pattern = max_using_pattern

    def compile_pattern(self,
                        nbr_of_feature: int,
                        nbr_pattern: int,
                        min_size: int,
                        max_size: int,
                        split: int,
                        output_dir: str,
                        no_intersections: bool,
                        categories_off: bool,
                        today: str) -> set:
        """
        Create all pattern
        :param nbr_of_feature: number of feature from the data to extract pattern
        :param nbr_pattern: total number of pattern wanted
        :param min_size: minimum size of a pattern (usually 2)
        :param max_size: maximum size of a pattern
        :param split: repartition of pattern between the two categories (only use if categories_off = False)
        :param output_dir: output directory to hold all result
        :param no_intersections: specify if all pattern shouldn't have any intersections between themselfs
        :param categories_off: split pattern in two catergorues
        :param today: datetime in str
        :return: set of Pattern
        """
        patterns = set()
        cpt_pat = 0

        pattern_value_dealer = PatternValueDealer(nbr_of_feature, no_intersections=no_intersections)

        # If we don"t want categories, we just override the label finding function
        if categories_off:
            log.info("Category has been disabled")
            set_label = no_label
        else:
            set_label = put_label

        pbar = tqdm.tqdm(nbr_pattern)
        while cpt_pat < nbr_pattern:
            pattern = Pattern()
            size = random.randint(min_size, max_size)

            pattern = set_label(pattern, split)

            try:
                pattern.values = pattern_value_dealer.get_val(size)
            except ValueError:
                log.error(
                    f"Arguments can't be followed. {nbr_pattern} patterns has been asked but in with the number "
                    f"of feature, the size of patterns and the no_intersection modes it can't be done. "
                    f"The running has been stopped here")
                break
            patterns.add(pattern)

            if cpt_pat >= len(patterns):  # test duplicate
                continue

            cpt_pat += 1
            pbar.update(1)

        log.info(f"{len(patterns)} patterns created")

        pattern_file = os.path.join(output_dir, f"pattern_{today}.txt")
        if categories_off:
            PatternWriter.write_patterns_only(patterns, pattern_file)
        else:
            label_file = os.path.join(output_dir, f"label_{today}.txt")
            PatternWriter.write_patterns_and_labels(patterns, pattern_file, label_file)

        self.patterns = [*patterns]  # unpack to list

    def get_patterns(self, nbr_of_pattern):
        pats = []
        indice = random.sample(range(0, len(self.patterns)), nbr_of_pattern)  #  get indice of pattern for this line
        for i in sorted(indice, reverse=True):  # for each indice in decreased order for the pop
            over_limit = self.patterns[i].update_use(self.max_using_pattern)  # update the use of each pattern
            pats.append(self.patterns[i].values)
            if over_limit:  # if a pattern is over the limit of use
                self.patterns.pop(i)

        ret = set()
        for p in pats:
            ret.update(set(p))

        return [*ret]


if __name__ == '__main__':
    p = PatternValueDealer(100000)
    for i in range(1000):
        p.all(100, 3)
        print(p.no_intersect(3))

