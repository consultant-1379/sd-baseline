#!/usr/bin/env python
"""This module increments the version in the Chart.yaml."""
import sys
import argparse
import logging
import yaml
from common_functions import read_yaml, write_doc_to_yaml, step_version

LOG = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def main():
    """This is the main function that does all of the work."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--appChartDir',
        help="""Full path to the application chart directory
        """,
        required=True
    )
    parser.add_argument(
        '--dryRun',
        help="""Do a dry run of the commands
        """,
        action="store_true",
        required=False
    )
    args = parser.parse_args()

    # Initialize variables
    chart_yaml_file = "%s/Chart.yaml" % args.appChartDir

    # Read yamls
    chart = read_yaml(chart_yaml_file)

    # Update Chart.yaml
    LOG.info("Updating Chart.yaml with new version: " + chart["version"])
    chart["version"] = step_version(chart["version"])
    yaml.dump(chart, sys.stdout, default_flow_style=False)
    if not args.dryRun:
        write_doc_to_yaml(chart, chart_yaml_file)

if __name__ == "__main__":
    main()
