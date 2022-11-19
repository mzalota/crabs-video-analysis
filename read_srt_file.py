
rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"

filepath = rootDir + "/R_20200916_194953_20200916_195355.srt"


# Using readlines()
file1 = open(filepath, 'r')
Lines = file1.readlines()

block_count = 0
count = 0
last_line_was_empty = True
index_of_last_empty_line = -1
blocks = list()
# Strips the newline character
#for line_num in range(0, len(Lines)):
while True:
    if count >= len(Lines):
        break

    line = Lines[count]
    striped_line = line.strip()
    if not striped_line:
        if not last_line_was_empty:
            block_count += 1
            block = Lines[index_of_last_empty_line+1:count]
            blocks.append(block)

        last_line_was_empty = True
        index_of_last_empty_line = count
        count += 1
        continue
    #count += 1
    last_line_was_empty = False

    count += 1
    #print("Line {}: {}".format(count, striped_line))
file1.close()

out_lines = list()

block_count2 = 0
for block in blocks:
    block_count2 += 1
    reading_num= block[0].strip()
    time = block[1].strip()
    date = block[2].strip()
    lat_lan = block[3].strip()
    if len(block) == 4 or lat_lan == "No data here":
        distance = 0.0
        distance_str = "none"
        distance_str3 = ""
        depth_alt = 0
    else:
        distance_str = block[4].strip()
        distance_str2 = distance_str[10:]
        distance_str3 = distance_str2[0:len(distance_str2)-2].strip()
        distance = float(distance_str3)
        depth_alt = block[5].strip()

    out_lines.append(reading_num+"\t"+str(distance)+"\n")

    print (reading_num, distance_str, distance_str3, distance)

    # for item in block:
    #     print ("item33: ", block_count2, item.strip())


filepath_out = rootDir + "/R_20200916_194953_20200916_195355/srt.csv"
file2= open(filepath_out, 'w')
file2.writelines(out_lines)
file2.close()

