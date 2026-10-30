import argparse
import logging
import os
import subprocess
import pandas as pd
import sys
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the CLI.
    """
    parser = argparse.ArgumentParser(description="Scans code repositories for outdated or vulnerable dependencies.")
    parser.add_argument("repo_path", help="Path to the code repository.")
    parser.add_argument("-o", "--output", help="Path to the output file (CSV or JSON). Defaults to 'dependency_report.csv'.", default="dependency_report.csv")
    parser.add_argument("-f", "--format", help="Output format: csv or json. Defaults to csv.", choices=['csv', 'json'], default='csv')
    parser.add_argument("-p", "--package_manager", help="Package manager to use (e.g., pip, npm, yarn). If not specified, will attempt to detect.", choices=['pip', 'npm', 'yarn'], default=None)
    parser.add_argument("--ignore-vulnerabilities", help="Path to a JSON file containing a list of vulnerabilities to ignore.", default=None)
    return parser.parse_args()


def detect_package_manager(repo_path):
    """
    Detects the package manager used in the repository based on the presence of specific files.
    """
    if os.path.exists(os.path.join(repo_path, 'requirements.txt')):
        return 'pip'
    elif os.path.exists(os.path.join(repo_path, 'package.json')):
        return 'npm'
    elif os.path.exists(os.path.join(repo_path, 'yarn.lock')):
        return 'yarn'
    else:
        return None


def get_dependencies(repo_path, package_manager):
    """
    Retrieves the list of dependencies and their versions using the specified package manager.
    """
    try:
        if package_manager == 'pip':
            result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True, cwd=repo_path, check=True)
            return _parse_pip_freeze(result.stdout)
        elif package_manager == 'npm':
            result = subprocess.run(['npm', 'list', '--depth=0', '--json'], capture_output=True, text=True, cwd=repo_path, check=True)
            data = json.loads(result.stdout)
            dependencies = []
            if 'dependencies' in data:
                for name, version_info in data['dependencies'].items():
                    dependencies.append({'name': name, 'version': version_info.get('version', 'N/A')})
            return dependencies
        elif package_manager == 'yarn':
            result = subprocess.run(['yarn', 'list', '--depth=0', '--json'], capture_output=True, text=True, cwd=repo_path, check=True)
            data = json.loads(result.stdout)
            dependencies = []
            if 'data' in data:
                for item in data['data']['trees']:
                  # Yarn names can start with @ (scoped packages), so a
                  # plain split on "@" mangles them. Split off only the
                  # trailing version, from the right.
                  name, _, version = item['name'].rpartition("@")
                  dependencies.append({'name': name or item['name'], 'version': version or 'N/A'})
            return dependencies
        else:
            logging.error("Unsupported package manager: %s", package_manager)
            return []
    except subprocess.CalledProcessError as e:
        logging.error("Error retrieving dependencies: %s", e)
        return []
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON output: %s", e)
        return []


def _parse_pip_freeze(output):
    # pip freeze emits one "name==version" line per package, but editable
    # installs show up as "-e git+..." lines and blank lines appear at the
    # ends. Both used to become phantom packages with an empty name.
    dependencies = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("-e ") or "==" not in line:
            continue
        name, version = line.split("==", 1)
        dependencies.append({'name': name, 'version': version})
    return dependencies


def check_vulnerabilities(dependencies):
    """
    Checks for known vulnerabilities in the dependencies using a (placeholder) vulnerability database.
    In a real-world scenario, this would involve querying an actual vulnerability database.
    """
    vulnerability_db = {  # Placeholder vulnerability database
        "requests": {"version": "2.28.0", "vulnerabilities": ["CVE-2023-1234", "CVE-2023-5678"]},
        "django": {"version": "3.2.0", "vulnerabilities": ["CVE-2022-9012"]}
    }
    
    for dependency in dependencies:
        name = dependency['name']
        version = dependency['version']

        if name in vulnerability_db:
            if vulnerability_db[name]["version"] == version:
                dependency['vulnerabilities'] = vulnerability_db[name]["vulnerabilities"]
            else:
                dependency['vulnerabilities'] = []
        else:
            dependency['vulnerabilities'] = []
    return dependencies


def load_ignored_vulnerabilities(file_path):
    """Loads a list of vulnerabilities to ignore from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Ignore vulnerabilities file not found: %s", file_path)
        return []
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in ignore vulnerabilities file: %s", file_path)
        return []


def filter_vulnerabilities(dependencies, ignored_vulnerabilities):
    """Filters out any ignored vulnerabilities from the dependency list."""
    for dependency in dependencies:
        if 'vulnerabilities' in dependency and dependency['vulnerabilities']:
            dependency['vulnerabilities'] = [
                vuln for vuln in dependency['vulnerabilities'] if vuln not in ignored_vulnerabilities
            ]
    return dependencies


def generate_report(dependencies, output_path, output_format):
    """
    Generates a report of the dependencies and their vulnerabilities in CSV or JSON format.
    """
    df = pd.DataFrame(dependencies)
    if output_format == 'csv':
        df.to_csv(output_path, index=False)
        logging.info("Report generated successfully at: %s", output_path)
    elif output_format == 'json':
        df.to_json(output_path, orient="records")
        logging.info("Report generated successfully at: %s", output_path)
    else:
        logging.error("Invalid output format: %s", output_format)


def main():
    """
    Main function to orchestrate the dependency scanning process.
    """
    args = setup_argparse()
    repo_path = args.repo_path
    output_path = args.output
    output_format = args.format
    package_manager = args.package_manager
    ignore_vulnerabilities_file = args.ignore_vulnerabilities

    # Validate repo_path. Exit nonzero, as with the other early stops in
    # this function, so callers can tell a bad path from a clean scan.
    if not os.path.isdir(repo_path):
        logging.error("Invalid repository path: %s", repo_path)
        sys.exit(1)

    # Detect package manager if not specified
    if not package_manager:
        package_manager = detect_package_manager(repo_path)
        if not package_manager:
            logging.warning("Could not automatically detect package manager.  Please specify with the -p option.")
            sys.exit(1)

    logging.info("Scanning repository: %s using package manager: %s", repo_path, package_manager)

    dependencies = get_dependencies(repo_path, package_manager)

    if not dependencies:
        logging.warning("No dependencies found.")
        return

    dependencies = check_vulnerabilities(dependencies)

    # Load and filter ignored vulnerabilities
    ignored_vulnerabilities = []
    if ignore_vulnerabilities_file:
        ignored_vulnerabilities = load_ignored_vulnerabilities(ignore_vulnerabilities_file)
        dependencies = filter_vulnerabilities(dependencies, ignored_vulnerabilities)

    generate_report(dependencies, output_path, output_format)

if __name__ == "__main__":
    main()

