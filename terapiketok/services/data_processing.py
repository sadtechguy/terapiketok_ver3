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