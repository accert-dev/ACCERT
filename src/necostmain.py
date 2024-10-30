import os
import sys
import json

from input_processor import parse_son_input

if __name__ == "__main__":
    code_folder = os.path.dirname(os.path.abspath(__file__))
    necost_path = os.path.abspath(os.path.join(code_folder, os.pardir))
    user_input = sys.argv[2]

    if os.path.exists(user_input):
        input_path = os.path.abspath(user_input)
    else:
        print('NE-COST did not find the input file {}'.format(user_input))
        raise SystemExit

    # Parse the input (str->dict)
    res = parse_son_input(input_path, necost_path)

    # Save output to file (for verification only)
    json_formatted_str = json.dumps(res, indent=4)
    with open("output.json", "w") as f:
        f.write(json_formatted_str)
