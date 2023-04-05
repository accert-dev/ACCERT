#!/usr/bin/python
"""accert runtime environment"""

# standard imports
import os
import sys

# super import
import workbench

class accertRuntimeEnvironment(workbench.WorkbenchRuntimeEnvironment):
    """accert-specific runtime environment"""
    def __init__(self):
        """constructor"""

        # call super class constructor
        super(accertRuntimeEnvironment, self).__init__()

    def update_and_print_grammar(self, grammar_path):
        if self.executable == None:            
            import argparse
            # if the -grammar flag appears earlier in the arg list than the -e, it won't have been set
            # so, we must parse the argv for that case
            parser_for_grammar = argparse.ArgumentParser()
            parser_for_grammar.add_argument("-e", type=str)    
            known, unknown = parser_for_grammar.parse_known_args(sys.argv)        
            self.executable = known.e  
            
        if self.executable == None:            
            sys.stderr.write("***Error: The -grammar option requires -e argument!\n")
            sys.exit(1)
        
        accert_bin_dir = os.path.dirname(self.executable)
        accert_dir = accert_bin_dir

        accert_grammar_path = accert_dir+"/etc/accert.wbg"
        
        accert_grammar_mtime = os.path.getmtime(accert_grammar_path)
        try:
            workbench_grammar_mtime = os.path.getmtime(grammar_path)
        except OSError:
            # indicate grammar file is 'way old' 
            # which will indicate it needs to be updated
            workbench_grammar_mtime = 0

        # Update Workbench's grammar status file        
        if accert_grammar_mtime > workbench_grammar_mtime:
            accert_grammar_name = os.path.basename(grammar_path).replace(".wbg","")
            with open(grammar_path,"w") as workbench_grammar_file:
                workbench_grammar_file.write("name='{0}' redirect='{1}'".format(accert_grammar_name, accert_grammar_path))
            print (grammar_path)       
                 
            
        return
    def app_name(self):
        """returns the app's self-designated name"""
        return "accert"

    def app_options(self):
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
        super(accertRuntimeEnvironment, self).prerun(options)

        #  override the working directory removal - dont do it
        self.cleanup = False

    def run_args(self, options):
        """returns a list of arguments to pass to the given executable"""
        # build argument list
        args = ["-i", options.input]

        # TODO add application unique arguments
        return args

if __name__ == "__main__":
    # execute runtime, ignoring first argument (the python script itself)
    accertRuntimeEnvironment().execute(sys.argv[1:])
