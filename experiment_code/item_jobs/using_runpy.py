import runpy
a = 1
runpy.run_path("./code_to_run/hello.py")
print("using_runpy.py::a", a)

"""
With `runpy`, we pass in data using the `init_globals` dictionary
"""

runpy.run_path("./code_to_run/hello_and_input_runpy_globals.py",{"a": a})
print("using_runpy.py::a (after running the secondary script)", a)