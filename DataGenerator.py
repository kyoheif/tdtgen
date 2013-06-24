# -*- coding: utf-8 -*-

# global variables
#multiple_key_dic = {}
#tables_dic = {}

# loader


def load_yaml(filename):
    import yaml
    stream = file(filename, 'r')
    line = yaml.load(stream)
    return line

# builder
def build_columns_data(count, columns):
    data = {}
    data["__names__"] = []
    for item in columns:
        name = item["name"]
        data["__count__"] = count
        data["__names__"].append(name)
        data[name] = generator_helper(count, item)
        # zfill format
        if "zfill" in item:
            n = item["zfill"]
            data[name] = zero_fill_int_list(n, data[name])
        # prefix format
        if "prefix" in item:
            prefix = item["prefix"]
            data[name] = append_prefix(prefix, data[name])
    return data

def build_multiple_key_hash(multiple_key_line):
    data = {}
    for line in multiple_key_line:
        name = line["name"]
        count = line["count"]
        columns = line["columns"]
        data[name] = build_columns_data(count, columns)
    return data

def build_table_hash(table_line):
    data = {}
    for line in table_line:
        name = line["name"]
        count = line["count"]
        columns = line["columns"]
        data[name] = build_columns_data(count, columns)
    return data

# helper
def generator_helper(count, line):
    generator_name = u'generate_' + line["type"] + u'_list'
    generator = eval(generator_name)
    param = line["param"]
    name = line["name"]
    return generator(count, param)

# formatter
def zero_fill_int_list(n, list):
    ret = []
    format = u'%0' + str(n) + u'd'
    for num in list:
        ret.append(format % num)
    return ret

def append_prefix(prefix, list):
    ret = []
    for item in list:
        ret.append(prefix + item)
    return ret

def append_suffix(suffix, list):
    ret = []
    for item in list:
        ret.append(item + suffix)
    return ret

# generators
def generate_multiple_key_list_impl(count, key_name, column_name, order, duplicate):
    # check multiple key dic
    multiple_key_set = multiple_key_dic[key_name]
    column = multiple_key_set[column_name]
    ret = []
    if count > len(column):
        if order and duplicate == u'rotate':
            l = len(column)
            m = count % l
            for i in xrange(count / l):
                ret.extend(column[:])
            ret.extend(column[:m])
    else:
        ret.extend(column[:count])
    return ret

def generate_multiple_key_list(count, param):
    order = param["order"]
    duplicate = param["duplicate"]
    key_name = param["key_name"]
    column_name = param["column_name"]
    return generate_multiple_key_list_impl(count, key_name, column_name, order, duplicate)


import random
def generate_random_int_list_impl(count, start, end):
    ret = []
    for i in xrange(count):
        ret.append(random.randint(start, end))
    return ret

def generate_random_int_list(count, param):
    start = param["start"]
    end = param["end"]
    return generate_random_int_list_impl(count, start, end)

def generate_sequential_int_list_impl(count, start, step):
    stop = start + step * count
    return range(start, stop, step)

def generate_sequential_int_list(count, param):
    start = param["start"]
    step = param["step"]
    return generate_sequential_int_list_impl(count, start, step)

def generate_same_number_list_impl(count, number):
    ret = []
    for i in xrange(count):
        ret.append(number)
    return ret

def generate_same_number_list(count, param):
    number = param["number"]
    return generate_same_number_list_impl(count, number)

def generate_random_float_list_impl(count, start, end):
    ret = []
    for i in xrange(count):
        ret.append(random.uniform(start, end))
    return ret

def generate_random_float_list(count, param):
    start = param["start"]
    end = param["end"]
    return generate_random_float_list_impl(count, start, end)

def generate_random_string_list_impl(count, length, is_fixed_length):
    r = []
    if is_fixed_length:
        r = generate_same_number_list_impl(count, length)
    else:
        r = generate_random_int_list_impl(count, 1, length)
    ret = []
    for n in r:
        ret.append(generate_random_string(n))
    return ret

def generate_random_string_list(count, param):
    length = param["length"]
    is_fixed_length = param["is_fixed_length"]
    return generate_random_string_list_impl(count, length, is_fixed_length)

def generate_random_string(length):
    import string
    alphabets = string.digits + string.letters
    return ''.join(random.choice(alphabets) for i in xrange(length))

def generate_random_item_list_impl(count, choices, length, is_fixed_length, is_duplicated):
    r = []
    if is_fixed_length or length == 1:
        r = generate_same_number_list_impl(count, length)
    else:
        r = generate_random_int_list_impl(count, 1, length)
    ret = []
    sampler = generate_no_duplicate_item_list
    if is_duplicated:
        sampler = generate_item_list
    for n in r:
        ret.append(sampler(choices, n))
    return ret

def generate_random_item_list(count, param):
    choices = param["choices"]
    length = param["length"]
    is_fixed_length = param["is_fixed_length"]
    is_duplicated = param["is_duplicated"]
    return generate_random_item_list_impl(count, choices, length, is_fixed_length, is_duplicated)

def generate_item_list(choices, length):
    ret = []
    for i in xrange(length):
        ret.append(random.choice(choices))
    return ret

def generate_no_duplicate_item_list(choices, length):
    c = choices[:]
    for i in xrange(length):
        index = random.randint(i, len(c)-1)
        c[i],c[index] = c[index],c[i]
    return c[:length]


if __name__ == '__main__':
    # load data file
    line = load_yaml('data.yaml')
    
    # build multiple_key
    multiple_key_line = line["multiple_key"]
    global multiple_key_dic
    multiple_key_dic = build_multiple_key_hash(multiple_key_line)
    
    # build tables
    tables_line = line["tables"]
    global tables_dic
    tables_dic = build_table_hash(tables_line)
    
    # cvs format
    for name, table in tables_dic.items():
        print name
        for i in xrange(table["__count__"]):
            for column in table["__names__"]:
                print str(table[column][i]) + ',',
            print ' '
    
    # test print
    #print "multiple_key_dic:" + str(multiple_key_dic)
    #print "tables_dic:" + str(tables_dic)
