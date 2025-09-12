from pathlib import Path
import csv
import json
from typing import Any, Dict, Union, List, Iterable


class output:
    @staticmethod
    def output_results(
        results: Union[Dict[str, Any], List[Any], Iterable[Any]], 
        result_name: str | None = None
    ) -> None:

        def Print_console(r):
#            print("Printing results to console instead:")
#            if isinstance(r, dict):
#                for k, v in r.items():
#                    print(f"{k}: {v}")
#            else:
#                for item in r:
#                    print(item)

            if result_name:
                path = Path(result_name)
                try:
                    match path.suffix.lower():
                        case ".txt":
                            write_txt(path, results)
                        case ".csv":
                            write_csv(path, results)
                        case ".json":
                            write_json(path, results)
                        case _:
                            print("Unsupported file format. Please use .txt, .csv, or .json")
                            Print_console(results)
                            return
                    print(f"Results saved to {result_name} at {path.resolve()}")

                except Exception as e:
                    print(f"Error saving results: {e}")
                    Print_console(results)
            else:
                Print_console(results)


def write_txt(path: Path, results: Union[Dict[str, Any], Iterable[Any]]) -> None:
    mode = "a" if path.exists() else "w"
    with open(path, mode, encoding="utf-8") as f:
        if isinstance(results, dict):
            for key, value in results.items():
                if isinstance(value, dict):
                    f.write(f"{key}:\n")
                    for k, v in value.items():
                        f.write(f"  {k}: {v}\n")
                    f.write("\n")
                else:
                    f.write(f"{key}: {value}\n")
        else:
            for item in results:
                f.write(f"Open: {item}\n")


def write_csv(path: Path, results: Union[Dict[str, Any], Iterable[Any]]) -> None:
    mode = "a" if path.exists() else "w"
    with open(path, mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if isinstance(results, dict):
            if mode == "w":
                writer.writerow(["Key", "Value"])
            for key, value in results.items():
                writer.writerow([key, value])
        else:
            if mode == "w":
                writer.writerow(["Result"])
            for item in results:
                writer.writerow([item])


def write_json(path: Path, results: Union[Dict[str, Any], List[Any], Iterable[Any]]) -> None:
    existing_data = None
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            pass

    if isinstance(existing_data, dict) and isinstance(results, dict):
        existing_data.update(results)
        to_write = existing_data
    elif isinstance(existing_data, list):
        if isinstance(results, dict):
            existing_data.append(results)
        else:
            existing_data.extend(list(results))
        to_write = existing_data
    else:
        to_write = results if isinstance(results, dict) else list(results)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_write, f, indent=4)


def print_results(results: Union[Dict[str, Any], Iterable[Any]]) -> None:
    print("\nResults:")
    print("=" * 50)
    if isinstance(results, dict):
        for key, value in results.items():
            print(f"{key}: {value}")
    else:
        for item in results:
            print(item)
