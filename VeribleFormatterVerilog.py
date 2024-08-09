import sublime
import sublime_plugin
import subprocess
import threading
import time

import sys
import os #temp file removal
import shlex #shell arg escaping
import tempfile
from functools import singledispatch

SETTINGS_FILE = "VeribleFormatterVerilog.sublime-settings"

class FormatWithVeribleCommand(sublime_plugin.TextCommand):
 
    def run(self, edit):
        view = self.view
        # 获取当前文件路径
        file_path = view.file_name()
        view.run_command("save")

        self.add_comment(view, edit)

        settings = sublime.load_settings(SETTINGS_FILE)

        if file_path:
            # 调用 Verible 格式化 Verilog 代码
            flags_file_path = settings["flags_file_path"]
            if(flags_file_path!=""):
                if(flags_file_path == "example"):
                    flags_file_path = os.path.join(sublime.packages_path(), 'VeribleFormatterVerilog/flags.txt')
                command = ["verible-verilog-format ", "--flagfile", flags_file_path]
            else:
                command = ["verible-verilog-format"]
                command.append("--indentation_spaces="+str(settings["tab_size"]))
                command.append("--column_limit="+str(settings["column_limit"]))
                command.append("--line_break_penalty="+str(settings["line_break_penalty"]))
                command.append("--over_column_limit_penalty="+str(settings["over_column_limit_penalty"]))
                command.append("--wrap_spaces="+str(settings["line_break_penalty"]))

                command.append("--assignment_statement_alignment="+str(settings["assignment_statement_alignment"]))
                command.append("--case_items_alignment="+str(settings["case_items_alignment"]))
                command.append("--class_member_variable_alignment="+str(settings["class_member_variable_alignment"]))
                command.append("--compact_indexing_and_selections="+str(settings["compact_indexing_and_selections"]).lower())
                command.append("--distribution_items_alignment="+str(settings["distribution_items_alignment"]))
                command.append("--enum_assignment_statement_alignment="+str(settings["enum_assignment_statement_alignment"]))
                command.append("--expand_coverpoints="+str(settings["expand_coverpoints"]).lower())
                command.append("--formal_parameters_alignment="+str(settings["formal_parameters_alignment"]))
                command.append("--formal_parameters_indentation="+str(settings["formal_parameters_indentation"]))
                command.append("--module_net_variable_alignment="+str(settings["module_net_variable_alignment"]))
                command.append("--named_parameter_alignment="+str(settings["named_parameter_alignment"]))
                command.append("--named_parameter_indentation="+str(settings["named_parameter_indentation"]))
                command.append("--named_port_alignment="+str(settings["named_port_alignment"]))
                command.append("--named_port_indentation="+str(settings["named_port_indentation"]))
                command.append("--port_declarations_alignment="+str(settings["port_declarations_alignment"]))
                command.append("--port_declarations_indentation="+str(settings["port_declarations_indentation"]))
                command.append("--port_declarations_right_align_packed_dimensions="+str(settings["port_declarations_right_align_packed_dimensions"]).lower())
                command.append("--port_declarations_right_align_unpacked_dimensions="+str(settings["port_declarations_right_align_unpacked_dimensions"]).lower())
                command.append("--struct_union_members_alignment="+str(settings["struct_union_members_alignment"]))
                command.append("--try_wrap_long_lines="+str(settings["try_wrap_long_lines"]).lower())     
                command.append("--wrap_end_else_clauses="+str(settings["wrap_end_else_clauses"]).lower())
            command.append(file_path)
            try:
                encoding = view.settings().get('force_encoding')
                if not encoding:
                    encoding = view.settings().get('origin_encoding')

                # 执行命令
                # st=subprocess.STARTUPINFO()
                # st.dwFlags=subprocess.STARTF_USESHOWWINDOW
                
                # startupinfo = subprocess.STARTUPINFO()
                # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                command_res = ' '.join(command)
                print(command_res)
                # cmd_process = subprocess.Popen(command, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cmd_process = subprocess.run(command_res, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                cmd_output = cmd_process.stdout.decode(encoding).replace('\x0d','')
                cmd_err_output = cmd_process.stderr.decode(encoding)
                if(cmd_err_output==''):
                    self.remove_comment(view, edit, cmd_output)
                    sublime.message_dialog("Verilog 代码格式化成功")
                else:
                    error_message = cmd_err_output.replace(file_path+":","")[1:]
                    sublime.message_dialog("Verilog 代码格式化失败，存在语法错误：\n{}".format(error_message))
            except subprocess.CalledProcessError as e:
                sublime.error_message("Verilog 代码格式化失败：{}".format(e))
        else:
            sublime.error_message("无法获取当前文件路径")

    def add_comment(self, view, edit):
        region_all = sublime.Region(0, view.size())
        file_text = view.substr(region_all)
        lines=file_text.split('\n')

        processed_text = ""
        for i in lines:
            if(i.find(r'`include')!=-1):
                i="//"+i.lstrip()
            processed_text+=i+'\n'
        processed_text=processed_text[:-1]
        view.replace(edit,region_all,processed_text)
        view.run_command("save")

    def remove_comment(self, view, edit, str_formatted):
        region_all = sublime.Region(0, view.size())
        file_text = str_formatted
        lines=file_text.split('\n')

        processed_text = ""
        for i in lines:
            if(i.find(r"`include")!=-1 and i.find("//")!=-1):
                i=i.replace("//","")
            processed_text+=i+"\n"
        processed_text=processed_text[:-1]
        view.replace(edit,region_all,processed_text)
