import capabilities.Agent as agent
# from capabilities import runchat
from capabilities.chatSetups import *
from capabilities.interaction import *
    
if __name__ == "__main__":
    # coder_agent = agent.CreateAgent(chat_name="a2", preset="coder")
    # exe_coder_agent = agent.CreateAgent(chat_name="coder1", preset="exe_Coder")
    # run.exe_chat(exe_coder_agent)
    # testAgent = agent.CreateAgent(chat_name="testCandQ", preset="codeAndQuery")
    testAgent = agent.CreateAgent(chat_name="testQuery1", preset="codeAndQuery")
    code_and_query_chat(testAgent)
    # print(search_and_import_function("save_script"))

