import enum
import random
import tqdm

from binaps_data.utils.logs import log


class Category(enum.IntEnum):
    CAT0 = 0
    CAT1 = 1


class Pattern(object):
    values = []
    label = None

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
        Get randomly with uniforme probability "size" numbre between 0 and "nbr_feature"
        """
        ret = sorted(random.sample(range(0, self.nbr_feature), size), reverse=False)
        return ret

    def no_intersect(self, size):
        indices = random.sample(range(0, len(self.val)), size)
        ret = []
        for i in sorted(indices, reverse=True):  # remove from the list with pop so we take indice in descending order
            ret.append(self.val.pop(i))

        ret = sorted(ret, reverse=False)
        return ret

    def get_val(self):
        pass


if __name__ == '__main__':
    p = PatternValueDealer(100000)
    for i in range(1000):
        p.all(100, 3)
        print(p.no_intersect(3))

