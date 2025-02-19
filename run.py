# import capabilities.Agent as agent
# # from capabilities import runchat
# import capabilities.runchat as run
# from capabilities.interaction import *
# from capabilities.run import main
# import contextlib
# import io
# if __name__ == "__main__":
#     main()
#     # code_block = """create_file_with_format('example_file', '.txt')"""
#     # output_capture = io.StringIO()
#     # try:
#     #     with contextlib.redirect_stdout(output_capture):
#     #         exec(code_block, globals())
#     #     code_output = output_capture.getvalue().strip()
#     #     print("Execution result:")
#     #     print(code_output)
#     # except Exception as e:
#     #     code_output = f"Error during code execution: {e}"
#     #     print(code_output)
import pydoc
import capabilities

pydoc.help(capabilities)