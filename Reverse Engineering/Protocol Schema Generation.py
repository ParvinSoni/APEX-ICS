import sys
from lxml import etree
import xml.etree.ElementTree as ET
from collections import OrderedDict
import itertools
import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
from Levenshtein import ratio

# To generate static & dynamic fields. 
def generate_fields(schema):
    schema_list = {}
    length = max(len(elem) for elem in schema)
    for index in range (0, length):
        temp_list = [el[index] for el in schema if len(el) > index]
        if len(set(temp_list)) > 1:
            schema_list[index + 1] = [temp_list, "Dynamic"]
        else:
            schema_list[index + 1] = [temp_list, "Static"]  

    return schema_list

# Merging consecutive dynamic fields. 
def generate_merged_fields(schema, is_final_schema = False):
    schema_dict = OrderedDict()
    length = max(len(elem) for elem in schema)
    for index in range (0, length, 2):
        temp_list = [el[index: index + 2] for el in schema if len(el) > index]
        if index > 0:
            schema_list = list(schema_dict.items())
            prev_entry = schema_list[-1]
        else:
            prev_entry = None

        if prev_entry == None:
            if len(set(temp_list)) > 1:
                schema_dict[1] = [temp_list[0], 2, "Dynamic", LevenshteinSimilarityScore(temp_list), index]
            else:
                schema_dict[1] = [temp_list[0], 2, "Static", 1, index]

        elif len(set(temp_list)) > 1 and prev_entry[1][2] == "Dynamic" and index != min_len:
            new_list = []

            for el in schema:
                if len(el) > index:
                    new_list.append(el[index - int(prev_entry[1][1]) : index + 2])
                else:
                    new_list.append(el[index - int(prev_entry[1][1]) : ])
            if index > min_len or is_final_schema:
                schema_dict[prev_entry[0]] = [new_list[-1], int(prev_entry[1][1]) + 2 , "Dynamic", LevenshteinSimilarityScore(new_list), prev_entry[1][4]]
            else:
                SimilarByteOnly = LevenshteinSimilarityScore(temp_list) 
                if abs(SimilarByteOnly - float(prev_entry[1][3])) < float(0.03):
                    #print("Merging dynamic fields..") 
                    schema_dict[prev_entry[0]] = [new_list[-1], int(prev_entry[1][1]) + 2 , "Dynamic", LevenshteinSimilarityScore(new_list), prev_entry[1][4]]
                else: 
                    schema_dict[prev_entry[0] + 1] = [temp_list[-1],  2 , "Dynamic", SimilarByteOnly, index]
           
        
        elif len(set(temp_list)) > 1:
            schema_dict[int(prev_entry[0]) + 1] = [temp_list[-1], 2, "Dynamic", LevenshteinSimilarityScore(temp_list), index]
        
        elif len(set(temp_list)) == 1 and prev_entry[1][2] == "Static" and index != min_len:
            temp_list = [prev_entry[1][0] + temp_list[0]]
            schema_dict[int(prev_entry[0])] = [temp_list[0], int(prev_entry[1][1])+2 , "Static", 1, prev_entry[1][4]]
        elif len(set(temp_list)) == 1 :
            schema_dict[int(prev_entry[0]) + 1] = [temp_list[0], 2, "Static", 1, index]
    return schema_dict

# Gneerating Levenshtein matrix. 
def LevenshteinSimilarityScore(value_list):
    SimilarityScore = []    
    combination_list = list(itertools.combinations(value_list, 2))
    for each_com in combination_list:
        SimilarityScore.append(ratio(each_com[0], each_com[1]))
    SimilarityScore = np.array(SimilarityScore)
    if len(SimilarityScore) == 0:
        return 0
    return SimilarityScore.mean()

