from capabilities.CapRetrieval import generate_and_store_embeddings, search_code
from capabilities.intQuery import *
# from capabilities.document import process_directory

if __name__ == "__main__":

    
    # generate_and_store_embeddings(path="capabilities")
    # print("Jobs finished")
    # print(search_code(query,2))
    # generate_and_store_structure()
    # print(func_list("interaction.py"))

    # Get the description of a component.
    # desc = get_comp_desc("save_script")
    # print(desc)
    # desc = get_comp_desc("PERSONAS")
    # print(desc)

    # Get the complete code of a component.
    code = get_comp_code("save_script")
    print(code)
