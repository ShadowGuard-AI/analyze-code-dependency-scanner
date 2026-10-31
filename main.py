import argparse
import logging
import os
import subprocess
import pandas as pd
import sys
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the CLI.
    """
    parser = argparse.ArgumentParser(description="Lists the dependencies a repository declares and checks them against a small built in example table (requests 2.28.0 and django 3.2.0). No vulnerability database is queried, and no outdated version comparison is made.")
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
    For pip, the target repository's requirements.txt is parsed directly.
    Returns None when retrieval fails, so a failure is not mistaken for
    an empty dependency set.
    """
    try:
        if package_manager == 'pip':
            return _parse_requirements_file(repo_path)
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
            return None
    except subprocess.CalledProcessError as e:
        logging.error("Error retrieving dependencies: %s", e)
        return None
    except FileNotFoundError as e:
        logging.error("Error retrieving dependencies: %s", e)
        return None
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON output: %s", e)
        return None


def _parse_requirements_file(repo_path):
    """
    Reads the target repository's own requirements.txt and returns the
    packages declared in it. Returns None if the file cannot be read,
    so the caller can tell a retrieval failure apart from a file that
    declares no packages.
    """
    requirements_path = os.path.join(repo_path, 'requirements.txt')
    try:
        with open(requirements_path, 'r') as f:
            text = f.read()
    except OSError as e:
        logging.error("Error reading requirements file %s: %s", requirements_path, e)
        return None
    return _parse_requirements(text)


def _parse_requirements(text):
    # One requirement per line as written in the file: a package name
    # plus whatever version specifier the author wrote ("==1.0.0",
    # ">=2.0", or nothing). Comment and blank lines carry no package,
    # and option lines (starting with "-") are pip instructions, not
    # packages, so both are skipped.
    dependencies = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        line = line.split(" #", 1)[0].strip()
        line = line.split(";", 1)[0].strip()
        if not line:
            continue
        match = re.match(r"([A-Za-z0-9._-]+)(\[[^\]]*\])?\s*(.*)", line)
        if not match:
            continue
        dependencies.append({'name': match.group(1), 'version': match.group(3).strip()})
    return dependencies


def check_vulnerabilities(dependencies):
    """
    Checks the dependencies against the small built in example table
    below. No vulnerability database is queried, and no version is
    compared for being outdated: a package is flagged only when its
    pinned version is exactly the version listed in the table.
    """
    vulnerability_db = {  # Built in example table: two packages, one version each
        "requests": {"version": "2.28.0", "vulnerabilities": ["CVE-2023-1234", "CVE-2023-5678"]},
        "django": {"version": "3.2.0", "vulnerabilities": ["CVE-2022-9012"]}
    }
    
    for dependency in dependencies:
        name = dependency['name']
        version = dependency['version']

        pinned = version[2:].strip() if version.startswith("==") else version.strip()
        if name.lower() in vulnerability_db:
            if vulnerability_db[name.lower()]["version"] == pinned:
                dependency['vulnerabilities'] = vulnerability_db[name.lower()]["vulnerabilities"]
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

    if dependencies is None:
        logging.error("Dependency retrieval failed for repository: %s using package manager: %s. No report was written.", repo_path, package_manager)
        sys.exit(1)

    if not dependencies:
        logging.error("Zero dependencies found in repository: %s. Nothing was scanned, so no report was written.", repo_path)
        sys.exit(1)

    dependencies = check_vulnerabilities(dependencies)

    # Load and filter ignored vulnerabilities
    ignored_vulnerabilities = []
    if ignore_vulnerabilities_file:
        ignored_vulnerabilities = load_ignored_vulnerabilities(ignore_vulnerabilities_file)
        dependencies = filter_vulnerabilities(dependencies, ignored_vulnerabilities)

    generate_report(dependencies, output_path, output_format)

if __name__ == "__main__":
    main()

