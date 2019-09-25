import xlwt


class EpochStats():
    def __init__(self):
        self.epoch_num = 0
        self.ave_acc_gain_per_training_step = 0
        self.ave_acc_gain_per_testing_step = 0
        self.max_acc_training = 0
        self.max_acc_testing = 0
        self.ave_loss_decrease_per_training_step = 0
        self.auc = 0
        self.num_steps = 0

        self.total_loss = 0
        self.total_acc_training = 0
        self.total_acc_testing = 0

    def set_epoch_num(self, val):
        self.epoch_num = val
    def get_epoch_num(self):
        return self.epoch_num

    def set_ave_acc_gain_per_training(self, val):
        self.ave_acc_gain_per_training_step = val
    def get_ave_acc_gain_per_training(self):
        return self.ave_acc_gain_per_training_step

    def set_ave_acc_gain_per_testing(self, val):
        self.ave_acc_gain_per_testing_step = val
    def get_ave_acc_gain_per_testing(self):
        return self.ave_acc_gain_per_testing_step

    def set_max_acc_training(self, val):
        self.max_acc_training = val
    def get_max_acc_training(self):
        return self.max_acc_training

    def set_max_acc_testing(self, val):
        self.max_acc_testing = val
    def get_max_acc_testing(self):
        return self.max_acc_testing

    def set_ave_loss_dec_per_step(self, val):
        self.ave_loss_decrease_per_training_step = val
    def get_ave_loss_dec_per_step(self):
        return self.ave_loss_decrease_per_training_step

    def set_auc(self, val):
        self.auc = val
    def get_auc(self):
        return self.auc

    def incr_total_loss(self, val):
        self.total_loss += val
    def get_total_loss(self):
        return self.total_loss

    def incr_total_acc_training(self, val):
        self.total_acc_training += val
    def get_total_acc_training(self):
        return self.total_acc_training

    def incr_total_acc_testing(self, val):
        self.total_acc_testing += val
    def get_total_acc_testing(self):
        return self.total_acc_testing

    def incr_num_steps(self):
        self.num_steps += float(1)
    def get_num_steps(self):
        return self.num_steps

    def __str__(self):
        return "EpochNum: {}; NumSteps: {}; AveAccTrainingStep: {}; AveAccTestingStep: {}; AveLossDecrPerStep: {}".format(self.epoch_num, self.num_steps, self.ave_acc_gain_per_training_step, self.ave_acc_gain_per_testing_step, self.ave_loss_decrease_per_training_step)
    def __repr__(self):
        return str(self)


def parseLine(line, mode, curr_epoch):
    data = line.split(' ')
    i = 0
    while i < len(data):
        # to get averages, just get totals first then divide all by number of steps
        if data[i] == '|':
            curr_epoch.incr_num_steps()
        elif data[i] == 'loss:':
            curr_epoch.incr_total_loss(float(data[i + 1][:-1]))
            i += 1
        #elif data[i] == 'not NA accuracy:':
        elif (i < len(data)-2) and (data[i] == 'not' and data[i+1] == 'NA' and data[i+2] == 'accuracy:'):
            acc = float(data[i + 3][:-1])
            if mode == 'train':
                if acc > curr_epoch.get_max_acc_training():
                    curr_epoch.set_max_acc_training(acc)
                curr_epoch.incr_total_acc_training(acc)
            elif mode == 'test':
                if acc > curr_epoch.get_max_acc_testing():
                    curr_epoch.set_max_acc_testing(acc)
                curr_epoch.incr_total_acc_testing(acc)
            else:
                raise AttributeError
            #curr_epoch.incr_total_acc(float(data[i + 1]))
            i += 1
        i+=1
    return curr_epoch


