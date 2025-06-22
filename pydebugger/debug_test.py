from cleaner import DebugCleaner

lines = [
    "debug(a=1, debug=1)",
    "debug(debug=1)",
    "debug(a=1, debug=1, b=2)",
    "debug(foo=bar, debug=verbose)",  # should remain unchanged
]

manager = DebugCleaner()
for line in lines:
    new_line, changed = manager.process_line(line, action="clean")
    print("OLD:", line)
    print("NEW:", new_line)
    print("CHANGED:", changed)
    print("------")
