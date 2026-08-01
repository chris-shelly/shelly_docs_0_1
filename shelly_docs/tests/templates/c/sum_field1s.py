from pathlib import Path
output_filepath = Path("sum.txt")
print("job::sum_field1s.py:: current path", output_filepath.absolute())
print("job::sum_field1s.py:: query", query)

output_filepath.touch()

output_filepath.write_text(str(query.get("results")))