def parse(lines):
    epochs = list()
    training_line = False
    testing_line = False
    curr_epoch = None

    for line in lines:
        #print(line)
        '''steps separated by | ^M'''
        if training_line:
            curr_epoch = parseLine(line, 'train', curr_epoch)
            training_line = False # so it won't continue thinking next line is training line
        if testing_line:
            curr_epoch = parseLine(line, 'test', curr_epoch)
            testing_line = False
        if '[TEST] auc:' in line:
            auc = float(line.split(' ')[2].strip())
            curr_epoch.set_auc(auc)

        if 'Finish calculating':
            testing_line = True
        if '###### Epoch' in line:
            #then, it has epoch num
            if(curr_epoch): #and curr_epoch.get_num_steps() != 0):
                #calc averages
                curr_epoch.set_ave_acc_gain_per_training(curr_epoch.get_total_acc_training()/curr_epoch.get_num_steps())
                curr_epoch.set_ave_acc_gain_per_testing(curr_epoch.get_total_acc_testing()/curr_epoch.get_num_steps())
                curr_epoch.set_ave_loss_dec_per_step(curr_epoch.get_total_loss() / curr_epoch.get_num_steps())
                epochs.append(curr_epoch)

            curr_epoch = EpochStats()
            epoch_num = int(line.split('######')[1].split(' ')[2].strip())
            curr_epoch.set_epoch_num(epoch_num)
            #next line is the one we want
            training_line = True
    if(curr_epoch and curr_epoch.get_num_steps()!=0):
        curr_epoch.set_ave_acc_gain_per_training(curr_epoch.get_total_acc_training() / curr_epoch.get_num_steps())
        curr_epoch.set_ave_acc_gain_per_testing(curr_epoch.get_total_acc_testing() / curr_epoch.get_num_steps())
        curr_epoch.set_ave_loss_dec_per_step(curr_epoch.get_total_loss() / curr_epoch.get_num_steps())
        epochs.append(curr_epoch)

    print(epochs)
    return epochs

def getBestEpochs(epochs):
    max_ave_acc_gain_per_step_training = 0
    maagpstraining_epoch = 0
    max_ave_acc_gain_per_step_testing = 0
    maagpstesting_epoch = 0
    max_ave_loss_decr_per_step = 0
    maldps_epoch = 0
    max_auc = 0
    mauc_epoch = 0

    max_acc_training = 0
    mat_epoch = 0
    max_acc_testing = 0
    matest_epoch = 0

    for epoch in epochs:
        if epoch.get_ave_acc_gain_per_training() > max_ave_acc_gain_per_step_training:
            max_ave_acc_gain_per_step_training = epoch.get_ave_acc_gain_per_training()
            maagpstraining_epoch = epoch.get_epoch_num()
        if epoch.get_ave_acc_gain_per_testing() > max_ave_acc_gain_per_step_testing:
            max_ave_acc_gain_per_step_testing = epoch.get_ave_acc_gain_per_testing()
            maagpstesting_epoch = epoch.get_epoch_num()
        if epoch.get_ave_loss_dec_per_step() > max_ave_loss_decr_per_step:
            max_ave_loss_decr_per_step = epoch.get_ave_loss_dec_per_step()
            maldps_epoch = epoch.get_epoch_num()
        if epoch.get_auc() > max_auc:
            max_auc = epoch.get_auc()
            mauc_epoch = epoch.get_epoch_num()
        if epoch.get_max_acc_training() > max_acc_training:
            max_acc_training = epoch.get_max_acc_training()
        if epoch.get_max_acc_testing() > max_acc_testing:
            max_acc_testing = epoch.get_max_acc_testing()

    #print('{}, {}, {}, {}'.format(maagpstraining_epoch, maagpstesting_epoch, maldps_epoch, mauc_epoch))
    #print('{}, {}, {}, {}'.format(max_ave_acc_gain_per_step_training, max_ave_acc_gain_per_step_testing, max_ave_loss_decr_per_step, max_auc))
    return(max_ave_acc_gain_per_step_training, max_ave_acc_gain_per_step_testing, max_ave_loss_decr_per_step, max_auc, max_acc_training, max_acc_testing)


