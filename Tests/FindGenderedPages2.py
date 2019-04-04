
if __name__ == '__main__':

    names = list()
    with open('dbpedia_query.txt') as names_file:
        for line in names_file.readlines():
            if '<td><pre>' in line:
                names.append(line[13:-12])

    print(sorted(names))