import re

def character_cleaning(data):
    len_data = len(data)
    result = []
    
    if len_data == 0:
        pass
    
    elif type(data) is not list or len_data == 1:
        txt = ''.join([char for char in data if not char.islower() and char != ' '])
        txt = re.sub(r'[^A-Z0-9]', '', data)
        result.append(txt)
        return result
    
    else:
        for text in data:
            txt = ''.join([char for char in text if not char.islower() and char != ' '])
            txt = re.sub(r'[^A-Z0-9]', '', text)
            
            if txt != '':
                result.append(txt)
                
        return result

def character_process(data):
    if type(data) is not list:
        return data
    
    else:
        data = [item for sublist in data for item in sublist]
        data = ''.join(data)
        return data