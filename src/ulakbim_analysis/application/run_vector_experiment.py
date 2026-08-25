from ulakbim_analysis.application.load_vector_experiment import (
    main as load_main,
)
from ulakbim_analysis.application.report_vector_experiment import (
    generate_reports,
)


def main() -> None:
    load_main()
    generate_reports()


if __name__ == "__main__":
    main()
