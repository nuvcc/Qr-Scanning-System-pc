import json

# Step 1: Read the list of JWT tokens from the TXT file
txt_file_path = "encodedjwt_family_pass.txt"  # Replace with the path to your text file containing multiple JWT tokens
with open(txt_file_path, "r") as txt_file:
    jwt_tokens = [token.strip() for token in txt_file.readlines()]

# Step 2: Create a JSON array with the JWT tokens
json_data = {"tokens": jwt_tokens}

# Step 3: Write the JSON data to a JSON file
json_file_path = "jwt_tokens_family.json"  # Replace with the path to your desired JSON file
with open(json_file_path, "w") as json_file:
    json.dump(json_data, json_file, indent=4)
