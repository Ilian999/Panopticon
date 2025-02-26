from capabilities.CapRetrieval import generate_and_store_embeddings, search_code
# from capabilities.document import process_directory

if __name__ == "__main__":

    query = "How do i create Files"
    generate_and_store_embeddings(path="test", excluded_files=None, excluded_dirs=None)
    print("Jobs finished")
    # print(search_code(query,2))
