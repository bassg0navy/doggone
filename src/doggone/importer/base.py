'''Module for functions that import resources'''
import pulumi_oci
import pulumi

def import_infra(resource_type, resource_name, resource_id, namespace, compartment_id):
    '''Pulumi program to import resource into state'''

    resource_types = {
        "bucket": pulumi_oci.objectstorage.Bucket,
        "identity_policy": pulumi_oci.identity.Policy,
        # Add other resource types as needed
    }
    # Get resource class using resource type parameter passed to function
    resource_class = resource_types.get(resource_type)
    if not resource_class:
        raise ValueError(f"Unsupported resource type: {resource_type}")

    # Build optional arguments to pass to resource when making call to auto API
    args = {
        # "metadata": {
        #     "Created-By": "Pulumi",
        #     "Purpose": "Infra Import Demo"
        # },
    }
    import_id = (f"n/{namespace}/b/{resource_name}"
                 if resource_type == 'bucket'
                 else resource_id)

    opts = pulumi.ResourceOptions(import_=import_id)

    # Create resource object
    resource_class(resource_name,
        # Required parameters
        compartment_id=compartment_id,
        name=resource_name,
        namespace=namespace,
        # Optional parameters
        **args,
        opts=opts
    )
