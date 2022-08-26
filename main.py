import argparse
import json
import datetime
import os
import logging
import gc

from binaps_data.utils.logs import set_logger
from binaps_data.pattern import PatternManager, PatternManagerWithCat
from binaps_data.line import LineManager, LineManagerWithCat

log = logging.getLogger('main')


def argument_parser(cp_args=None) -> argparse.Namespace:
    """
    Get argument from command line or in main
    :param cp_args: possible way to pass arguments to the parser
    :return: [argparse.Namespace]
    """
    log.debug("Parsing argument")
    # Arguments to generate patterns
    parser = argparse.ArgumentParser(description='Create data for binaps contrastive experiments')
    parser.add_argument('-o', '--output_dir',
                        type=str, default=".",
                        help="Output directory, file will be ./pattern_date.txt and ./label_date.txt")
    parser.add_argument('--nbr_pattern',
                        type=int, default="10", help="Number of pattern to generate inside the data")
    parser.add_argument('--no_intersections',
                        action='store_true', default=False, help="Allow patterns where intersection are not null "
                                                                 "(pattern can inlude, intersect and belong to both category)")
    parser.add_argument('--min_size',
                        type=int, default="2", help="minimum pattern size")
    parser.add_argument('--max_size',
                        type=int, default="10", help="maximum pattern size")
    parser.add_argument('--nbr_of_feature', type=int, default="100",
                        help="Number of feature (pattern will be chosen inside [0,nbr_of_features]")
    parser.add_argument('--categories_off',
                        action='store_true', default=False,
                        help="By default the data will be labeled in two categories, use this argument "
                             "two disable this feature")
    parser.add_argument('--split', type=int, default="50",
                        help="Split between both categories, in percent. "
                             "The value given will be for the first category. The other will be 100-split")
    parser.add_argument('--disable_tqdm', action="store_true", default=False,
                        help="Disable tqdm")

    # Arguments to generate lines
    parser.add_argument('--nbr_of_rows', type=int, default="10000",
                        help="Number of row wanted")
    parser.add_argument('--noise', type=float, default="0.001",
                        help="Noise applied to the data (additive and destructive")
    parser.add_argument('--max_using_pattern', type=int, default="0",
                        help="If greater than 0, maximum number of time a pattern will be used to generate data")
    parser.add_argument('--max_pattern_on_a_line', type=int, default="10",
                        help="If positive, maximum number of pattern used to generate one line")
    parser.add_argument('--fill_with_noise', action='store_true', default=False,
                        help="If there is a maximum of use by pattern, this feature allow to fill line only with noise")

    # parser.add_argument('--overlap_pattern_inclusion',
    #                    action='store_true', default=False, help="Allow patterns include in an other")
    # TODO : To add this feature, we adivce to use the no_intersect mode and then add pattern from other

    # parser.add_argument('--overlap_categorie',
    #                    action='store_true', default=False, help="Allow patterns belonging to both class")
    # TODO : To add this feature, we adivce to use the no_intersect mode and then add pattern from other

    args = parser.parse_args(cp_args)
    log.info("Argument parsed")
    log.debug(f"Arguments: {args}")

    return args


def main(cp_args=None):
    # ND indice for column start with 1
    log.debug("main")
    today = datetime.datetime.now().strftime("%Y-%m-%dT%Hh%Mm%Ss")
    args = argument_parser(cp_args)

    # Two mode actuel to create data, with ou withour two categories for supervised learning
    if args.categories_off:
        pattern_manager = PatternManager(max_using_pattern=args.max_using_pattern)
        line_manager = LineManager()
        max_pat_line = args.max_pattern_on_a_line if args.max_pattern_on_a_line < args.nbr_pattern else args.nbr_pattern
    else:
        pattern_manager = PatternManagerWithCat(max_using_pattern=args.max_using_pattern)
        line_manager = LineManagerWithCat()
        max_pat_line = args.max_pattern_on_a_line if args.max_pattern_on_a_line < (args.nbr_pattern/2) else args.nbr_pattern/2

    if args.no_intersections:
        no_inter = "NO_INTER"
    else:
        no_inter = "INTER"

    #  Create all patterns
    pattern_files = pattern_manager.compile_pattern(nbr_of_feature=args.nbr_of_feature,
                                                    nbr_pattern=args.nbr_pattern,
                                                    min_size=args.min_size,
                                                    max_size=args.max_size,
                                                    split=args.split,
                                                    output_dir=args.output_dir,
                                                    no_intersections=args.no_intersections,
                                                    today=today,
                                                    disable_tqdm=args.disable_tqdm)

    #  Compile lines based on patterns. The .dat format is used to speed up process (kind of meta way for binary DB,
    #  we only specified indice of 1. Many place is won because of sparsity)
    data_files = line_manager.compile_lines(nbr_of_rows=args.nbr_of_rows,
                                            patterns_manager=pattern_manager,
                                            max_pat_by_line=max_pat_line,
                                            noise=args.noise,
                                            split=args.split,
                                            suffix=f"{args.nbr_of_rows}_{args.nbr_of_feature}_{args.nbr_pattern}_{args.noise}_{no_inter}_{today}",
                                            output_dir=args.output_dir,
                                            disable_tqdm=args.disable_tqdm)

    config = args.__dict__.copy()
    config["pattern_file"] = pattern_files
    config["data_file"] = data_files
    config["density"] = line_manager.nbr_of_one / (args.nbr_of_feature * args.nbr_of_rows)
    with open(os.path.join(args.output_dir, f'config_{today}.json'), 'w') as fd:
        json.dump(config, fd)

    log.info("Cleaning")
    del pattern_manager
    del line_manager
    gc.collect()

if __name__ == "__main__":
    log = set_logger()
    log.info("Start")
    argument = "-o output --nbr_pattern 100 --min_size 2 --max_size 5 --nbr_of_feature 100 --split 50 " \
               "--nbr_of_rows 100"# --categories_off"
    main(argument.split())
    log.info("End")
