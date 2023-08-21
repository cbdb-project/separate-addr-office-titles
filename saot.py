import pandas as pd
import re

def lstrip_word(string, word):   
    return re.sub(f'^{word}', '', string)

def rstrip_word(string, word):   
    return re.sub(f'{word}$', '', string)

def split_by_string(string, keyword):
	split_list = re.split(keyword, string, 1)
	return split_list[0] + keyword, split_list[1]

def refine_border_of_addr_and_office_raw(addr_raw, office_title_raw, addr_type_list):
	# refine the first word duplicated in office_title_raw. Ex: 新城縣縣尉 -> 新城|縣縣尉 will be refined to 新城縣|縣尉
	if len(office_title_raw) >= 2:
		if office_title_raw[0] == office_title_raw[1]:
			office_title_raw = office_title_raw[1:]
			addr_raw = addr_raw + office_title_raw[0]
			return addr_raw, office_title_raw, "refine the first word duplicated in office_title_raw"
	# don't do anything if office_title_raw is empty
	if len(office_title_raw) == 0:
		return addr_raw, office_title_raw, "don't do anything if office_title_raw is empty"
	# add address type to office_title_raw if the length of office_title_raw is 1. Ex 新城守 -> 新城|守 will be refined to 新城|城守
	for addr_type in addr_type_list:			
		if len(office_title_raw) == 1:
			addr_short = rstrip_word(addr_raw, addr_type)
			if addr_short != addr_raw:
				office_title_raw = addr_type + office_title_raw
				return addr_raw, office_title_raw, "add address type to office_title_raw if the length of office_title_raw is 1"
		else:
			office_title_short = lstrip_word(office_title_raw, addr_type)
			addr_short = rstrip_word(addr_raw, addr_type)
			# if address type is at both the end of address title and begining of office title. Don't do anything. Ex. 新城縣縣尉 -> 新城縣|縣尉
			if office_title_short != office_title_raw and addr_short != addr_raw:
				return addr_raw, office_title_raw, "if address type is at both the end of address title and begining of office title. Don't do anything."
			# # Deprecated! Reason: 西安知縣 -> 西安縣|知縣 which is wrong
			# # if address type is at the begining of office title, and not at the end of address title. Add address type to address title. Ex. 新城縣尉 -> 新城|縣尉 will be refined to 新城縣|縣尉
			# elif office_title_short != office_title_raw and addr_short == addr_raw:
			# 	addr_raw = addr_raw + addr_type
			# 	return addr_raw, office_title_raw, "if address type is at the begining of office title, and not at the end of address title. Add address type to address title."
			else:
				continue
	return addr_raw, office_title_raw, "do nothing"

def split_by_addr_belongs_pairs(input_list, addr_belongs_pairs_dict, addr_type_list, output_list):
	counter	= 0
	total_count = len(input_list)
	for input_row in list(input_list):
		counter += 1
		if counter % 10000 == 0:
			print("split_by_addr_belongs_pairs: " + "{:.2f}".format(counter/total_count*100) + "%" )
		for addr_belongs_pair, addr_belongs_component_list in addr_belongs_pairs_dict.items():
			if addr_belongs_pair in input_row:
				addr_raw, office_title_raw = split_by_string(input_row, addr_belongs_pair)
				addr_raw, office_title_raw, solution_log = refine_border_of_addr_and_office_raw(addr_raw, office_title_raw, addr_type_list)
				solution_log = "SPLIT: split_by_addr_belongs_pairs|REFINE: " + solution_log
				output_list.append([input_row, addr_raw, office_title_raw, addr_belongs_component_list[0], addr_belongs_component_list[1], solution_log])
				input_list.remove(input_row)
				break
	return input_list, output_list

