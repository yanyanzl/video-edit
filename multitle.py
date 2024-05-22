"""
generate a merged file for both subtitles in two files (.srt file)
the merged file will include both language according to the time line

you can generate a batch of merged files all together
in this non-GUI version, you have to name the batch of files 
according to the rules:


"""
import os
import sys
import datetime

# maximum number of lines for each subtitle in a screen
MAX_LINES_SUBTITLE = 4

# maximum number of subtitle files to be merged and generated
FILES_NUMBER = 1000

# remove lines for advitisement or other lines not to be included in the merged files.
WORDS_IN_REMOVING_LINE = ["www","WWW"]

# these are the rules for the name of the files for non-GUI version
''' base language file name. the name of those files should be base_language1, base_language2, ... '''
LANGUAGE1_FILE_NAME = "base_language"

''' added language file name. the name of those files should be added_language1, added_language2, ... '''
LANGUAGE2_FILE_NAME = "added_language"

''' generated language file name.  can't be changed.'''
GENERATED_FILE_NAME = "multilanguage"

# current_path = os.path.abspath(os.getcwd())
# get the directory of the script being run
# current_path = os.path.dirname(os.path.abspath(__file__))

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    current_path = os.path.dirname(sys.executable)
elif __file__:
    current_path = os.path.dirname(__file__)

print("the directory of the script being run is:", current_path)

sub_folder = "/"


def gen_dual_file(language1_file, language2_file,dual_language_file):
    '''
        generate merged a subtitle file with language 1 and language 2. 
        the file will be saved as dual_language_file.
        language 1 will be used as the base for the merge. 
        all the contents will be included in the merged file.
        contents in language 2 files will be merged if the timestamp (to second) 
        is the same as in the language 1 files
    '''

    # Chinese_lines = ""
    # english_lines = ""
    dual_lines = ""

    try:

        with open(
            language1_file,
        ) as readfile1:
            
            lang1_lines = readfile1.readlines()

        with open(
            language2_file,
        ) as readfile2:
            
            lang2_lines = readfile2.readlines()



        for line in lang1_lines:
            if "-->" not in line:
                if not any(_ in line for _ in WORDS_IN_REMOVING_LINE):
                    dual_lines += line

            # line contains --> is time stamp. 
            else:
                # add time stamp to the file first.
                dual_lines += line
                
                # if the timestamp can be found in language 2 file. 
                starttime1, endtime1 = stamp_split(line)

                for line2 in lang2_lines:
                    if "-->" not in line2:
                        continue
                    else:
                        starttime2, endtime2 = stamp_split(line2)
                        start_difference = starttime2 - starttime1
                        start_difference = start_difference.total_seconds()
                        
                        end_difference = endtime2 - endtime1
                        end_difference = end_difference.total_seconds()
                        
                        start2_end1_difference = starttime2 - endtime1
                        start2_end1_difference = start2_end1_difference.total_seconds()

                        # time range in language 2 within time range in language 1
                        # add language 2 to merged file.
                        if start_difference >= 0:
                            if end_difference <= 0 or start2_end1_difference < 0:
                                lang2_len = len(lang2_lines)
                                lang2_lines = lang2_lines[lang2_lines.index(line2):lang2_len]
                                lang2_len = len(lang2_lines)
                                i = 1
                                lang2_line = ""
                                while i < MAX_LINES_SUBTITLE and i < lang2_len:
                                    if lang2_lines[i] != "\n":
                                        lang2_line += lang2_lines[i]
                                        i += 1
                                    else:
                                        break
                                lang2_lines = lang2_lines[i:len(lang2_lines)]
                                dual_lines += lang2_line
                                # add language 2 and break.
                                break
                            else:
                                # start time in language 2 beyond that in language 1
                                # but not in the range of the time in that line in language 1
                                # no match break
                                break
                        # start time is beyond the end time of language 1. 
                        # stop checking the remain lines in language 2
                        # no match break
                        elif start2_end1_difference > 0:
                            break

    except OSError:
        print("Could not open/read file:", language1_file, "or file: ", language2_file)
        raise

    try:

        with open(dual_language_file, "w") as writefile:

            writefile.writelines(dual_lines)
    except OSError:
        print("Could not open/write file", dual_language_file, "maybe no authorization for access:")
        raise

def main():

    try:

        i = 1
        while i <= FILES_NUMBER:

            langugae1_path = current_path + sub_folder + LANGUAGE1_FILE_NAME + str(i) + ".srt"
            langugae2_path = current_path + sub_folder + LANGUAGE2_FILE_NAME + str(i) + ".srt"
            multi_language_path = current_path + sub_folder + GENERATED_FILE_NAME + str(i) + ".srt"
        
            gen_dual_file(langugae1_path, langugae2_path, multi_language_path)

            i += 1

    except OSError as e:
        if i > 1:
            print(i-1, " files successfully merged and generated.")
        else:
            print(" can't open files: ", langugae1_path, " or ", langugae2_path)

        sys.exit()


def stamp_split(timestamp):
    """
    split timestamp in srt file to two parts and 
    remove milliseconds and whitespaces
    "00:14:27,680 --> 00:14:29,760" to "00:14:27" and "00:14:29"
    """
    # timestamp = "00:14:27,680 --> 00:14:29,760"
    stamp1, stamp2 = timestamp.split('-->', 1)

    # remove milliseconds
    stamp1,stamp11 = stamp1.split(',', 1)
    stamp2,stamp21 = stamp2.split(',', 1)
    # remove whitespaces
    stamp1 = stamp1.strip()
    stamp2 = stamp2.strip()

    stamp1 = datetime.datetime.strptime(stamp1, '%H:%M:%S')
    stamp2 = datetime.datetime.strptime(stamp2, '%H:%M:%S')
    # print("stamp1:", stamp1 in "00:14:27,960 --> 00:14:29,760")
    # print("stamp2:", stamp2 in "00:14:27,960 --> 00:14:29,760")
    # print("lang2:", lang2)
    # time_difference = stamp2 - stamp1
    # print("d2-d1", time_difference.seconds)

    return stamp1, stamp2



main()

