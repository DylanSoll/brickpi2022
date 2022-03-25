import json #imports json library
class JSONHelper(): #creates an object
    def __init__(self, filename): #each object is a file
        self.filename = filename #saves the filename
        with open(self.filename) as self.json_file: #opens the file as self.json_file
            self.json_data = json.load(self.json_file) #converts the data to dictionary
        return

    def reload_data(self): #gets the new data
        with open(self.filename) as self.json_file: #same process as __init__()
            self.json_data = json.load(self.json_file)
        return self.json_data #returns the new data
   
    def write_data(self, data): #update JSON data
        json_string = json.dumps(data) #converts to string
        with open(self.filename, 'w') as f:
            f.write(json_string) #writes the provided data to file
def get_top_x(data, number = 10, desc = True):
    """Gets the first x

    Args:
        data (dict): Dictionary of values to be sorted
        number (int, optional): Number of datapoints to be returned. Defaults to 10.
        desc (bool, optional): Sort in descending order or not. Defaults to True.

    Returns:
        dict: Ordered dictionary of x length
    """    
    ordered_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=desc)) #orders by value
    data_keys = ordered_data.keys() #retrieves the keys in a dict_keys list
    #dict keys are very quiry and cant be indexed
    top_x_data = {} #creates a blank dictionary
    iterator = 0 #seperate iterators because dict_key arrays cant be indexed
    for key in data_keys: #runs through all the keys
        top_x_data[key] = ordered_data[key] #adds the data to the top_x_data dictionary
        iterator += 1 #increases iterator by 1
        if iterator == number: #if iterator is equal to number
            break #exits out of the for loop
    return top_x_data #returns ordered data
#usage
if __name__ == "__main__":
    data = {'h': 1, 'g': 2, 'gs':3, 'sa':4,'f': 5, 'fg': 6, 'fgs':7, 'fsa':8, 'afg': 9, 'afgs':10, 'afsa':11}
    print(get_top_x(data, 3))