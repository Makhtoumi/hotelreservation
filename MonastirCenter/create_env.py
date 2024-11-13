# create_env.py

# Define your default environment variables and their values
default_env_values = {
    "SECRET_KEY": "your-secret-key",
    "DEBUG": "True",
    "DATABASE_URL": "sqlite:///db.sqlite3",
    # Add more variables and values as needed
}

# Create the .env file with default values
with open(".env", "w") as env_file:
    for key, value in default_env_values.items():
        env_file.write(f"{key}={value}\n")

print(".env file created with default values.")
