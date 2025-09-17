import xml.etree.ElementTree as ET
from datetime import datetime
import argparse
import sys
import os

class POMLToVFCParser:
    def __init__(self):
        self.vfc_lines = []
        self.indent_level = 0
    
    def parse(self, poml_content, output_filename="converted.py.vfc"):
        """Parse POML content and convert to VFC format"""
        self.vfc_lines = []
        self.indent_level = 0
        
        # Add VFC header
        self._add_header(output_filename)
        
        try:
            # Parse XML
            root = ET.fromstring(poml_content)
            
            # Process each element
            self._process_element(root)
            
            # Add footer
            self._add_footer()
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid POML XML: {e}")
        
        return '\n'.join(self.vfc_lines)
    
    def _add_header(self, filename="converted.py.vfc"):
        """Add VFC file header"""
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p - %d:%b:%Y")
        
        self.vfc_lines.extend([
            ";  IRL FlowCode Version: Version 10.0",
            ";  c1995-2015: Visual Flow Coder by 2LResearch",
            ";",
            f";  File Name : {filename}",
            f";  File Date : {time_str}",
            ""
        ])
    
    def _process_element(self, element):
        """Process a single XML element"""
        tag = element.tag.lower()
        
        if tag == 'poml':
            # Root element, process children
            for child in element:
                self._process_element(child)
        
        elif tag == 'let':
            # Variable assignment: <let name="var" value="val" />
            name = element.get('name', '')
            value = element.get('value', '')
            
            # Handle multi-line values (like arrays/objects)
            if '\n' in value:
                # Split multi-line values into multiple set() calls
                lines = value.strip().split('\n')
                first_line = lines[0].strip()
                self.vfc_lines.append(f'set(name="{name}" value="{first_line}");')
                
                # Add remaining lines as separate set() calls
                for line in lines[1:]:
                    line = line.strip()
                    if line and line != ']':  # Skip empty lines and closing brackets
                        self.vfc_lines.append(f'set({line});')
                
                # Add closing bracket if it was on its own line
                if lines[-1].strip() == ']':
                    self.vfc_lines.append('set(]");')
            else:
                self.vfc_lines.append(f'set(name="{name}" value="{value}");')
            
            self.vfc_lines.append('end();')
            self.vfc_lines.append('')
        
        elif tag == 'task':
            # Input task: <task>description</task>
            task_text = element.text.strip() if element.text else ''
            self.vfc_lines.append(f'input({task_text});')
        
        elif tag == 'for':
            # Loop: <for each="item" in="items">
            each_var = element.get('each', '')
            in_var = element.get('in', '')
            self.vfc_lines.append('loop(for each);')
            
            # Process children of loop block
            for child in element:
                self._process_element(child)
            
            # Close the loop
            self.vfc_lines.append('lend();')
        
        elif tag == 'if':
            # Conditional branch: <if condition="expr">
            condition = element.get('condition', '')
            self.vfc_lines.append(f'branch(if  condition="{condition}");')
            self.vfc_lines.append('path();')
            
            # Process children of if block
            for child in element:
                self._process_element(child)
        
        elif tag == 'elseif':
            # ElseIf path: <elseif condition="expr">
            condition = element.get('condition', '')
            self.vfc_lines.append(f'path(condition="{condition}");')
            
            # Process children of elseif block
            for child in element:
                self._process_element(child)
        
        elif tag == 'else':
            # Else path
            self.vfc_lines.append('path(else);')
            
            # Process children of else block
            for child in element:
                self._process_element(child)
            
            # Close the branch
            self.vfc_lines.append('bend();')
        
        elif tag == 'p':
            # Output paragraph: <p>text</p>
            text = element.text.strip() if element.text else ''
            self.vfc_lines.append(f'output({text});')
        
        # Add more element types as needed
        else:
            # Unknown element, process children
            for child in element:
                self._process_element(child)
    
    def _add_footer(self):
        """Add VFC file footer"""
        self.vfc_lines.extend([
            'end();',
            '',
            '',
            '',
            ';INSECTA EMBEDDED SESSION INFORMATION',
            '; 255 16777215 65280 16777088 16711680 13158600 13158600 0 255 255 9895835 6946660 3289650',
            ';       //   ...',
            '; notepad.exe',
            ';INSECTA EMBEDDED ALTSESSION INFORMATION',
            '; 1286 256 1272 1162 0 160   632   226    default.key  0'
        ])

def convert_poml_file(input_file, output_file=None):
    """Convert POML file to VFC file"""
    # Validate input file
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.py.vfc"
    
    # Read POML content
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            poml_content = f.read()
    except Exception as e:
        raise IOError(f"Error reading input file: {e}")
    
    # Parse and convert
    parser = POMLToVFCParser()
    vfc_content = parser.parse(poml_content, os.path.basename(output_file))
    
    # Write VFC content
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
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
  python POML2VFC.py input.poml -o output.py.vfc
  python POML2VFC.py input.poml --output custom_name.vfc
        """
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input POML file path'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Output VFC file path (default: <input_name>.py.vfc)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Check if input file was provided
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

# Example usage and testing
if __name__ == "__main__":
    # Run CLI if called directly
    main()