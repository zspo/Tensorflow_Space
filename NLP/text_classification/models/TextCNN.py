# -*- coding: utf-8 -*-

'''
TextCNN
* embedding layers
* convolutinal layers
* max_pool
* softmax layers
'''

import numpy as np
import tensorflow as tf

class TextCNN(object):
    def __init__(self, filter_sizes, num_filters, num_classes, sequence_length, 
                 vocab_size, embedding_size,
                 initializer=tf.random_normal_initializer(stddev=0.1),
                 l2_reg_lambda=0.0):
        self.filter_sizes = filter_sizes
        self.num_filters = num_filters
        self.num_filters_total = self.num_filters * len(self.filter_sizes)
        self.num_classes = num_classes
        self.sequence_length = sequence_length
        self.vocab_size = vocab_size
        self.embedding_size = embedding_size
        self.initializer = initializer
        self.l2_reg_lambda = l2_reg_lambda

        self.input_x = tf.placeholder(tf.int32, [None, self.sequence_length], name='input_x')
        self.input_y = tf.placeholder(tf.int32, [None, self.num_classes], name='input_y')
        self.keep_prob = tf.placeholder(tf.float32, name='keep_prob')

        with tf.name_scope('weights'):
            self.Embedding = tf.get_variable(name='embedding', 
                                             shape=[self.vocab_size, self.embedding_size], 
                                             initializer=self.initializer)

        self.embedding_words = tf.nn.embedding_lookup(self.Embedding, self.input_x)
        self.sentence_embedding_expanded = tf.expand_dims(self.embedding_words, -1)

        pooled_outputs = []
        for i, filter_size in enumerate(self.filter_sizes):
            with tf.variable_scope('convolution-pooling-{}'.format(i)):
                filter = tf.get_variable(name='filter-{}'.format(filter_size),
                                         shape=[filter_size, self.embedding_size, 1, self.num_filters],
                                         initializer=self.initializer)
                conv = tf.nn.conv2d(self.sentence_embedding_expanded, 
                                    filter, 
                                    strides=[1, 1, 1, 1], 
                                    padding='VALID', 
                                    name='conv')
                
                b = tf.get_variable(name='b-{}'.format(filter_size), shape=[self.num_filters])
                h = tf.nn.relu(tf.nn.bias_add(conv, b), 'relu')

                pooled = tf.nn.max_pool(h, 
                                        ksize=[1, self.sequence_length - filter_size + 1, 1, 1],
                                        strides=[1, 1, 1, 1],
                                        padding='VALID',
                                        name='pool')
                pooled_outputs.append(pooled)

        self.h_pool = tf.concat(pooled_outputs, 3)
        self.h_pool_flatten = tf.reshape(self.h_pool, [-1, self.num_filtes_total])

        with tf.name_scope('dropout'):
            self.h_drop = tf.nn.dropout(self.h_pool_flatten, self.keep_drop)
        
        with tf.name_scope('output'):
            self.W = tf.get_variable(name='W',
                                     shape=[self.num_filters_total, self.num_classes],
                                     initializer=self.initializer)
            self.b = tf.get_variable(name='b', shape=[self.num_classes])
            l2_loss += tf.nn.l2_loss(b)
            self.logits = tf.matmul(self.h_drop, W) + self.b
            self.predictions = tf.argmax(self.logits, 1, name='predictions')

        with tf.name_scope('loss'):
            losses = tf.nn.softmax_cross_entropy_with_logits(logits=self.logits, labels=self.input_y)
            self.loss_val = tf.reduce_mean(losses) + self.l2_reg_lambda * l2_loss

        with tf.name_scope('accuracy'):
            correct_preditions = tf.equal(self.predictions, tf.argmax(self.input_y, 1))
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name='accuracy')