"""def get_jaro_winkler_similarity_score(value_list):
    jaro_list = []    
    combination_list = list(itertools.combinations(value_list, 2))
    for each_com in combination_list:
        #jaro_list.append(jarowinkler_similarity(each_com[0], each_com[1]))
        jaro_list.append(ratio(each_com[0], each_com[1]))
    jaro_list = np.array(jaro_list)
    if len(jaro_list) == 0:
        #print(len(value_list))
        return 0
    return jaro_list.mean()"""

# Defining M score, to identify probable keyfield. 
def get_probable_keyword_bytes(schema):
    # Control values of M
    keywords_list = []
    min_range = float(0.6)
    max_range = float(0.9)
    iteration = 1
    while max_range <= 1.0:
        for el in schema:
            val = schema.get(el)
            if int(val[4]) < min_len and val[2] == "Dynamic":
                #for i, el in enumerate(val[3]):
                if val[3] > min_range and val[3] < max_range:
                    keywords_list.append([int(val[4]), int(val[1]), val[3]]) 
        if len(keywords_list) > 0:
            return keywords_list
        else:
            iteration += 1
            max_range += 0.1
            print("Updating range for round" , iteration, "\n New range : \tmin_value = ", min_range, " \tmax_value = ", max_range)
               
    #print(keywords_list) 

    while min_range >= 0.40:
        for el in schema:
            val = schema.get(el)
            if int(val[4]) < min_len and val[2] == "Dynamic":
                if val[3] > min_range and val[3] < max_range:
                    keywords_list.append([int(val[4]), int(val[1]), val[3]]) 
        if len(keywords_list) > 0:
            return keywords_list
        else:
            iteration += 1
            min_range -= 0.1
            print("Updating range for round" , iteration, "\n New range : \tmin_value = ", min_range, " \tmax_value = ", max_range)
    return keywords_list    

# Generating final exctracted grammar for request/reponse. 
def get_final_keyword_field(schema):
    final_similarity = []
    for keyfield in probable_key_fields:
        print("\nComputing probability for keyfield: ", keyfield)
        inter_score_array = []
        intra_score_array = []
        len_variance_array = []
        each_schema = cluster_for_field(keyfield, schema)
        #print(each_schema)
        for key in each_schema:
            print("\tParsing key: ", key)
            if len(each_schema.get(key)) < 2:
                print("\t\t Key with only one pacekt in cluster ....")
                inter_score_array.append(0)
                intra_score_array.append(0)
                len_variance_array.append(0)
                #continue
            else: 
                print("\t\t Total number of packets in cluster = ", len(each_schema.get(key)))
                inter_score, intra_score = get_inter_intra_score(each_schema.get(key))
                len_variance = get_length_variance(each_schema.get(key))
                inter_score_array.append(inter_score)
                intra_score_array.append(intra_score)
                len_variance_array.append(len_variance)
        print("\n\tStatistics for keyfield: ", keyfield)
        print("\t\tIntra score array : ", intra_score_array)
        print("\t\tLength variance array: ", len_variance_array)
        inter_score_array = np.array(inter_score_array)
        intra_score_array = np.array(intra_score_array)
        len_variance_array = np.array(len_variance_array)
        intra_score_mean = intra_score_array.mean() if len(intra_score_array) > 0 else 0
        inter_score_mean = inter_score_array.mean() if len(intra_score_array) > 0 else 1
        len_variance_mean = len_variance_array.mean() if len(len_variance_array) > 0 else 0
        print("\t\tInitial M value: ", keyfield[2])
        print("\t\tFinal intra score: ", intra_score_mean)
        print("\t\tFinal inter score: ", inter_score_mean)
        print("\t\tFinal length variance: ", len_variance_mean)
        print("\t\tJoint Probability: ", keyfield[2]  * intra_score_mean   )#* len_variance_mean) #* (1 - inter_score_mean))
        print("\t\tFraction of clusters: ", (1 - (len(each_schema) / len(schema))))
        final_probability = keyfield[2]  * intra_score_mean      
        final_probability = final_probability * (1 - (len(each_schema) / len(schema)))        
        print("\t\tFinal Probability: ", final_probability)
        final_similarity.append([keyfield[0], keyfield[1], final_probability])
    print("\nProbabilty score for each keyfield: ", final_similarity)
    max_list = max(final_similarity, key=lambda sublist: sublist[2])
    return max_list
    

