from pathlib import Path
import csv
import json
from typing import Any, Dict


#main class for output
class output:
    @staticmethod
    def output_results(results: Dict[str, Any],  result_name: str | None = None) -> None:

        if result_name:

            path = Path(result_name)

            #if the file type matches anoy otheres run that function if it doesnt, throw and error
            try:
                match path.suffix.lower():
                    case '.txt':
                        write_txt(path, results)
                    case '.csv':
                        write_csv(path, results)
                    case '.json':
                        write_json(path, results)
                    case _:
                        print("Unsupported file format. Please use .txt, .csv, or .json")
                print(f"Results saved to {result_name} saved at location {path}")

            #exception error
            except Exception as e:
                print(f"Error saving results: {e}")
                print("Printing results to console instead:")
                for key, value in results.items():
                    print(f"{key}: {value}")
        



def write_txt(path: Path, results: Dict[str, Any]) -> None:
    mode = 'a' if path.exists() else 'w'
    with open(path, mode, encoding="utf-8") as f:
            
        for key, value in results.items():
            if isinstance(value, dict):
                f.write(f"{key}:\n")

                for k, v in value.items():
                    f.write(f"  {k}: {v}\n")
                f.write("\n")
            else:
                f.write(f"{key}: {value}\n")


def write_csv(path: Path, results: Dict[str, Any]) -> None:
    mode = 'a' if path.exists() else 'w'
    with open(path, mode, newline='', encoding="utf-8") as f:
        writer = csv.writer(f)

        if mode == 'w':
            writer.writerow(['URL', 'Status'])
        for key, value in results.items():
            writer.writerow([key, value])


def write_json(path: Path, results: Dict[str, Any]) -> None:
    existing_data = {}
    if path.exists():
        try:
            with open(path, 'r', encoding="utf-8") as f:
                existing_data = json.load(f)
        except:
            pass

    existing_data.update(results)
    
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(results, f, indent=4)


def print_results(results: Dict[str, Any]) -> None:
    print("\nResults:")
    print("=" * 50)

    for key, value in results.items():
        print(f"{key}: {value}")