#!/usr/bin/python
"""necost runtime environment. This file runs from the Workbench application."""

import os
import sys
import argparse

# super import. This module only exists inside the `Workbench/Contents/rte/`
# folder, and will be adjacent to this file once this is moved there.
import workbench


class NECostRuntimeEnvironment(workbench.WorkbenchRuntimeEnvironment):
    """necost-specific runtime environment for NEAMS Workbench"""

    def __init__(self):
        super(NECostRuntimeEnvironment, self).__init__()
        self.executable = None
        self.cleanup = True

    def update_and_print_grammar(self, grammar_path):
        if self.executable is None:
            # if the -grammar flag appears earlier in the arg list than the -e, it won't have been set
            # so, we must parse the argv for that case
            parser_for_grammar = argparse.ArgumentParser()
            parser_for_grammar.add_argument("-e", type=str)
            known, _ = parser_for_grammar.parse_known_args(sys.argv)

            if known is not None:
                self.executable = known.e
            else:
                sys.stderr.write("***Error: The -grammar option requires the -e argument!\n")
                sys.exit(1)

        necost_bin_dir = os.path.dirname(self.executable)
        necost_grammar_path = necost_bin_dir + "/etc/necost.wbg"
        necost_grammar_mtime = os.path.getmtime(necost_grammar_path)

        try:
            workbench_grammar_mtime = os.path.getmtime(grammar_path)
        except OSError:
            # indicate grammar file is 'way old', which will indicate it needs to be updated
            workbench_grammar_mtime = 0

        # Update Workbench's grammar status file
        if necost_grammar_mtime > workbench_grammar_mtime:
            necost_grammar_name = os.path.basename(grammar_path).replace(".wbg", "")

            with open(grammar_path, "w") as workbench_grammar_file:
                workbench_grammar_file.write(
                    f"name='{necost_grammar_name}' redirect='{necost_grammar_path}'"
                )

            print(grammar_path)

    @staticmethod
    def app_name():
        """returns the app's self-designated name"""
        return "necost"

    @staticmethod
    def app_options():
        """list of app-specific options"""
        opts = []

        # TODO add application unique arguments
        return opts

    def prerun(self, options):
        """actions to perform before the run starts"""

        # override values
        options.working_directory = os.path.dirname(options.input)
        # build argument list
        options.input = options.input.replace(options.working_directory + "/", "")

        # call default implementation
        super(NECostRuntimeEnvironment, self).prerun(options)

        # override the working directory removal - don't do it
        self.cleanup = False

    @staticmethod
    def run_args(options):
        """returns a list of arguments to pass to the given executable"""
        # build argument list
        args = ["-i", options.input]

        # TODO add application unique arguments
        return args


if __name__ == "__main__":
    # execute runtime, ignoring first argument (the python script itself)
    NECostRuntimeEnvironment().execute(sys.argv[1:])
