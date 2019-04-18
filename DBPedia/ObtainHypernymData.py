from ParseDBPedia import *



class GenderCounts:
    male_count = 0
    female_count = 0
    hypernym = ""

    def __init__(self, hypernym):
        self.hypernym = hypernym

    def incr_male_count(self):
        self.male_count += 1

    def incr_female_count(self):
        self.female_count += 1

    def get_ratio(self):
        return (float(self.male_count)) / (float(self.female_count))

    def get_male_count(self):
        return self.male_count

    def get_female_count(self):
        return self.female_count

    def __eq__(self, other):
        return self.hypernym == other

    def __lt__(self, other):
        return self.male_count < other.male_count



if __name__ == "__main__":
    hypernym_counts = dict()

    #ratio_sort = open('HypernymData/ratio_sort.txt', 'w')
    #male_sort = open('HypernymData/male_dominated.txt', 'w')
    #female_sort = open('HypernymData/female_dominated.txt', 'w')
    dump = open('HypernymData/dump.txt','w')

    with open('PersonData_ttl/female_names.txt') as file:
        for line in file.readlines():
            name = line.strip()
            hypernym = getAttributeForPerson(name, 'hypernym')

            if hypernym in hypernym_counts:
                hypernym_counts[hypernym].incr_female_count()
            else:
                hypernym_counts[hypernym] = GenderCounts(hypernym)
                hypernym_counts[hypernym].incr_female_count()

    with open('PersonData_ttl/male_names.txt') as file:
        for line in file.readlines():
            name = line.strip()
            hypernym = getAttributeForPerson(name, 'hypernym')

            if hypernym in hypernym_counts:
                hypernym_counts[hypernym].incr_male_count()
            else:
                hypernym_counts[hypernym] = GenderCounts(hypernym)
                hypernym_counts[hypernym].incr_male_count()


    for key in sorted(hypernym_counts):
        dump.write(str(key) + ", " + "male: " + str(hypernym_counts[key].get_male_count()) + ", female: " + str(hypernym_counts[key].get_female_count()) + ", ratio: " + str(hypernym_counts[key].get_ratio()))
        dump.write("\n")

    dump.close()