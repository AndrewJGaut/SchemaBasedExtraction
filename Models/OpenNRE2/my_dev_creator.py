


def createDevFileFromTrainFile():
    file = open('data/nyt/train-reading-friendly.json', 'r')

    num_examples = 0
    total_examples = 100000
    out_str = ""
    done = False
    possible_end = False

    for line in file.readlines():
        if line.strip() == "{":
            #we're starting a new entity
            num_examples += 1

            if num_examples == total_examples:
                done = True

        if possible_end:
            if line.strip() == "{":
                break
            else:
                possible_end = False
        if done:
            if line.strip() == "},":
                possible_end = True
        out_str += line
    out_str = out_str[:-3]
    out_str += "\n]"

    out_file = open('dev.json', 'w')
    out_file.write(out_str)

if __name__ == '__main__':
    createDevFileFromTrainFile()
