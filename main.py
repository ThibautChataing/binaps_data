import argparse
import random
import tqdm
import datetime
import os

from binaps_data.utils.logs import log as LOG
from binaps_data.pattern import Pattern, PatternValueDealer, PatternWriter


def argument_parser() -> argparse.Namespace:
    # Get argument from command line
    """
    Get argument from command line
    Return [argparse.Namespace]
    """
    LOG.debug("Parsing argument")
    parser = argparse.ArgumentParser(description='Create data for binaps contrastive experiments')
    parser.add_argument('-o', '--output_dir',
                        type=str, default=".", help="Output directory, file will be ./pattern_date.txt and ./label_date.txt")
    parser.add_argument('--nbr_pattern',
                        type=int, default="10", help="Number of pattern to generate inside the data")
    parser.add_argument('--no_intersections',
                        action='store_true', default=False, help="Allow patterns where intersection are not null "
                                                                 "(pattern can inlude, intersect and belong to both category)")
    parser.add_argument('--min_size',
                        type=int, default="2", help="minimum pattern size")
    parser.add_argument('--max_size',
                        type=int, default="5", help="maximum pattern size")
    parser.add_argument('--nbr_of_feature', type=int, default="100",
                        help="Number of feature (pattern will be chosen inside [0,nbr_of_features]")
    parser.add_argument('--categories_off',
                        action='store_true', default=False,
                        help="By default the data will be labeled in two categories, use this argument "
                             "two disable this feature")
    parser.add_argument('--split', type=int, default="50",
                        help="Split between both categories, in percent. "
                             "The value given will be for the first category. The other will be 100-split")


    #parser.add_argument('--overlap_pattern_inclusion',
    #                    action='store_true', default=False, help="Allow patterns include in an other")
    # TODO : To add this feature, we adivce to use the no_intersect mode and then add pattern from other

    #parser.add_argument('--overlap_categorie',
    #                    action='store_true', default=False, help="Allow patterns belonging to both class")
    # TODO : To add this feature, we adivce to use the no_intersect mode and then add pattern from other

    args = parser.parse_args()
    LOG.info("Argument parsed")
    LOG.debug(f"Arguments: {args}")

    return args


def put_label(pattern, split):
    label = 0 if random.random() <= (split / 100) else 1
    pattern.set_label(label)
    return pattern


def no_label(pattern, split):
    return pattern


def main():
    LOG.debug("main")
    today = datetime.datetime.now().strftime("%Y-%m-%dT%Hh%Mm%Ss")
    args = argument_parser()

    patterns = set()
    cpt_pat = 0

    pattern_value_dealer = PatternValueDealer(args.nbr_of_feature, no_intersections=args.no_intersections)

    # If we don"t want categories, we just override the label finding function
    if args.categories_off:
        LOG.info("Category has been disabled")
        set_label = no_label
    else:
        set_label = put_label

    pbar = tqdm.tqdm(args.nbr_pattern)
    while cpt_pat < args.nbr_pattern:
        pattern = Pattern()
        size = random.randint(args.min_size, args.max_size)

        pattern = set_label(pattern, args.split)

        try:
            pattern.values = pattern_value_dealer.get_val(size)
        except ValueError:
            LOG.error(f"Arguments can't be followed. {args.nbr_pattern} patterns has been asked but in with the number "
                      f"of feature, the size of patterns and the no_intersection modes it can't be done. "
                      f"The running has been stopped here")
            break
        patterns.add(pattern)

        if cpt_pat >= len(patterns):  # test duplicate
            continue

        cpt_pat += 1
        pbar.update(1)

    LOG.info(f"{len(patterns)} patterns created")

    pattern_file = os.path.join(args.output_dir, f"pattern_{today}.txt")
    if args.categories_off:
        PatternWriter.write_patterns_only(patterns, pattern_file)
    else:
        label_file = os.path.join(args.output_dir, f"label_{today}.txt")
        PatternWriter.write_patterns_and_labels(patterns, pattern_file, label_file)

    with open(os.path.join(args.output_dir, f'config_{today}.txt'), 'w') as fd:
        fd.write(str(args.__dict__))


if __name__ == "__main__":
    LOG.info("Start")
    main()
    LOG.info("End")
