import argparse
from binaps_data.utils.logs import log as LOG


def argument_parser() -> argparse.Namespace:
    # Get argument from command line
    """
    Get argument from command line
    Return [argparse.Namespace]
    """
    LOG.debug("Parsing argument")
    parser = argparse.ArgumentParser(description='Create data for binaps contrastive experiments')
    parser.add_argument('--nbr_pattern',
                        type=int, default="10", help="Number of pattern to generate inside the data")
    parser.add_argument('--allow_intersections',
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


def main():
    LOG.debug("main")
    args = argument_parser()


if __name__ == "__main__":
    LOG.info("Start")
    main()
    LOG.info("End")
