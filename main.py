def read_file(target_file) -> list:
    """ Takes a .txt file, returns a formatted list for the script

        Each entry in the list corresponds to one line in the .txt-file and consists of another list with 2 indices:
            Index 0 stores the URL as a string
            Index 1 stores the comment (if there is one) next to the URL as a string
    """

    formatted_list = []

    with open (target_file, "r") as file:
        file_contents = file.readlines()
        
        for f in file_contents:
            f = f.strip()
            line_contents = f.split(None,1)
            if (len(line_contents) > 1):                        # Replaces "\t" with spaces in the comment (if there is a comment)
                x = line_contents[1].split("\t")    
                x = " ".join(x)
                line_contents[1] = x
            formatted_list.append(line_contents)
        
    return formatted_list

def print_list(list):
    for i in list:
        print(i)

def filter_by_phrase(l, p) -> list:
    phrase = p
    list = l

    filtered_list = []

    for i in list:
        if (len(i)==2):
            if (phrase in i[1]):
                filtered_list.append(i)

    return filtered_list


def print_test_file():
    test_txt_file = "test.txt"
    print_list(read_file(test_txt_file))


def test_filter_phrase():
    list = filter_by_phrase(read_file("test.txt"), "asd")
    print(list)

test_filter_phrase()
#print_test_file()
