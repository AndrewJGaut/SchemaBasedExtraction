




class HypObj:
    
    def __init__(self, hyp, m, f, r):
        self.h = hyp
        self.m = m
        self.f = f
        self.r = r

    def __lt__(self, other):
        return self.r < other.r
    '''
    def __lt__(self, other):
        return (self.m + self.f) < (other.m + other.f) 
    '''


    def __repr__(self):
        return self.h + ", male: " + str(self.m) + ", female: " + str(self.f) + ", ratio: " + str(self.r) + "\n"

    
    def __str__(self):  
        return self.h + ", male: " + str(self.m) + ", female: " + str(self.f) + ", ratio: " + str(self.r)


if __name__ == "__main__":
    with open('dump.txt', 'r') as file:
        counts = list()
        for line in file.readlines():
            print(line)
            hypernym, male, female, ratio = line.split(',') 
            male_count = int(male.split()[-1])
            female_count = int(female.split()[-1])
            ratio = float(ratio.split()[-1])
            counts.append(HypObj(hypernym, male_count, female_count, ratio))
        print(sorted(counts))
        out = open('sorted_by_ratio.txt', 'w')
        out.write(str(sorted(counts)))

        
            
