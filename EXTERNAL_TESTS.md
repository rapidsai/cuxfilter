# External Tests Workflow

This document provides an overview of the GitHub Actions workflow (`.github/workflows/test-external.yaml`) and associated script (`ci/test_external.sh`) for running external tests on specified Python libraries, such as Datashader and Holoviews.

## Purpose

The purpose of this workflow is to perform GPU testing on external party dependencies. It involes the following steps:

1. Create a Conda environment named `test_external`.
2. Install external dependencies specified in `ci/utils/external_dependencies.yaml`.
3. Clone specified Python libraries from their respective GitHub repositories.
4. Install test dependencies for each library.
5. Run GPU tests on the specified libraries using Pytest.

## Workflow Configuration

### Workflow Trigger

The workflow is triggered in two ways:

1. **Manual Trigger:** You can manually trigger the workflow by selecting the "GPU testing for external party dependencies" workflow and providing the following inputs:

   - `external-project`: Specify the project to test (`datashader`, `holoviews`, or `all`).
   - `pr_number`: (Optional) If testing a pull request, provide the PR number.

2. **Scheduled Trigger:** The workflow runs automatically every Sunday evening (Pacific Time) using a cron schedule (`0 0 * * 1`).

## Script (`test_external.sh`)

The script is responsible for setting up the Conda environment, installing dependencies, cloning specified Python libraries, and running GPU tests. Key steps in the script include:

1. **Create Conda Environment:** Creates a Conda environment named `test_external` and installs external dependencies from `external_dependencies.yaml`.

2. **Clone Repositories:** Clones GitHub repositories of specified Python libraries (`datashader`, `holoviews`, or both).

3. **Install Dependencies:** Installs test dependencies for each library using `python -m pip install -e .[tests]`.

4. **Run Tests:** Gathers GPU tests containing the keywords `cudf` and runs them using Pytest. The number of processes is set to 8 by default, but specific tests (`test_quadmesh.py`) are run separately.

## Running External Tests

To manually trigger the workflow and run external tests:

1. Navigate to the "Actions" tab in your GitHub repository.
2. Select "GPU testing for external party dependencies" workflow.
3. Click the "Run workflow" button.
4. Provide inputs for `external-project` and `pr_number` if needed.

## Contributing

Contributors can use this workflow to test changes in external libraries on the RAPIDS AI ecosystem. When contributing, follow these steps:

1. Make changes to the external library code.
2. Push the changes to your fork or branch.
3. Trigger the workflow manually by selecting the appropriate inputs.

For additional information, refer to the [GitHub Actions documentation](https://docs.github.com/en/actions).