def getAvesBetweenEpochs(epochs):
    ave_max_acc_gain_training = 0
    ave_max_acc_gain_testing = 0
    ave_incr_in_loss_decr_per_epoch = 0
    ave_auc_gain = 0


    for i in range(len(epochs) - 1):
        ave_max_acc_gain_training += abs(epochs[i].get_max_acc_training() - epochs[i+1].get_max_acc_training())
        ave_max_acc_gain_testing = abs(epochs[i].get_max_acc_testing() - epochs[i + 1].get_max_acc_testing())
        ave_incr_in_loss_decr_per_epoch = abs(epochs[i].get_ave_loss_dec_per_step() - epochs[i+1].get_ave_loss_dec_per_step())
        ave_auc_gain = abs(epochs[i].get_auc() - epochs[i+1].get_auc())

    #print('{}, {}, {}, {}'.format(ave_max_acc_gain_training, ave_max_acc_gain_testing, ave_incr_in_loss_decr_per_epoch, ave_auc_gain))
    return(ave_max_acc_gain_training, ave_max_acc_gain_testing, ave_incr_in_loss_decr_per_epoch, ave_auc_gain)

def getBestModel(model_stats):
    best_model = 0
    best_auc = 0

    for i in range(len(model_stats)):
        model = model_stats[i][1]
        max_auc = getBestEpochs(model)[3]
        if max_auc > best_auc:
            best_auc = max_auc
            best_model = i

    return model_stats[best_model][0]


def getStats(str):
    spouse = str.split(' ')
    spouse_stats = list()
    for i in range(1, len(spouse)):
        stat = spouse[i]
        spouse_stats.append(getNum(stat[:-1]))
    return spouse_stats

def getNum(str):
    print(str)
    return float(str.split('=')[1])

def writeStats(sheet, stats_list, col_counter, row_counter):
    for stats in stats_list:
        for stat in stats:
            sheet.write(row_counter, col_counter, stat)
            col_counter += 1
    return sheet


if __name__ == '__main__':
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('statsitics')
    row_write_counter = 0
    sheet.write(0, 1, 'SPOUSE')
    sheet.write(0, 4, 'BIRTHDATE')
    sheet.write(0, 7, 'BIRTHPLACE')
    sheet.write(0, 10, 'HYPERNYM')

    stats=['numcorrect', 'numtotal', 'percentage']

    for i in range(4):
        for j in range(3):
            sheet.write(1, i*3+j + 1, stats[j])

    row_write_counter = 2

    #nohup_file = open('GRID_SEARCH_OUTPUT.txt', 'r')
    nohup_file = open('DEBIASED_TESTING.out', 'r+')
    #nohup_file.seek(0)
    model_outputs = nohup_file.read().split('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*****************************^^^^^^^^^^^^^&&&&&$$$$$$$$$$$$$$$$$$$$$$$$$$$')[1:]
    model_stats = list()
    nohup_file.seek(0)
    model_name = nohup_file.readlines()[0].strip()
    for model in model_outputs:
        lines = model.split('\n')
        for i in range(len(lines)):
            if 'Finish testing' in lines[i]:
                #then take next 4 lines for our dark purposes
                spouse_stats = getStats(lines[i+1])
                birthdate_stats = getStats(lines[i+2])
                birthplace_stats = getStats(lines[i+3])
                hypernym_stats = getStats(lines[i+4])
                col_counter = 1
                sheet = writeStats(sheet, [spouse_stats, birthdate_stats, birthplace_stats, hypernym_stats], col_counter, row_write_counter)
                sheet.write(row_write_counter, 0, model_name)
                row_write_counter += 1

            if i+6 < len(lines):
                model_name = lines[i+6].strip()
    workbook.save('STATS_DEB.xls')



    '''
    for model in model_outputs:
        name = model.split('\n')[1].split(' ')
        batch = name[2]
        learningrate = name[3]
        model_name = batch + " " + learningrate
        print(model_name)

        #print(model[0].split(':')[1])
        #epochs = parse(nohup_file.readlines()
        epochs = parse(model.split('\n'))
        if epochs:
            model_stats.append((model_name, epochs))
            getBestEpochs(epochs)
            getAvesBetweenEpochs(epochs)

    print('BEST: ' + str(getBestModel(model_stats)))

    print("---------------------------------------------")

    for model in model_stats:
        print('{}, AUC: {}, MAX_TRAIN_ACC: {}, MAX_TEST_ACC: {}'.format(model[0], getBestEpochs(model[1])[3], getBestEpochs(model[1])[4], getBestEpochs(model[1])[5]))
    '''




