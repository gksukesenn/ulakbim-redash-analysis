import argparse

import pytest

from ulakbim_analysis.main import build_parser, positive_integer


def test_cli_exposes_required_commands() -> None:
    parser = build_parser()

    assert parser.parse_args(["inspect"]).command == "inspect"
    assert parser.parse_args(["validate", "--limit", "10"]).limit == 10
    assert parser.parse_args(
        ["import", "--limit", "10", "--batch-size", "2"]
    ).batch_size == 2
    assert parser.parse_args(["count"]).command == "count"


def test_cli_rejects_non_positive_integer() -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        positive_integer("0")
