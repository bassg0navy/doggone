'''Generates code for resource types'''

def generate_resource_code(resource_type, resource_name, properties):
    """
    Generate Python code for the resource based on its type and properties.
    
    Args:
        resource_type: Type of resource
        resource_name: Name for the resource variable
        properties: Dictionary of resource properties
    
    Returns:
        Formatted Python code for the resource
    """
    if resource_type == "bucket":
        return generate_bucket_code(resource_name, properties)

    # elif resource_type == "identity_policy":
    #     return generate_policy_code(resource_name, properties)

    return f"# TODO: Add code for {resource_type} resource named {resource_name}"

def generate_bucket_code(resource_name, properties):
    """Generate code for an OCI bucket resource."""
    # Convert resource name to a valid Python variable name
    variable_name = resource_name.replace('-', '_').replace('.', '_')

    # Build the code with explicit line breaks and indentation
    code = f"# Imported {resource_name} bucket\n"
    code += f"{variable_name} = pulumi_oci.objectstorage.Bucket('{resource_name}',\n"
    code += f"    compartment_id='{properties.get('compartment_id', 'compartment_id')}',\n"
    code += f"    name='{properties.get('name', resource_name)}',\n"
    code += f"    namespace='{properties.get('namespace', 'namespace')}',\n"

    # Add metadata if available
    if "metadata" in properties and properties["metadata"]:
        code += "    metadata={\n"
        for key, value in properties["metadata"].items():
            code += f"        '{key}': '{value}',\n"
        code += "    },\n"

    # Add remaining properties
    code += f"    storage_tier='{properties.get('storage_tier', 'Standard')}',\n"
    code += f"    versioning='{properties.get('versioning', 'Enabled')}'\n"
    code += ")"

    return code
