from html.parser import HTMLParser

MyList=[]

class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        MyList.append([self.get_starttag_text(), data])
        return MyList


parser = MyHTMLParser()
with open("output.html", "r") as html_file:
    html_string = html_file.read()
    parser.feed(html_string)

print(MyList)

def chapter(list):
    chapters=[]
    for i in list:
        if i[0] != '<p>':
            chapters.append([i[1], MyList.index(i)])
    return chapters

def level(list):
    level_one_list = []
    level_two_list = []
    level_three_list = []
    level_four_list = []
    level_data_list = []
    for i in list:
        if i[0]=='<h1>':
            level_one_list.append([i[1], MyList.index(i)])
        elif i[0]=='<h2>':
            level_two_list.append([i[1], MyList.index(i)])
        elif i[0] == '<h3>':
            level_three_list.append([i[1], MyList.index(i)])
        elif i[0] == '<h4>':
            level_four_list.append([i[1], MyList.index(i)])
        elif i[0] == '<p>':
            level_data_list.append([i[1], MyList.index(i)])
    return level_one_list, level_two_list, level_three_list, level_four_list, level_data_list


def hierarchy(list_two, list_three):
    added_values = []
    hierarchy_dict={}
    for j in reversed(list_two):
        emptyList = []
        for i in list_three:
            if i[0] not in added_values and i[1]>j[1]:
                emptyList.append(i[0])
                added_values.append(i[0])
        hierarchy_dict[j[0]]=emptyList
    return hierarchy_dict

chapter_list=chapter(MyList)
level_one_list, level_two_list, level_three_list, level_four_list, level_data_list = level(MyList)
one_two_dict=hierarchy(level_one_list, level_two_list)
two_three_dict=hierarchy(level_two_list, level_three_list)
three_four_dict=hierarchy(level_three_list, level_four_list)
chapter_data_dict=hierarchy(chapter_list, level_data_list)

print(level_one_list)
print(level_two_list)
print(level_three_list)
print(level_four_list)
print(one_two_dict)
print(two_three_dict)
print(three_four_dict)
print(chapter_data_dict)



