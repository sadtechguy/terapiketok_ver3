import datetime

def authenticate_user(username, password):
    if username is not None and password is not None:
        return True
    return False

def get_queue_number(tuple_queue, id):
    result = -1
    for queue_number, ticket_id in tuple_queue:
        if str(id) == str(ticket_id):
            result = queue_number
            break
        
    return result

def format_date_str(value_str):
    try:
        formatted_value = datetime.datetime.strptime(value_str, "%a, %d %b %Y %H:%M:%S %Z")
        formatted_date = formatted_value.strftime("%d-%b-%Y")
    except ValueError:
        formatted_date = None
    return formatted_date