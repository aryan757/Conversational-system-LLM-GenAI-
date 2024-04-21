import pandas as pd

def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=['Name', 'Movie', 'Date', 'Seat'])

def save_data(data, file_path):
    data.to_csv(file_path, index=False)

def add_ticket(data, ticket_details):
    new_ticket = pd.DataFrame([ticket_details])  # Create a new DataFrame for the new ticket
    updated_data = pd.concat([data, new_ticket], ignore_index=True)
    return updated_data

def update_ticket(data, ticket_index, updates):
    for key, value in updates.items():
        data.at[ticket_index, key] = value
    return data

def cancel_ticket(data, ticket_index):
    data = data.drop(ticket_index).reset_index(drop=True)
    return data
