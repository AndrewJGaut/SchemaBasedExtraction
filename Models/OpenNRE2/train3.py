import nrekit
import numpy as np
import tensorflow as tf
import sys
import os

'''ray code'''
import ray
from ray import tune
from ray.tune import grid_search, register_trainable


# dataset_name = 'nyt'
dataset_name = 'Wikigender'
if len(sys.argv) > 1:
    dataset_name = sys.argv[1]
dataset_dir = os.path.join('./data', dataset_name)
if not os.path.isdir(dataset_dir):
    raise Exception("[ERROR] Dataset dir %s doesn't exist!" % (dataset_dir))

# The first 3 parameters are train / test data file name, word embedding file name and relation-id mapping file name respectively.
train_loader = nrekit.data_loader.json_file_data_loader(os.path.join(dataset_dir, 'train.json'),
                                                        os.path.join(dataset_dir, 'word_vec.json'),
                                                        os.path.join(dataset_dir, 'rel2id.json'),
                                                        mode=nrekit.data_loader.json_file_data_loader.MODE_RELFACT_BAG,
                                                        shuffle=True)
test_loader = nrekit.data_loader.json_file_data_loader(os.path.join(dataset_dir, 'test.json'),
                                                       os.path.join(dataset_dir, 'word_vec.json'),
                                                       os.path.join(dataset_dir, 'rel2id.json'),
                                                       mode=nrekit.data_loader.json_file_data_loader.MODE_ENTPAIR_BAG,
                                                       shuffle=False)

framework = nrekit.framework.re_framework(train_loader, test_loader)


class model(nrekit.framework.re_model):
    encoder = "pcnn"
    selector = "att"

    def __init__(self, train_data_loader, batch_size, max_length=120):
        nrekit.framework.re_model.__init__(self, train_data_loader, batch_size, max_length=max_length)
        self.mask = tf.placeholder(dtype=tf.int32, shape=[None, max_length], name="mask")

        # Embedding
        with tf.name_scope('embedding'):
            x = nrekit.network.embedding.word_position_embedding(self.word, self.word_vec_mat, self.pos1, self.pos2)

        # Encoder
        with tf.name_scope('encoder'):
            if model.encoder == "pcnn":
                x_train = nrekit.network.encoder.pcnn(x, self.mask, keep_prob=0.5)
                x_test = nrekit.network.encoder.pcnn(x, self.mask, keep_prob=1.0)
            elif model.encoder == "cnn":
                x_train = nrekit.network.encoder.cnn(x, keep_prob=0.5)
                x_test = nrekit.network.encoder.cnn(x, keep_prob=1.0)
            elif model.encoder == "rnn":
                x_train = nrekit.network.encoder.rnn(x, self.length, keep_prob=0.5)
                x_test = nrekit.network.encoder.rnn(x, self.length, keep_prob=1.0)
            elif model.encoder == "birnn":
                x_train = nrekit.network.encoder.birnn(x, self.length, keep_prob=0.5)
                x_test = nrekit.network.encoder.birnn(x, self.length, keep_prob=1.0)
            else:
                raise NotImplementedError

        # Selector
        with tf.name_scope('selector'):
            if model.selector == "att":
                self._train_logit, train_repre = nrekit.network.selector.bag_attention(x_train, self.scope,
                                                                                       self.ins_label, self.rel_tot,
                                                                                       True, keep_prob=0.5)
                self._test_logit, test_repre = nrekit.network.selector.bag_attention(x_test, self.scope, self.ins_label,
                                                                                     self.rel_tot, False, keep_prob=1.0)
            elif model.selector == "ave":
                self._train_logit, train_repre = nrekit.network.selector.bag_average(x_train, self.scope, self.rel_tot,
                                                                                     keep_prob=0.5)
                self._test_logit, test_repre = nrekit.network.selector.bag_average(x_test, self.scope, self.rel_tot,
                                                                                   keep_prob=1.0)
                self._test_logit = tf.nn.softmax(self._test_logit)
            elif model.selector == "one":
                self._train_logit, train_repre = nrekit.network.selector.bag_one(x_train, self.scope, self.label,
                                                                                 self.rel_tot, True, keep_prob=0.5)
                self._test_logit, test_repre = nrekit.network.selector.bag_one(x_test, self.scope, self.label,
                                                                               self.rel_tot, False, keep_prob=1.0)
                self._test_logit = tf.nn.softmax(self._test_logit)
            elif model.selector == "cross_max":
                self._train_logit, train_repre = nrekit.network.selector.bag_cross_max(x_train, self.scope,
                                                                                       self.rel_tot, keep_prob=0.5)
                self._test_logit, test_repre = nrekit.network.selector.bag_cross_max(x_test, self.scope, self.rel_tot,
                                                                                     keep_prob=1.0)
                self._test_logit = tf.nn.softmax(self._test_logit)
            else:
                raise NotImplementedError

        # Classifier
        with tf.name_scope('classifier'):
            self._loss = nrekit.network.classifier.softmax_cross_entropy(self._train_logit, self.label, self.rel_tot,
                                                                         weights_table=self.get_weights())

    def loss(self):
        return self._loss

    def train_logit(self):
        return self._train_logit

    def test_logit(self):
        return self._test_logit

    def get_weights(self):
        with tf.variable_scope("weights_table", reuse=tf.AUTO_REUSE):
            print("Calculating weights_table...")
            _weights_table = np.zeros((self.rel_tot), dtype=np.float32)
            for i in range(len(self.train_data_loader.data_rel)):
                _weights_table[self.train_data_loader.data_rel[i]] += 1.0
            _weights_table = 1 / (_weights_table ** 0.05)
            weights_table = tf.get_variable(name='weights_table', dtype=tf.float32, trainable=False,
                                            initializer=_weights_table)
            print("Finish calculating")
        return weights_table


use_rl = False
model.encoder = 'cnn'
model.selector = 'att'
'''
if len(sys.argv) > 2:
    model.encoder = sys.argv[2]
if len(sys.argv) > 3:
    model.selector = sys.argv[3]
if len(sys.argv) > 4:
    if sys.argv[4] == 'rl':
        use_rl = True
'''

if use_rl:
    rl_framework = nrekit.rl.rl_re_framework(train_loader, test_loader)
    rl_framework.train(model, nrekit.rl.policy_agent,
                       model_name=dataset_name + "_" + model.encoder + "_" + model.selector + "_rl", max_epoch=60,
                       ckpt_dir="checkpoint")
else:
    ray.init()

    register_trainable('framework_train', framework.train)
    specs = {
        "stop": {
            "mean_accuracy": 0.99,
            "time_total_s": 600,
        },
        "config": {
            "learning_rate": grid_search([0.5, 0.1, 0.01, 0.001, 0.0001]),
            "batch_size": grid_search([40, 160, 640, 1280]),
            "max_length": 120, #just test for now
            #"max_length": grid_search([]) compute max length afterwards!!! It'll be hard to parallelize (have to re-preprocess every time I believe)
            "max_epoch": 4,
            "model": model,
            "model_name": dataset_name + "_" + model.encoder + "_" + model.selector
        }
    }
    tune.run('framework_train', name='TEST_HYPERPARAMS', **specs)
    #framework.train(model, model_name=dataset_name + "_" + model.encoder + "_" + model.selector, max_epoch=60,
    #                ckpt_dir="checkpoint", gpu_nums=1)
    # framework.train(model, model_name=dataset_name + "_" + model.encoder + "_" + model.selector, max_epoch=60, ckpt_dir="checkpoint", gpu_nums=0)