def cluster_for_field(keyfield, schema):
    keyfield_schema = {}
    #print (keyfield)
    for el in schema:
        key = el[keyfield[0]: keyfield[0] + keyfield[1]]
        #print("el: ", el, " key: ", key) 
        if key in keyfield_schema:
            val = keyfield_schema.get(key) 
            val.append(el)
            keyfield_schema[key] =  val
        else:
             keyfield_schema[key] = [el]
    return keyfield_schema

def generate_schema_for_keyfield(final_cluster):
    final_schema = {}
    for el in final_cluster:
        final_schema[el] = generate_merged_fields(final_cluster.get(el), is_final_schema=True)
    return final_schema
    

def generate_similarity_matrix(schema):
    LevenshteinList = []    
    combination_list = list(itertools.combinations(schema, 2))
    for each_com in combination_list:
        LevenshteinList.append([each_com[0], each_com[1], ratio(each_com[0], each_com[1])])
    return LevenshteinList

def get_inter_intra_score(value_list):
    set_value_list = set(value_list)
    inter_score = []
    intra_score = []
    for el in similarity_matrix:
        if el[0] in set_value_list and el[1] in set_value_list:
            intra_score.append(el[2])
        elif el[0] in set_value_list or el[1] in set_value_list:
            inter_score.append(el[2])
    inter_score = np.array(inter_score)
    intra_score = np.array(intra_score)
    return inter_score.mean(), intra_score.mean()

def get_length_variance(value_list):
    total_len = 0
    for el in value_list:
        total_len += len(el)
    avg_len = total_len / len(value_list)
    max_len = len(max(value_list, key = len))
    return avg_len / max_len



parser = argparse.ArgumentParser()

# Adding all the parameter to get the file names 
parser.add_argument('-i','--ifile', help='Input File Name (.xml)', required=True)
parser.add_argument('-p','--port', help='Port number', required=True)
#parser.add_argument('-s', '--sfile', help='Output Schema File Name (.pkl)', required=True)
#parser.add_argument('-t', '--hfile', help='Output Header File Name (.pkl)', required=True)
args = parser.parse_args()

argv = vars (args)

inputfile = ''
port_number = ''

# Parsing the arguments passed 
for opt in argv:
    if opt in ("i", "ifile"):
        inputfile = argv.get(opt)
    if opt in ("p", "port"):
        port_number = argv.get(opt)
    '''elif opt in ("s", "sfile"):
        outputfile = argv.get(opt)'''
    '''elif opt in ("t", "hfile"):
        head = argv.get(opt)'''

# Getting the root of the xml tree
# new_tree = etree.parse(inputfile)
# root = new_tree.getroot()
req = False
resp = False
schema_request = []
schema_response = []
schema_request_list = OrderedDict()
schema_response_list = {}
# Parsing the input xml file    
print("Parsing the input xml ...")
f = open("modbus_request_100.txt", "w")
for event, packet in ET.iterparse(inputfile):
    
    #print("Packet: ", packet.attrib['name']) if 'name' in packet.attrib else print("") 
    if 'name' in packet.attrib and packet.attrib['name'] == 'tcp.srcport':
        if packet.attrib['show'] == port_number:
            req = False
            resp = True
    if 'name' in packet.attrib and packet.attrib['name'] == 'tcp.dstport':
        if packet.attrib['show'] == port_number:
            #print("Found request packet") 
            req = True
            resp = False 
    if 'name' in packet.attrib and packet.attrib['name'] == 'tcp.payload':
        if req :
            schema_request.append(packet.attrib['value'])
            f.write(packet.attrib['value'])
            f.write('\n')
        elif resp : 
        #    schema_response.append(re.findall('..',proto.attrib['value']))
            schema_response.append(packet.attrib['value'])
        req = False
        resp = False

    if 'name' in packet.attrib and packet.attrib['name'] == 'udp.srcport':
        if packet.attrib['show'] == port_number:
            req = False
            resp = True
    if 'name' in packet.attrib and packet.attrib['name'] == 'udp.dstport':
        if packet.attrib['show'] == port_number:
            #print("Found request packet") 
            req = True
            resp = False 
    if 'name' in packet.attrib and packet.attrib['name'] == 'udp.payload':
        if req :
            schema_request.append(packet.attrib['value'])
            f.write(packet.attrib['value'])
            f.write('\n')
        elif resp : 
        #    schema_response.append(re.findall('..',proto.attrib['value']))
            schema_response.append(packet.attrib['value'])
        req = False
        resp = False    