def split_by_addr_name_list(input_list, addr_name_list, addr_type_list, output_list):
	counter	= 0
	total_count = len(input_list)
	for input_row in list(input_list):
		counter += 1
		if counter % 10000 == 0:
			print("split_by_addr_name_list: " + "{:.2f}".format(counter/total_count*100) + "%" )
		for addr_name in addr_name_list:
			if addr_name in input_row:
				office_title_raw = lstrip_word(input_row, addr_name)
				if office_title_raw != input_row:
					addr_raw = addr_name
					addr_raw, office_title_raw, solution_log = refine_border_of_addr_and_office_raw(addr_raw, office_title_raw, addr_type_list)
					solution_log = "SPLIT: split_by_addr_name_list|REFINE: " + solution_log
					output_list.append([input_row, addr_raw, office_title_raw, '', addr_name, solution_log])
					input_list.remove(input_row)
					break
	return input_list, output_list

def split_by_addr_type(input_list, addr_type_list, output_list):
	counter = 0
	total_count = len(input_list)
	for input_row in list(input_list):
		counter += 1
		if counter % 10000 == 0:
			print("split_by_addr_type: " + "{:.2f}".format(counter/total_count*100) + "%")
		if len(input_row) >= 3: # Ex: 歷縣尉
			for addr_type in addr_type_list:
				if input_row[0] == input_row[-1] and input_row[0] == addr_type: continue # 縣知縣 -> 縣|知縣 which is wrong
				if addr_type in input_row: # find address type in input_row
					if input_row[-1] == input_row[-3]:# To split 測試縣知縣 -> 測試縣|知縣. While 測試縣知縣 -> 測試縣知縣| is wrong
						input_row_splitted_list = input_row[:-1].rsplit(addr_type, 1)
						input_row_splitted_list[1] = input_row_splitted_list[1] + input_row[-1]
					else:
						input_row_splitted_list = input_row.rsplit(addr_type, 1)
					addr_raw = input_row_splitted_list[0] + addr_type
					office_title_raw = input_row_splitted_list[1]
					if addr_raw == addr_type: continue # 營參將 -> 營|參將 which is wrong
					addr_raw, office_title_raw, solution_log = refine_border_of_addr_and_office_raw(addr_raw, office_title_raw, addr_type_list)
					solution_log = "SPLIT: split_by_addr_type|REFINE: " + solution_log
					output_list.append([input_row, addr_raw, office_title_raw, '',  addr_raw, solution_log])
					input_list.remove(input_row)
					break
	return input_list, output_list

# 1. read data
print("1. read data")
input_list = [i[0] for i in pd.read_csv('input.txt', header=None, delimiter="\t").values.tolist()]
# input_list = [i[0] for i in pd.read_csv('input_small.txt', header=None).values.tolist()]
addr_belongs_pairs_list = pd.read_csv('supporting_data/cbdb_address_belongs_combination_pairs.csv').values.tolist()
addr_belongs_pairs_dict = {i[0] : [i[1], i[2]] for i in addr_belongs_pairs_list}
addr_name_list = [i[0] for i in pd.read_csv('supporting_data/cbdb_entity_addresses.csv').values.tolist()]
addr_type_list = [i[0] for i in pd.read_csv('supporting_data/cbdb_entity_address_types.csv').values.tolist()]

output_list = [] # output schema: [raw, addr_raw, office_title_raw, addr_upper, addr_lower, solution_log]

# 2. split
print("2. split_by_addr_belongs_pairs")
input_list, output_list = split_by_addr_belongs_pairs(input_list, addr_belongs_pairs_dict, addr_type_list, output_list)
print("2. split_by_addr_name_list")
input_list, output_list = split_by_addr_name_list(input_list, addr_name_list, addr_type_list, output_list)
print("2. split_by_addr_type")
input_list, output_list = split_by_addr_type(input_list, addr_type_list, output_list)

# 3. add the data that can't be split to output_list
print("3. add the data that can't be split to output_list")
if len(input_list) > 0:
	for input_row in input_list:
		output_list.append([input_row, '', input_row, '', '', 'can\'t seperate the data'])

print("4. output")
# 4. output
output_df = pd.DataFrame(output_list, columns=['raw', 'addr_raw', 'office_title_raw', 'addr_upper', 'addr_lower', 'solution_log'])
output_df.to_csv('output.csv', index=False)
output_df.to_excel('output.xlsx', index=False)

print("5. done")

