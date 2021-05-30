import re
import logging

log = logging.getLogger(__name__)

def remove_special_chars(text):
    """
        Remove the special characters from the passing parameters
    """
    try:
        # remove more than one continuos dots
        text = re.sub(r"(\.\.+)", r" ", text)
        #    text = re.sub(r'\“', r' ', text) # remove asci char
        #    text = re.sub(r'\”', r' ', text) # remove asci char
        text = re.sub(r"[\…\”\“\’]", r"", text)  # remove asci chars
        # remove more than one continuos hypens
        text = re.sub(r"(\-\-+)", r" ", text)
        text = re.sub(
            r"\b([a-zA-Z]+)\/([0-9]+)\b", r"\1 \2", text
        )  # remove slash beween alpha and numbers only
        text = re.sub(
            r"\-+\>", r" ", text
        )  # remove more than one continuos hypens end with >
        # remove ( ) if a word contains
        text = re.sub(r"(\()(\w+)(\))", r" \2 ", text)
        #    text = re.sub(r',.?$', r' ', text) # replace only ends
        #    with chars
        text = re.sub(r"[\?\;\"\<\>\:\[\]\(\)\|,\*,\_]",
                      r" ", text)  # remove special chars
        text = re.sub(r"[\'\~\!]", r"", text)  # remove special chars
        text = re.sub(
            r"\b([0-9A-Za-a]{3,})+\/+([0-9A-Za-z]{5,})\b", r"\1 \2", text)  # split words which contain / between the words
        text = re.sub(
            r"([\,\.\#])(?!\S)", r"", text
        )  # remove special chars at end of each words
        text = re.sub(r"\n", r":", text)
        text = re.sub(r"\s+", r" ", text)  # multi space to single space
        text = re.sub(r":", "\n", text)
        while " \n" in text:
            text = text.replace(" \n", "\n")
        while "\n " in text:
            text = text.replace("\n ", "\n")
        while "\n\n" in text:
            text = text.replace("\n\n", "\n")
    except Exception as e:
        log.error("An error is occured while removing special chars {}".format(e))

    return text.strip()
def pre_processing(text):
    """
        The function will the pre-processing steps to remove special chars,
        get the first mail content from trailing mail conversation
    """
    try:
        #text = _remove_special_chars(text)
        # Apply logic to get first mail content from trailing mail
        regexp = r'(From +)'
        matches = []
        for m in re.finditer(regexp, text):
            matches.append(m)
        if len(matches)>=2:
            text = text[0:matches[1].start()] # get mail content from oth index till 2nd trailing mail conversation
    except Exception as e:
        log.error("An error is occured while doing pre-processing operation {}".format(e))
    return text

def post_processing(prediction_result):
    """
        The function will do removing unwanted chars/words from the predicted entities
    """
    try:
        regexp_words_with_special_chars = r"(?:^|(?<= ))[a-zA-Z\#\/\-\–]+(?= |$)"
        regexp_for_specials_chars_beginig = r"(po-|po|po#|pono|p.o.|p.o|no|#|k|h|b)[0-9]+"
        regexp_for_specials_chars_ending = r"[0-9]+(\/|\-|\#)+$"

        # remove the words alone from the extracted entities
        for idx, entity in enumerate(prediction_result["entities"]):
            # print("current entity {}".format(entity))          
            

            if entity["type"] == "QUANTITY":
                matches = re.findall("\d+", entity["text"]) 
                if(len(matches) >= 2):
                    if "st" in entity["text"].lower():                    
                        #qty = matches[-1] # consider the last index of value as quantity                  
                        qty_index= entity["text"].lower().index("st")+3
                        prediction_result["entities"][idx]["start_pos"] = prediction_result["entities"][idx]["start_pos"] + qty_index                  
                        prediction_result["entities"][idx]["text"] = entity["text"][qty_index:len(entity["text"])]
                  
            # remove additional words(such as order no, sales order, po, po #) which are extracted by the ML model
            if entity["type"] == "ACCOUNT_NO" or entity["type"] == "PO_NO" or entity["type"] == "SALES_ORDER":
                # print(entity)
                _text = entity["text"].split(" ")
                is_end_offset_change = False
                final_text = ""
                is_made_any_change_in_start_offset = False
                is_made_any_change_in_end_offset = False
                for txt in _text:
                    matches = re.findall(
                        regexp_words_with_special_chars, txt.lower())
                    if matches:
                        if not is_end_offset_change:
                            prediction_result["entities"][idx]["start_pos"] = prediction_result["entities"][idx]["start_pos"] + len(
                                txt)+1 # to take space for count and increase the start offset
                            is_made_any_change_in_start_offset = True
                        elif is_end_offset_change:
                            prediction_result["entities"][idx]["end_pos"] = prediction_result["entities"][idx]["end_pos"] - len(
                                txt)-1 # to take space for count and reduce the end offset
                            is_made_any_change_in_end_offset = True
                    else:
                        final_text = "{} {}".format(final_text, txt)
                        is_end_offset_change = True

                prediction_result["entities"][idx]["text"] = final_text.strip(
                ) if final_text.lower().strip() != "" else entity["text"]
                # matches = re.findall(regexp, entity["text"].lower())
                # print("matches {}".format(matches))
                # for match_text in matches:
                #     prediction_result["entities"][idx]["text"] = prediction_result["entities"][idx]["text"].replace(
                #         match_text, "").strip()
                #     prediction_result["entities"][idx]["start_pos"] = prediction_result["entities"][idx]["start_pos"] + len(
                #         match_text)

                # find special chars begining of string
                matches = re.findall(
                    regexp_for_specials_chars_beginig, entity["text"].lower())
                # print("begining matches {}".format(matches))
                for match_text in matches:
                    prediction_result["entities"][idx]["text"] = prediction_result["entities"][idx]["text"].lower().replace(
                        match_text, " ").strip()
                    prediction_result["entities"][idx]["start_pos"] = prediction_result["entities"][idx]["start_pos"] + len(
                        match_text)
                    is_made_any_change_in_start_offset = True
                    # print(prediction_result["entities"][idx]["text"])

                # find special chars end of string
                matches = re.findall(
                    regexp_for_specials_chars_ending, entity["text"].lower())
                # print("begining matches {}".format(matches))
                for match_text in matches:
                    prediction_result["entities"][idx]["text"] = prediction_result["entities"][idx]["text"].lower().replace(
                        match_text, " ").strip()
                    prediction_result["entities"][idx]["end_pos"] = prediction_result["entities"][idx]["end_pos"] - len(
                        match_text)
                    # is_made_any_change_in_end_offset = True

                #if is_made_any_change_in_end_offset:
                #    prediction_result["entities"][idx]["end_pos"] = prediction_result["entities"][idx]["end_pos"] - 1
                #if is_made_any_change_in_start_offset:
                #    prediction_result["entities"][idx]["start_pos"] = prediction_result["entities"][idx]["start_pos"] + 1

    except Exception as exp:
        log.error("An error is occured while perform post-processing {}".format(exp))

    return prediction_result

