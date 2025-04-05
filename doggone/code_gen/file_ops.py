'''Module for functions that perform operations against local files'''
from doggone.code_gen.file_ops import generate_resource_code

def add_resource_to_main_file(
    resource_type, resource_name, resource_properties,
    target_file="__main__.py"
):
    """
    Add imported resource code to the target Python file.
    
    Args:
        resource_type: Type of resource (e.g., 'bucket', 'policy')
        resource_name: Name of the resource in Pulumi
        resource_properties: Dictionary of resource properties
        target_file: Path to the target Python file (default: __main__.py)
    """
    try:
        # Read the existing file
        with open(target_file, 'r', encoding='utf-8') as file:
            content = file.read()

        # Generate the resource code
        resource_code = generate_resource_code(resource_type, resource_name, resource_properties)

        # Find an appropriate place to insert the code
        if "pulumi.export" in content:
            # Insert before exports
            insert_position = content.find("pulumi.export")
            new_content = (
                content[:insert_position] +
                resource_code + "\n\n" +
                content[insert_position:]
            )
        else:
            # Append to the end of the file
            new_content = content + "\n\n" + resource_code

        # Write the updated content back to the file
        with open(target_file, 'w', encoding='utf-8') as file:
            file.write(new_content)

        return True, f"\nAdded {resource_type} resource '{resource_name}' to {target_file}"

    except Exception as e: # pylint: disable=broad-exception-caught
        return False, f"Error adding resource to {target_file}: {e}"
