from ParseDBPedia import *


if __name__ == '__main__':
    males = dict()
    females = dict()

    with open('/Users/agaut/Downloads/persondata_en.ttl', 'r') as file:
        for line in file.readlines():
            if '<http://xmlns.com/foaf/0.1/gender>' in line:
                #then we know this entity has a gender value
                #so put it in male or female dict
                name_url = line.split()[0][1:-1]
                print(name_url)
                name = getNameFromUrl(name_url)
                gender = line.split()[2]
                gender = gender[1:gender.rindex("\"")]
                if gender == "male":
                    if name not in males:
                        males[name] = name
                if gender == "female":
                    if name not in females:
                        females[name] = name

    writeKeysToFiles('PersonData_ttl', males, females)




