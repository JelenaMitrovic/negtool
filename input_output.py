import sys

def read_parsed_data(filename, mode):
    with open(filename, 'r') as infile:
        sentence = {}
        counter = 0
        instances = []
        for line in infile:
            token_dict = {}
            tokens = line.split()
            if len(tokens) == 0:
                for key in sentence:
                    head_index = int(sentence[key]['head']) - 1
                    if head_index > -1:
                        sentence[key]['head-pos'] = sentence[head_index][5]
                    else:
                        sentence[key]['head-pos'] = sentence[key][5]

                instances.append(sentence)
                sentence = {}
                counter = 0
                continue
            if counter == 0 and tokens[0] != '1':
                print "ERROR: Trying to read file that is not (properly) parsed"
                sys.exit(1)
            for i in range(3):
                if tokens[i] != "_":
                    token_dict[i+2] = tokens[i]
            if mode == 'raw':
                token_dict[5] = tokens[3]
                token_dict['head'] = tokens[5]
                token_dict['deprel'] = tokens[6]
            else:
                token_dict[5] = tokens[4]
                token_dict['head'] = tokens[6]
                token_dict['deprel'] = tokens[7]
            sentence[counter] = token_dict
            counter += 1
    return instances
            
def read_cuepredicted_data(filename, mode):
    if mode == 'raw':
        lower_limit = 4
        upper_limit = 6
    else:
        lower_limit = 3
        upper_limit = 7
    cue_offset = upper_limit - 5
    with open(filename, 'r') as infile:
        sentence = {}
        cues = []
        mw_cues = []
        scopes = {}
        events = {}
        line_counter = 0
        counter = 0
        cue_counter = 0
        prev_cue_column = -1
        instances = []

        for line in infile:
            token_dict = {}
            tokens = line.split()
            #check for sentence end
            if len(tokens) == 0:
                for key in sentence:
                    head_index = int(sentence[key]['head']) - 1
                    if head_index > -1:
                        sentence[key]['head-pos'] = sentence[head_index][5]
                    else:
                        sentence[key]['head-pos'] = sentence[key][5]

                if len(scopes) != len(cues):
                    for i in range(len(cues)):
                        if not i in scopes:
                            scopes[i] = []

                sentence['cues'] = cues
                sentence['mw_cues'] = mw_cues
                sentence['scopes'] = scopes
                sentence['events'] = events
                    
                if len(cues) > 0:
                    sentence['neg'] = True
                else:
                    sentence['neg'] = False

                #yield sentence
                instances.append(sentence)
                sentence = {}
                counter = 0
                prev_cue_column = -1
                cues = []
                mw_cues = []
                scopes = {}
                events = {}
                line_counter += 1
                continue

            for i in range(len(tokens)):            
                if tokens[i] != "_" and i < lower_limit:
                    token_dict[i+2] = tokens[i]
                #cue column
                elif tokens[i] != "***" and tokens[i] != "_" and i > upper_limit and (i-cue_offset) % 3 == 0:
                    if i == prev_cue_column:
                        cues[-1][2] = 'm'
                        prev_cue_column = i
                        if cues[-1][2] == 'm':
                            mw_cues.append([cues[-1][0],cues[-1][1]])
                        mw_cues.append([tokens[i], counter])
                    elif tokens[i] != tokens[1]:
                        cues.append([tokens[i], counter, 'a'])
                        prev_cue_column = i
                    else:
                        cues.append([tokens[i], counter, 's'])
                        prev_cue_column = i
                #scope column
                elif tokens[i] != "***" and tokens[i] != "_" and i > upper_limit and (i-cue_offset-1) % 3 == 0:
                    cue_counter = (i-upper_limit+2)/3
                    if cue_counter in scopes:
                        scopes[cue_counter].append([tokens[i], counter])
                    else:
                        scopes[cue_counter] = [[tokens[i], counter]]
                elif tokens[i] != "***" and tokens[i] != "_" and i > upper_limit and (i-cue_offset-2) % 3 == 0:
                    cue_counter = (i-upper_limit+3)/3
                    events[cue_counter] = tokens[i]

            if mode == 'raw':
                token_dict['head'] = tokens[5]
                token_dict['deprel'] = tokens[6]
            else:
                token_dict[5] = tokens[4]
                token_dict['head'] = tokens[6]
                token_dict['deprel'] = tokens[7]

            sentence[counter] = token_dict
            counter += 1
            line_counter += 1
        return instances