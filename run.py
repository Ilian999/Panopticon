from capabilities.CapRetrieval import generate_and_store_embeddings, search_code
# from capabilities.document import process_directory

if __name__ == "__main__":

    query = "I want to create an ai agent"
    # generate_and_store_embeddings(path="test", excluded_files=None, excluded_dirs=None)
    # print("Jobs finished")
    print(search_code(query,2))
