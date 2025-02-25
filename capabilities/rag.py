import os
import re
import ast
import pickle
import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer

"""
# Example usage:
if __name__ == "__main__":
    rag_framework = RAGFramework()
    # Build and save indices (BM25 and FAISS) via a single function call
    rag_framework.build_and_save_indices(
        directory='capabilities',
        bm25_filepath='bm25_model.pkl',
        faiss_filepath='faiss_index.pkl'
    )
    
    # Execute a hybrid retrieval query with an array of search queries
    query = ["Personas dictionary"]
    topk = 1
    results = rag_framework.retrieve(query, topk=topk)
    print("Hybrid retrieval results:")
    for res in results:
        print(res)

"""

LOG_FILE = "ragcreationerror.log"

class RAGFramework:
    def __init__(self):
        self.data = {}            # Maps file -> parsed components (functions, classes, arrays, dictionaries)
        self.entries = []         # List of search entries (each a dict with fields and a text representation)
        self.corpus = []          # List of text strings for each entry (used for indexing)
        self.bm25 = None          # BM25 model (BM25Okapi)
        self.faiss_index = None   # FAISS index
        self.vectorizer = None    # TfidfVectorizer
       
    def log_error(self, message):
        """Append error messages to the log file."""
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")
       
    def parse_file(self, filepath):
        """
        Parse a file using the ast module (for functions and classes)
        and regex (for arrays and dictionaries).
        Returns a dict with keys: "functions", "classes", "arrays", "dictionaries".
        """
        parsed = {
            "functions": [],      # List of dicts: { "head": ..., "doc": ... }
            "classes": [],        # List of dicts: { "head": ..., "doc": ..., "methods": [ { "head":..., "doc":... } ] }
            "arrays": [],         # List of dicts: { "name":..., "head":..., "doc":... }
            "dictionaries": []    # Similar structure for dictionaries.
        }
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            # Use ast to parse functions and classes
            try:
                tree = ast.parse(source)
            except Exception as e:
                self.log_error(f"AST parse error in {filepath}: {e}")
                tree = None

            # Get source lines for retrieving the signature line
            lines = source.splitlines()
            if tree:
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef):
                        # Top-level function
                        head = lines[node.lineno - 1].strip() if node.lineno - 1 < len(lines) else f"def {node.name}(...)"
                        doc = ast.get_docstring(node)
                        if not doc:
                            self.log_error(f"No documentation found for function '{node.name}' in file {filepath}")
                        parsed["functions"].append({"head": head, "doc": doc or ""})
                    elif isinstance(node, ast.ClassDef):
                        # Class definition
                        class_head = lines[node.lineno - 1].strip() if node.lineno - 1 < len(lines) else f"class {node.name}(...)"
                        class_doc = ast.get_docstring(node)
                        if not class_doc:
                            self.log_error(f"No documentation found for class '{node.name}' in file {filepath}")
                        class_entry = {"head": class_head, "doc": class_doc or "", "methods": []}
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                # Only include methods directly under the class (skip nested functions)
                                method_head = lines[item.lineno - 1].strip() if item.lineno - 1 < len(lines) else f"def {item.name}(...)"
                                method_doc = ast.get_docstring(item)
                                if not method_doc:
                                    self.log_error(f"No documentation found for method '{item.name}' in class '{node.name}' in file {filepath}")
                                class_entry["methods"].append({"head": method_head, "doc": method_doc or ""})
                        parsed["classes"].append(class_entry)
            # Use regex for arrays and dictionaries
            array_pattern = re.compile(r'(?:(?P<doc>""".*?""")\s*)?(?P<var>\w+)\s*=\s*\[.*?\]', re.DOTALL | re.MULTILINE)
            for match in array_pattern.finditer(source):
                var_name = match.group("var")
                doc = match.group("doc")
                head_line = match.group(0).splitlines()[0].strip()
                if not doc:
                    self.log_error(f"No documentation found for array '{var_name}' in file {filepath}")
                    doc = ""
                else:
                    doc = doc.strip('"""').strip()
                parsed["arrays"].append({"name": var_name, "head": head_line, "doc": doc})
            dict_pattern = re.compile(r'(?:(?P<doc>""".*?""")\s*)?(?P<var>\w+)\s*=\s*\{.*?\}', re.DOTALL | re.MULTILINE)
            for match in dict_pattern.finditer(source):
                var_name = match.group("var")
                doc = match.group("doc")
                head_line = match.group(0).splitlines()[0].strip()
                if not doc:
                    self.log_error(f"No documentation found for dictionary '{var_name}' in file {filepath}")
                    doc = ""
                else:
                    doc = doc.strip('"""').strip()
                parsed["dictionaries"].append({"name": var_name, "head": head_line, "doc": doc})
        except Exception as e:
            self.log_error(f"Error processing file {filepath}: {e}")
        return parsed

    def load_data(self, directory):
        """Load and parse all Python files in the given directory."""
        for file in os.listdir(directory):
            if file.endswith('.py'):
                filepath = os.path.join(directory, file)
                # print(f"Scanned file: {filepath}")  # Debug: which files were scanned
                parsed_components = self.parse_file(filepath)
                self.data[filepath] = parsed_components

    def build_entries(self):
        """
        Build a list of entries from the parsed data.
        Each entry is a dictionary with keys:
          - file, type, head, doc, and optionally parent information for methods.
        Also build a corpus list (text for each entry) used for indexing.
        """
        self.entries = []
        self.corpus = []
        for filepath, components in self.data.items():
            # print(f"Building entries for file: {filepath}")  # Debug: file being processed
            # Top-level functions
            for func in components.get("functions", []):
                entry = {
                    "file": filepath,
                    "type": "function",
                    "head": func["head"],
                    "doc": func["doc"]
                }
                text = f"File: {filepath}. Type: function. Head: {func['head']}. Documentation: {func['doc']}."
                self.entries.append(entry)
                self.corpus.append(text)
                # print(f"Generated function entry: {entry}")  # Debug: function entry generated
            # Classes and their methods
            for cls in components.get("classes", []):
                class_entry = {
                    "file": filepath,
                    "type": "class",
                    "head": cls["head"],
                    "doc": cls["doc"]
                }
                class_text = f"File: {filepath}. Type: class. Head: {cls['head']}. Documentation: {cls['doc']}."
                self.entries.append(class_entry)
                self.corpus.append(class_text)
                # print(f"Generated class entry: {class_entry}")  # Debug: class entry generated
                for method in cls.get("methods", []):
                    method_entry = {
                        "file": filepath,
                        "type": "method",
                        "head": method["head"],
                        "doc": method["doc"],
                        "parent": {
                            "head": cls["head"],
                            "doc": cls["doc"]
                        }
                    }
                    method_text = (f"File: {filepath}. Type: method. Head: {method['head']}. Documentation: {method['doc']}."
                                   f" Belongs to class: {cls['head']}. Class documentation: {cls['doc']}.")
                    self.entries.append(method_entry)
                    self.corpus.append(method_text)
                    # print(f"Generated method entry: {method_entry}")  # Debug: method entry generated
            # Arrays
            for arr in components.get("arrays", []):
                entry = {
                    "file": filepath,
                    "type": "array",
                    "name": arr["name"],
                    "head": arr["head"],
                    "doc": arr["doc"]
                }
                text = f"File: {filepath}. Type: array. Name: {arr['name']}. Head: {arr['head']}. Documentation: {arr['doc']}."
                self.entries.append(entry)
                self.corpus.append(text)
                # print(f"Generated array entry: {entry}")  # Debug: array entry generated
            # Dictionaries
            for d in components.get("dictionaries", []):
                entry = {
                    "file": filepath,
                    "type": "dictionary",
                    "name": d["name"],
                    "head": d["head"],
                    "doc": d["doc"]
                }
                text = f"File: {filepath}. Type: dictionary. Name: {d['name']}. Head: {d['head']}. Documentation: {d['doc']}."
                self.entries.append(entry)
                self.corpus.append(text)
                # print(f"Generated dictionary entry: {entry}")  # Debug: dictionary entry generated

    def build_bm25_index(self):
        """Build BM25 model over the corpus (each entry's text)."""
        if self.corpus:
            tokenized_corpus = [doc.split() for doc in self.corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
        else:
            print("Warning: Corpus is empty. BM25 model not built.")

    def build_faiss_index(self):
        """Build FAISS index over the corpus using TF-IDF vectors."""
        if self.corpus:
            self.vectorizer = TfidfVectorizer()
            vectors = self.vectorizer.fit_transform(self.corpus).toarray()
            vectors = np.ascontiguousarray(vectors.astype('float32'))
            dim = vectors.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dim)
            self.faiss_index.add(vectors)
        else:
            print("Warning: Corpus is empty. FAISS index not built.")

    def save_bm25(self, filepath):
        """Save the BM25 model and the entries mapping."""
        if self.bm25 is not None:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'bm25': self.bm25,
                    'entries': self.entries,
                    'corpus': self.corpus
                }, f)
        else:
            print("BM25 model is not built.")

    def save_faiss(self, filepath):
        """Save the FAISS index, vectorizer, and the entries mapping."""
        if self.faiss_index is not None and self.vectorizer is not None:
            data_to_save = {
                "faiss_index": self.faiss_index,
                "vectorizer": self.vectorizer,
                "entries": self.entries,
                "corpus": self.corpus
            }
            with open(filepath, 'wb') as f:
                pickle.dump(data_to_save, f)
        else:
            print("FAISS index or vectorizer is not built.")

    def build_and_save_indices(self, directory, bm25_filepath, faiss_filepath):
        """
        Execute the entire process:
          1. Load and parse files from the directory.
          2. Build entries and corpus from parsed components.
          3. Build BM25 and FAISS indices.
          4. Save the models to specified file paths.
        """
        self.load_data(directory)
        self.build_entries()
        self.build_bm25_index()
        self.build_faiss_index()
        self.save_bm25(bm25_filepath)
        self.save_faiss(faiss_filepath)



    def retrieve(self, queries, topk=1):
        """
        Hybrid retrieval system for structured (exact) and semantic (natural language) search.
        """
        if self.faiss_index is None or self.vectorizer is None:
            print("FAISS index is not built.")
            return []

        dedup_results = {}

        for query in queries:
            query_lower = query.lower().strip()

            # Step 1: **Exact Match Boost for Function/Method Names**
            exact_matches = [
                entry for entry in self.entries
                if query_lower == entry.get("head", "").split("(")[0].lower()
            ]
            if exact_matches:
                return exact_matches[:topk]  # Return early if an exact match is found

            # Step 2: **Identify Query Type**
            is_natural_language = bool(re.search(r"\b(call|execute|use|define|create|instantiate)\b", query_lower))

            # Step 3: **BM25 Scoring for Natural Queries**
            query_tokens = query.split()
            bm25_scores = self.bm25.get_scores(query_tokens)  # Scores for all documents

            # Normalize BM25 scores
            bm25_scores = np.array(bm25_scores)
            if bm25_scores.size > 0:
                bm25_scores = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-8)

            # Step 4: **FAISS Vector Search**
            query_vector = self.vectorizer.transform([query]).toarray().astype('float32')
            distances, indices = self.faiss_index.search(query_vector, topk * 3)

            faiss_scores = np.exp(-distances[0])  # Convert distances to similarity scores

            # Step 5: **Align BM25 Scores with FAISS Results**
            relevant_bm25_scores = np.array([bm25_scores[idx] for idx in indices[0]])  # Select only relevant BM25 scores

            # Step 6: **Merge Scores**
            if is_natural_language:
                combined_scores = (relevant_bm25_scores + faiss_scores) / 2
            else:
                combined_scores = faiss_scores  # Only FAISS for direct lookups

            # Step 7: **Rank Results (Boost Functions & Methods)**
            ranked_results = []
            for idx, score in zip(indices[0], combined_scores):
                entry = self.entries[idx]
                entry_type = entry["type"]
                boost = 1.3 if entry_type in ["function", "method"] else 1.0  # Boost function/method results
                ranked_results.append((entry, score * boost))

            ranked_results.sort(key=lambda x: x[1], reverse=True)

            # Step 8: **Deduplicate & Return**
            for entry, _ in ranked_results[:topk]:
                key = (entry["file"], entry["type"], entry["head"])
                if key not in dedup_results:
                    dedup_results[key] = entry

        return list(dedup_results.values())



