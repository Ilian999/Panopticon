import inspect
import capabilities
members =  inspect.getmembers(capabilities)
print(members)
# Inspect all functions and classes in the package
for name, obj in inspect.getmembers(capabilities):
    if inspect.isfunction(obj):  # Check if it's a function
        print(f"Function: {name}")
        print(f"Docstring: {inspect.getdoc(obj)}\n")
    elif inspect.isclass(obj):  # Check if it's a class
        print(f"Class: {name}")
        print(f"Docstring: {inspect.getdoc(obj)}\n")