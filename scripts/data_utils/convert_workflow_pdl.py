"""
@241221
- [x] finish overall convertion procedure!
- [x] add hunyuan results

Usage::

    python scripts/data_utils/convert_workflow_pdl.py \
        --llm_name=gpt-4-turbo --output_version=v241127_converted_4turbo \
        --data_version=v241127 --export_version=export-1732628942
"""

import argparse
from data_utils.converter.workflow_pdl_converter import WorkflowPDLConverter


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_version", type=str, default="v241127", help="the dataset to be converted")
    parser.add_argument("--export_version", type=str, default="export-1732628942", help="the export version")

    parser.add_argument("--llm_name", type=str, default="gpt-4o-mini", help="the llm to be used")
    parser.add_argument("--output_version", type=str, default="pdl_converted_20241221_4omini", help="the output version (directory name)")

    parser.add_argument("--max_workers", type=int, default=10, help="the number of workers to be used")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    converter = WorkflowPDLConverter(
        llm_name=args.llm_name,
        output_version=args.output_version,
        data_version=args.data_version,
        export_version=args.export_version,
        max_workers=args.max_workers,
    )
    converter.convert_all()


if __name__ == "__main__":
    main()
