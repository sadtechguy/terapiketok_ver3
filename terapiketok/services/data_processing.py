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

def format_time(value_str):
    try:
        formatted_time = datetime.datetime.strptime(value_str, "%H:%M:%S").strftime("%H:%M")
    except ValueError:
        formatted_time = None
    return formatted_time

def format_default_batch_time(datas):
    datas.batch1_start = datas.batch1_start.strftime("%H:%M")
    datas.batch1_end = datas.batch1_end.strftime("%H:%M")
    datas.batch2_start = datas.batch2_start.strftime("%H:%M")
    datas.batch2_end = datas.batch2_end.strftime("%H:%M")
    datas.batch3_start = datas.batch3_start.strftime("%H:%M")
    datas.batch3_end = datas.batch3_end.strftime("%H:%M")
    datas.batch4_start = datas.batch4_start.strftime("%H:%M")
    datas.batch4_end = datas.batch4_end.strftime("%H:%M")
    datas.batch5_start = datas.batch5_start.strftime("%H:%M")
    datas.batch5_end = datas.batch5_end.strftime("%H:%M")

    return datas
    
