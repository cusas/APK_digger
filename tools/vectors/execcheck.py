#coding:utf8



from .. import *
from VulnerabilityVector import VulnerabilityVector



class ExecCheck(VulnerabilityVector):

        def __init__(self,context):

            self.context = context




        def analyze(self):

            #Runtime exec checking:

            """
                Example Java code:
                    1. Runtime.getRuntime().exec("");
                    2. Runtime rr = Runtime.getRuntime(); Process p = rr.exec("ls -al");

                Example Bytecode code (The same bytecode for those two Java code):
                    const-string v2, "ls -al"
                    invoke-virtual {v1, v2}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;

                #added by heen, ProcessBuilder is used to run command too.
                ProcessBuilder(String... command)
                    Constructs a new ProcessBuilder instance with the specified operating system program and its arguments.
                ProcessBuilder(List<String> command)
                    Constructs a new ProcessBuilder instance with the specified operating system program and its arguments.

                Example Smali:
                    new-instance v1, Ljava/lang/ProcessBuilder;

                    invoke-direct {v1, v0}, Ljava/lang/ProcessBuilder;-><init>([Ljava/lang/String;)V
                    or
                    invoke-direct {v1, v0}, Ljava/lang/ProcessBuilder;-><init>(Ljava/lang/String;)V

                    invoke-virtual {v1}, Ljava/lang/ProcessBuilder;->start()Ljava/lang/Process;

            """

            list_Runtime_exec = []

            path_Runtime_exec = self.context.vmx.get_tainted_packages().search_class_methods_exact_match("Ljava/lang/Runtime;", "exec",
                                                                                            "(Ljava/lang/String;)Ljava/lang/Process;")
            path_Runtime_exec = self.context.filteringEngine.filter_list_of_paths(self.context.d, path_Runtime_exec)

            for i in analysis.trace_Register_value_by_Param_in_source_Paths(self.context.d, path_Runtime_exec):
                if i.getResult()[1] is None:
                    continue
                if i.getResult()[1] == "su":
                    list_Runtime_exec.append(i.getPath())

            #Added by heen
            path_ProcessBuilder_exec1 = self.context.vmx.get_tainted_packages().\
                search_class_methods_exact_match("Ljava/lang/ProcessBuilder;", "<init>", "([Ljava/lang/String;)V")
            path_ProcessBuilder_exec1 = self.context.filteringEngine.\
                filter_list_of_paths(self.context.d, path_ProcessBuilder_exec1)
            path_ProcessBuilder_exec2 = self.context.vmx.get_tainted_packages(). \
                search_class_methods_exact_match("Ljava/lang/ProcessBuilder;", "<init>", "(Ljava/lang/String;)V")
            path_ProcessBuilder_exec2 = self.context.filteringEngine. \
                filter_list_of_paths(self.context.d, path_ProcessBuilder_exec2)

            if path_ProcessBuilder_exec1 or path_ProcessBuilder_exec2 or path_Runtime_exec:
                self.context.writer.startWriter("COMMAND", LEVEL_CRITICAL, "Runtime Command Checking",
                                                "This app is using critical function 'new ProcessBuilder(String[] cmd) or Runtime.getRuntime().exec()##'.\nPlease confirm these following code secions are not harmful:",
                                                ["Command"])

                if path_ProcessBuilder_exec1:
                    self.context.writer.show_Paths(self.context.d, path_ProcessBuilder_exec1)
                if path_ProcessBuilder_exec2:
                    self.context.writer.show_Paths(self.context.d, path_ProcessBuilder_exec2)
                #################


                if path_Runtime_exec:

                    self.context.writer.show_Paths(self.context.d, path_Runtime_exec)


                    if list_Runtime_exec:
                        self.context.writer.startWriter("COMMAND_SU", LEVEL_CRITICAL, "Runtime Critical Command Checking",
                                           "Requesting for \"root\" permission code sections 'Runtime.getRuntime().exec(\"su\")' found (Critical but maybe false positive):",
                                           ["Command"])

                        for path in list_Runtime_exec:
                            self.context.writer.show_Path(self.context.d, path)
            else:
                self.context.writer.startWriter("COMMAND", LEVEL_INFO, "Runtime Command Checking",
                                   "This app is not using critical function 'Runtime.getRuntime().exec(\"...\")'.", ["Command"])







