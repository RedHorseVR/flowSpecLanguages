import xml.etree.ElementTree as ET
from datetime import datetime
import argparse
import sys
import os

VFC_TOKEN = ");" + "//"


class POMLToVFCParser:

    def __init__(self):
        self.vfc_lines = []
        self.indent_level = 0

    def parse(self, poml_content, output_filename="converted.vfc"):
        """Parse POML content and convert to VFC format"""
        self.vfc_lines = []
        self.indent_level = 0

        self._add_header(output_filename)
        try:

            root = ET.fromstring(poml_content)

            self._process_element(root)

            self._add_footer()
        except ET.ParseError as e:
            raise ValueError(f"Invalid POML XML: {e}")

        return "\n".join(self.vfc_lines)

    def _add_header(self, filename="converted.vfc"):
        """Add VFC file header"""
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p - %d:%b:%Y")
        self.vfc_lines.extend(
            [
                ";  IRL FlowCode Version: Version 10.0",
                ";  c1995-2015: Visual Flow Coder by 2LResearch",
                ";",
                f";  File Name : {filename}",
                f";  File Date : {time_str}",
                "",
            ]
        )

    def _process_element(self, element):
        """Process a single XML element"""
        tag = element.tag.lower()
        if tag == "poml":

            for child in element:
                self._process_element(child)

        elif tag == "let":
            # Variable assignment: <let name="var" value="val" />
            name = element.get("name", "")
            value = element.get("value", "")
            self.vfc_lines.append(f'set(name="{name}" value="{value}");')

            self.vfc_lines.append("")
        elif tag == "task":

            self.vfc_lines.append("end();")
            task_text = element.text.strip() if element.text else ""
            self.vfc_lines.append(f"input({task_text});")
        elif tag == "if":

            self.vfc_lines.append("branch( if );")
            condition = element.get("condition", "")
            self.vfc_lines.append(f'path( condition="{condition}");')

            for child in element:
                self._process_element(child)

        elif tag == "for":

            each_var = element.get("each", "")
            in_var = element.get("in", "")
            text = f"for each {each_var}  in {in_var} "
            self.vfc_lines.append(f"loop( {text} );")

            for child in element:
                self._process_element(child)

            self.vfc_lines.append(f"lend( next {each_var} );")
        elif tag == "else if" or tag == "elseif":

            condition = element.get("condition", "")
            self.vfc_lines.append(f'path(if  condition="{condition}");')

            for child in element:
                self._process_element(child)

        elif tag == "else":

            self.vfc_lines.append("path(else);")

            for child in element:
                self._process_element(child)

            self.vfc_lines.append("bend();")
        elif tag == "p":

            text = element.text.strip() if element.text else ""
            self.vfc_lines.append(f"output({text});")

        else:
            text = element.text.strip() if element.text else ""
            regular_text = "<" + element.tag + ">" + text + "</" + element.tag + ">"
            self.vfc_lines.append(f"set({regular_text});")
            for child in element:
                self._process_element(child)

    def _add_footer(self):
        """Add VFC file footer"""
        self.vfc_lines.extend(
            [
                "end();",
                "",
                "",
                "",
                f';{"INSECTA"} EMBEDDED SESSION INFORMATION',
                "; 255 16777215 65280 16777088 16711680 13158600 13158600 0 255 255 9895835 6946660 3289650",
                ";       //   ...",
                "; notepad.exe",
                f';{"INSECTA"} EMBEDDED ALTSESSION INFORMATION',
                "; 1286 256 1272 1162 0 160   632   226    default.key  0",
            ]
        )


def convert_poml_file(input_file, output_file=None):
    """Convert POML file to VFC file"""

    if not os.path.exists(input_file):

        raise FileNotFoundError(f"Input file not found: {input_file}")

    if output_file is None:

        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.vfc"

    try:

        with open(input_file, "r", encoding="utf-8") as f:

            poml_content = f.read()

    except Exception as e:
        raise IOError(f"Error reading input file: {e}")

    parser = POMLToVFCParser()
    vfc_content = parser.parse(poml_content, os.path.basename(output_file))

    try:

        with open(output_file, "w", encoding="utf-8") as f:

            f.write(vfc_content)

    except Exception as e:
        raise IOError(f"Error writing output file: {e}")

    return output_file


def convert_poml_to_vfc(poml_content):
    """Convenience function to convert POML to VFC (for backward compatibility)"""
    parser = POMLToVFCParser()
    return parser.parse(poml_content)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Convert POML files to VFC (Visual Flow Coder) format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
	python POML2VFC.py input.poml
	python POML2VFC.py input.poml -o output.vfc
	python POML2VFC.py input.poml --output custom_name.vfc
	""",
    )
    parser.add_argument("input_file", nargs="?", help="Input POML file path")
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        help="Output VFC file path (default: <input_name>.vfc)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()

    if not args.input_file:

        print("Error: Input POML file is required", file=sys.stderr)
        print("Use --help for usage information")
        sys.exit(1)

    try:

        if args.verbose:

            print(f"Converting {args.input_file} to VFC format...")

        output_file = convert_poml_file(args.input_file, args.output_file)
        if args.verbose:

            print(f"Successfully converted to: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        else:
            print(f"Converted: {args.input_file} -> {output_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":

    main()

#  Export  Date: 01:13:23 PM - 15:Sep:2025.
