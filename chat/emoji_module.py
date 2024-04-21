import emoji

#키워드와 이모티콘을 매칭해서 저장
replace_emoji_dict = {"사랑" : emoji.emojize(':beating_heart:'), "안녕":emoji.emojize(':hand_with_fingers_splayed:'), 
                      "박수":emoji.emojize(':clapping_hands:'), "ㅋㅋ":emoji.emojize(':face_with_hand_over_mouth:'), 
                      "엥":emoji.emojize(':face_with_open_eyes_and_hand_over_mouth:'), "황당":emoji.emojize(':face_screaming_in_fear:'),
                      "ㅎㅎ":emoji.emojize(':smiling_face_with_open_hands:'), "공부":emoji.emojize(':writing_hand:'),
                        "짜증":emoji.emojize(':face_with_symbols_on_mouth:'), "바보":emoji.emojize(':shaking_face:'),
                        "굿":emoji.emojize(':thumbs_up:'), "짱":emoji.emojize(':thumbs_up:'), "/일등":emoji.emojize(':1st_place_medal:'),
                        }

add_emoji_dict = {"/사랑" : emoji.emojize(':beating_heart:'), "/안녕":emoji.emojize(':hand_with_fingers_splayed:'), 
                      "/박수":emoji.emojize(':clapping_hands:'), "/ㅋㅋ":emoji.emojize(':face_with_hand_over_mouth:'), 
                      "/엥":emoji.emojize(':face_with_open_eyes_and_hand_over_mouth:'), "/황당":emoji.emojize(':face_screaming_in_fear:'),
                      "/ㅎㅎ":emoji.emojize(':smiling_face_with_open_hands:'), "/공부":emoji.emojize(':writing_hand:'),
                        "/짜증":emoji.emojize(':face_with_symbols_on_mouth:'), "/바보":emoji.emojize(':shaking_face:'),
                        "/굿":emoji.emojize(':thumbs_up:'),  "/일등":emoji.emojize(':1st_place_medal:'),"/짱":emoji.emojize(':thumbs_up:'),
                        "/이등":emoji.emojize(':2nd_place_medal:'), "/삼등":emoji.emojize(':3rd_place_medal:'),
                        "/산타":emoji.emojize(':Santa_Claus_light_skin_tone:'), "/외계인":emoji.emojize(':3rd_place_medal:')}

#이모티콘 키워드 대체 함수
def replace_emoji_to_message(msg):
    for key in replace_emoji_dict:
        if key in msg:
            msg  = msg.replace(key,replace_emoji_dict[key])
    return msg

#이모티콘 사용 함수
def add_emoji_to_message(msg):
    for key in add_emoji_dict:
        if key in msg:
            msg  += msg.replace(key,add_emoji_dict[key])
    return msg