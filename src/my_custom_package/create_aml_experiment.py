import os

from azureml.core import ScriptRunConfig, Experiment, Environment

from my_custom_package.utils.aml_interface import AMLInterface
from my_custom_package.utils.const import (
    AML_COMPUTE_NAME, AML_ENV_NAME, AML_EXPERIMENT_NAME)


__here__ = os.path.dirname(__file__)


def submit_run(aml_interface):
    experiment = Experiment(aml_interface.workspace, AML_EXPERIMENT_NAME)
    src_dir = __here__
    run_config = ScriptRunConfig(
        source_directory=src_dir,
        script='train.py'
    )
    run_config.run_config.target = aml_interface.get_compute_target(
        AML_COMPUTE_NAME,
        'STANDARD_D2_V2'
    )
    aml_run_env = Environment.get(
        aml_interface.workspace,
        AML_ENV_NAME
    )
    run_config.run_config.environment = aml_run_env
    print("Submitting Run")
    run = experiment.submit(config=run_config)
    run.wait_for_completion(show_output=True)
    print(run.get_metrics())


def main():
    # Retrieve vars from env
    workspace_name = os.environ['AML_WORKSPACE_NAME']
    resource_group = os.environ['RESOURCE_GROUP']
    subscription_id = os.environ['SUBSCRIPTION_ID']

    spn_credentials = {
        'tenant_id': os.environ['TENANT_ID'],
        'service_principal_id': os.environ['SPN_ID'],
        'service_principal_password': os.environ['SPN_PASSWORD'],
    }

    aml_interface = AMLInterface(
        spn_credentials, subscription_id, workspace_name, resource_group
    )
    submit_run(aml_interface)


if __name__ == '__main__':
    main()
    