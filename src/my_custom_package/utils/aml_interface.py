from azureml.core import Workspace, Datastore
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.exceptions import ComputeTargetException

class AMLInterface:
    def __init__(self, spn_credentials, subscription_id,
                 workspace_name, resource_group):
        auth = ServicePrincipalAuthentication(
            **spn_credentials
        )
        self.workspace = Workspace(
            workspace_name=workspace_name,
            auth=auth,
            subscription_id=subscription_id,
            resource_group=resource_group
        )

    def register_datastore(self, datastore_name, blob_container,
                           storage_acct_name, storage_acct_key):
        Datastore.register_azure_blob_container(
            workspace=self.workspace,
            datastore_name=datastore_name,
            container_name=blob_container,
            account_name=storage_acct_name,
            account_key=storage_acct_key
        )

    def register_aml_environment(self, environment):
        environment.register(workspace=self.workspace)

    def get_compute_target(self, compute_name, vm_size=None):
        try:
            compute_target = ComputeTarget(
                workspace=self.workspace,
                name=compute_name
            )
            print('Found existing compute target')
        except ComputeTargetException:
            print('Creating a new compute target...')
            compute_config = AmlCompute.provisioning_configuration(
                vm_size=vm_size,
                min_nodes=1,
                max_nodes=2
            )
            compute_target = ComputeTarget.create(
                self.workspace,
                compute_name,
                compute_config
            )
            compute_target.wait_for_completion(
                show_output=True,
                timeout_in_minutes=20
            )
        return compute_target
