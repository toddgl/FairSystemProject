import yaml

def remove_fields_from_yaml(file_path, output_path, fields_to_remove):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    # Iterate through each object in the YAML data
    for item in data:
        if 'fields' in item:
            for field in fields_to_remove:
                item['fields'].pop(field, None)

    with open(output_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False, indent=4)

if __name__ == "__main__":
    input_file = "accounts/fixtures/accounts.yaml"
    output_file = "accounts/fixtures/accounts_cleaned.yaml"
    fields_to_remove = ['groups', 'user_permissions']

    remove_fields_from_yaml(input_file, output_file, fields_to_remove)
    print(f"Cleaned YAML file saved to {output_file}")
