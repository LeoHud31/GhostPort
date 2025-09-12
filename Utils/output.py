from pathlib import Path
import csv
import json
from typing import Any, Dict, Union, List, Iterable


class output:
    @staticmethod
    def output_results(
        open_ports: Union[Dict[str, Any], List[Any], Iterable[Any]], 
        result_name: str | None = None
    ) -> None:

        if result_name:
            path = Path(result_name)
            try:
                match path.suffix.lower():
                    case ".txt":
                        write_txt(path, open_ports)
                    case ".csv":
                        write_csv(path, open_ports)
                    case ".json":
                        write_json(path, open_ports)
                    case _:
                        print("Unsupported file format. Please use .txt, .csv, or .json")
                        print(open_ports)
                        return
                print(f"open_ports saved to {result_name} at {path.resolve()}")
            except Exception as e:
                print(f"Error saving results: {e}")
                print(open_ports)
        else:
            print(open_ports)


def write_txt(path: Path, open_ports: Union[Dict[str, Any], Iterable[Any]]) -> None:
    mode = "a" if path.exists() else "w"
    with open(path, mode, encoding="utf-8") as f:
        if isinstance(open_ports, dict):
            for key, value in open_ports.items():
                if isinstance(value, dict):
                    f.write(f"{key}:\n")
                    for k, v in value.items():
                        f.write(f"  {k}: {v}\n")
                    f.write("\n")
                else:
                    f.write(f"{key}: {value}\n")
        else:
            for item in open_ports:
                f.write(f"Open: {item}\n")


def write_csv(path: Path, open_ports: Union[Dict[str, Any], Iterable[Any]]) -> None:
    mode = "a" if path.exists() else "w"
    with open(path, mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if isinstance(open_ports, dict):
            if mode == "w":
                writer.writerow(["Key", "Value"])
            for key, value in open_ports.items():
                writer.writerow([key, value])
        else:
            if mode == "w":
                writer.writerow(["Result"])
            for item in open_ports:
                writer.writerow([item])


def write_json(path: Path, open_ports: Union[Dict[str, Any], List[Any], Iterable[Any]]) -> None:
    existing_data = None
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            pass

    if isinstance(existing_data, dict) and isinstance(open_ports, dict):
        existing_data.update(open_ports)
        to_write = existing_data
    elif isinstance(existing_data, list):
        if isinstance(open_ports, dict):
            existing_data.append(open_ports)
        else:
            existing_data.extend(list(open_ports))
        to_write = existing_data
    else:
        to_write = open_ports if isinstance(open_ports, dict) else list(open_ports)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_write, f, indent=4)


def print_open_ports(open_ports: Union[Dict[str, Any], Iterable[Any]]) -> None:
    print("\nResults:")
    print("=" * 50)
    if isinstance(open_ports, dict):
        for key, value in open_ports.items():
            print(f"{key}: {value}")
    else:
        for item in open_ports:
            print(item)