f.close()

#print("Length of schema request: ", len(schema_request))

#for el in schema_request:
#    print(el)

min_len = len(min(schema_request, key=len))
print("Minimum payload length for request: ", min_len / 2 , " bytes")

schema_request_list = generate_merged_fields(schema_request)


'''
el_list = []
static_dynamic = []
for el in schema_request_list:
    el_list.append(el)
    static_dynamic.append(schema_request_list.get(el)[2])
plt.scatter(el_list, static_dynamic)
#plt.plot(el_list, static_dynamic)
plt.title("Static Dynamic field for request" )
plt.xlabel("Field")
plt.ylabel("Static/Dynamic") 
plt.show()

el_list = []
static_dynamic = []
for el in schema_response_list:
    el_list.append(el)
    static_dynamic.append(schema_response_list.get(el)[1])
plt.scatter(el_list, static_dynamic)
#plt.plot(el_list, static_dynamic)
plt.title("Static Dynamic field for response" )
plt.xlabel("Field")
plt.ylabel("Static/Dynamic") 
plt.show()
'''

for el in schema_request_list:
    print("Field no: ", el, " Field length: ",  schema_request_list.get(el)[1], " Field Type: ", schema_request_list.get(el)[2], " M-score: ", schema_request_list.get(el)[3], " Index position: ",  schema_request_list.get(el)[4])

'''
el_list = []
static_dynamic = []
for el in schema_request_list:
    #el_list.append(schema_request_list.get(el)[1])
    el_list.append(el)
    static_dynamic.append(schema_request_list.get(el)[3])
plt.scatter(el_list, static_dynamic)
plt.plot(el_list, static_dynamic)
plt.title("Similarity for request" )
plt.xlabel("Field")
plt.ylabel("value") 
plt.show()
'''
#print("\nGenerating similarity matrix...")
similarity_matrix = generate_similarity_matrix(schema_request)
probable_key_fields = get_probable_keyword_bytes(schema_request_list)
print("\nProbable Keyfields : ", probable_key_fields)

if len(probable_key_fields) == 0:
    sys.exit("\nPlease add more input packets.... No keyfield found. \nExiting....")

keyword_final =  get_final_keyword_field(schema_request)
print("\nKeyword Final : ", keyword_final)

final_cluster = cluster_for_field(keyword_final, schema_request)
#print("final cluster using keyword:")
#for el in final_cluster:
#    print("Key: ", el)
#    print("\t Available packets: ", final_cluster.get(el))

final_schema = generate_schema_for_keyfield(final_cluster)

print("\nFinal Grammar for request: ")

for el in final_schema:
    print("Protocol function : ", el)
    val = final_schema.get(el)
    for key in val:
        print("\t key: ", key, " val: ", val.get(key))


final_cluster = cluster_for_field(keyword_final, schema_response)
final_schema = generate_schema_for_keyfield(final_cluster)

print("\nFinal Grammar for response: ")

for el in final_schema:
    print("Protocol function : ", el)
    val = final_schema.get(el)
    for key in val:
        print("\t key: ", key, " val: ", val.get(key))

print("Parsing XML File...")
