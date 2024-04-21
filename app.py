import streamlit as st
#from Data_Management import data_manager
import data_manager

st.title("Movie Ticket Booking System")

file_path = 'ticket_data.csv'
ticket_data = data_manager.load_data(file_path)

option = st.sidebar.selectbox("Choose an action", ["Book New Ticket", "Update Ticket", "Cancel Ticket"])

if option == "Book New Ticket":
    st.subheader("Book New Ticket")
    name = st.text_input("Name")
    movie = st.text_input("Movie")
    date = st.text_input("Date")
    seat = st.text_input("Seat")

    if st.button("Book"):
        ticket_details = {'Name': name, 'Movie': movie, 'Date': date, 'Seat': seat}
        ticket_data = data_manager.add_ticket(ticket_data, ticket_details)
        data_manager.save_data(ticket_data, file_path)
        st.success("Ticket booked successfully!")

elif option == "Update Ticket":
    st.subheader("Update Ticket")
    latest_ticket_index = len(ticket_data) - 1  # Index of the latest ticket
    ticket_index = st.number_input("Enter ticket index", min_value=0, max_value=latest_ticket_index, value=latest_ticket_index)
    ticket_details = ticket_data.loc[ticket_index].to_dict()

    st.write(f"Current Details: {ticket_details}")

    updates = {}
    for key in ticket_details.keys():
        new_value = st.text_input(f"Enter new {key}", ticket_details[key])
        updates[key] = new_value

    if st.button("Update"):
        ticket_data = data_manager.update_ticket(ticket_data, ticket_index, updates)
        data_manager.save_data(ticket_data, file_path)
        st.success("Ticket updated successfully!")

elif option == "Cancel Ticket":
    st.subheader("Cancel Ticket")
    latest_ticket_index = len(ticket_data) - 1  # Index of the latest ticket
    ticket_index = st.number_input("Enter ticket index to cancel", min_value=0, max_value=latest_ticket_index, value=latest_ticket_index)
    if st.button("Cancel"):
        ticket_data = data_manager.cancel_ticket(ticket_data, ticket_index)
        data_manager.save_data(ticket_data, file_path)
        st.success("Ticket canceled successfully!")
