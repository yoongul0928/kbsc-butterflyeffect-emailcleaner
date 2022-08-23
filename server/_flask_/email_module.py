import smtplib, email
import pandas as pd
import imaplib, email
from email.header import decode_header, make_header
from email.mime.text import MIMEText
import os
import pickle

PATH = os.getcwd()
PATH = "E:/workspace/kbsc-butterflyeffect-emailcleaner/server/_flask_"
eg_loaded_model = pickle.load(open(PATH + '/pkl/eg_model_NB.pkl', 'rb'))
eg_tdmvector = pickle.load(open(PATH + '/pkl/eg_tdmvector.pkl','rb')) 
eg_tfidf_transformer = pickle.load(open(PATH + '/pkl/eg_tfidf_transformer.pkl','rb'))
kr_loaded_model = pickle.load(open(PATH + '/pkl/kr_model_NB.pkl', 'rb'))
kr_tdmvector = pickle.load(open(PATH + '/pkl/kr_tdmvector.pkl','rb')) 
kr_tfidf_transformer = pickle.load(open(PATH + '/pkl/kr_tfidf_transformer.pkl','rb'))

def get_body(email_message):
    """
    WIP
    메세지를 받아서 바디부분을 파싱하는 함수
    파싱 결과와 바디 문자열을 리턴한다
    """

    res = "ERROR"

    body_ = ""
    try:
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                email_data = body.decode()
                body_ += email_data + "\n"
            elif part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True)
                email_data = html_body.decode()
                body_ += email_data + "\n"
    except Exception as e:
        res = "ERROR"
        body_ = e
    else:
        res = "OK"
    return res, body_

def count_inbox(email_address, password):
    """
    사용자의 메일 주소와 비밀번호를 입력받아서 메일 개수를 가져오는 함수
    """

    imap_host = 'imap.'+ email_address.split("@")[1]

    obj = imaplib.IMAP4_SSL(imap_host, 993)
    obj.login(email_address, password)
    obj.select('Inbox')

    _, data = obj.search(None, "ALL")
    
    obj.close()
    obj.logout()

    return len(data[0].split())

def fetch_emails(email_address, password):
    """
    사용자의 메일 주소와 비밀번호를 받아서 모든 메일을 읽어오는 함수
    """
    #imap login, fetch
    imap_host = 'imap.'+ email_address.split("@")[1]
    obj = imaplib.IMAP4_SSL(imap_host, 993)
    obj.login(email_address, password)
    obj.select('Inbox')

    _, all_data = obj.fetch('1:*' , '(RFC822)')
    obj.close()
    obj.logout()
    #Remove Bytes & Reverse
    all_data = all_data[0::2]
    all_data.reverse()
    df_mail_list = pd.DataFrame()
    
    #Parse Message
    for n, data in enumerate(all_data):
        email_message = email.message_from_bytes(data[1])

        date_ = make_header(decode_header(email_message["Date"]))
        from_ = make_header(decode_header(email_message["From"]))

        while True:
            try:
                subject_= make_header(decode_header(email_message['Subject']))
                break
            except TypeError:
                subject_= make_header(decode_header(str(email_message['Subject'])))
                break
        pred_ = emailClassification(subject_)
        
        res, body_ = get_body(email_message)

        df = pd.DataFrame({"index": n, "date": str(date_), "subject": str(subject_), "sender": str(from_), "body": body_, "pred" : pred_}, index=[n])
        #df = pd.DataFrame({"index": n, "date": str(date_), "subject": str(subject_), "sender": str(from_), "pred" : pred_}, index=[n])
        
        df_mail_list = pd.concat([df_mail_list, df])

    return df_mail_list

def emailClassification(subject_):
    """
    메일 제목을 받아서 메일의 종류를 판단하는 함수
    """
    test_email = [{'email_title' : str(subject_)}]
    df_test_email = pd.DataFrame(test_email)
    #print(df_test_email)
    lang = isEnglishOrKorean(str(subject_))
    if lang == 'k':
        test_x_email = df_test_email['email_title']
        test_x_tdm = kr_tdmvector.transform(test_x_email)
        test_x_tfidfv = kr_tfidf_transformer.transform(test_x_tdm)
        pred = kr_loaded_model.predict(test_x_tfidfv)
    elif lang == 'e':
        test_x_email = df_test_email['email_title']
        test_x_tdm = eg_tdmvector.transform(test_x_email)
        test_x_tfidfv = eg_tfidf_transformer.transform(test_x_tdm)
        pred = eg_loaded_model.predict(test_x_tfidfv)
    else:
        pred = 0
    return pred

# 이메일 언어 분류
def isEnglishOrKorean(input_s):
    """
    문자열을 받아서 영어인지 한글인지 판단하는 함수
    k: 한글, e: 기타, o: 영어
    """
    k_count = 0
    e_count = 0
    o_count = 0
    if input_s != input_s:
        return "o"
    for c in input_s:
        if ord('가') <= ord(c) <= ord('힣'):
            k_count+=1
        elif ord('a') <= ord(c.lower()) <= ord('z'):
            e_count+=1
        else:
            o_count+=1
    if k_count>1:
        return "k"  # 한글
    elif e_count>1:
        return "e"  # 기타
    else:
        return "o"  # 영어

def delete_email(email_address, password, emailList):
    """
    사용자의 메일 주소, 비밀번호, 삭제하려는 메일 리스트를 받아 삭제하고 결과, 삭제한 메일 개수와 데이터 리스트를 리턴하는 함수
    """
    imap_host = 'imap.'+ email_address.split("@")[1]
    obj = imaplib.IMAP4_SSL(imap_host, 993)
    obj.login(email_address, password)
    obj.select('Inbox')

    #search email
    _, search_data = obj.search(None, 'ALL')
    all_email = search_data[0].split()
    all_email.reverse()
    #get email data
    mail_numbers = ""
    for n, i in enumerate(emailList):
        if(n != 0): 
            mail_numbers += ","
        mail_numbers += str(len(all_email) - i)
    
    _, all_data = obj.fetch(mail_numbers , '(RFC822)')

    #Remove Bytes & Reverse
    all_data = all_data[0::2]
    all_data.reverse()

    df_mail_list = pd.DataFrame()

    #Parse Message
    for n, data in enumerate(all_data):

        email_message = email.message_from_bytes(data[1])

        date_ = make_header(decode_header(email_message["Date"]))
        from_ = make_header(decode_header(email_message["From"]))

        while True:
            try:
                subject_= make_header(decode_header(email_message['Subject']))
                break
            except TypeError:
                subject_= make_header(decode_header(str(email_message['Subject'])))
                break
        
        res, body_ = get_body(email_message)

        df = pd.DataFrame({"index": n, "date": str(date_), "subject": str(subject_), "sender": str(from_), "body": body_}, index=[n])
        #df = pd.DataFrame({"index": n, "date": str(date_), "subject": str(subject_), "sender": str(from_)}, index=[n])
        df_mail_list = pd.concat([df_mail_list, df])
        emailRsult = df_mail_list.to_dict('records')
    #delete email
    for i in emailList:
        obj.store(all_email[i], '+FLAGS', '\\Deleted')
        pass

    res, deleted = obj.expunge()

    obj.close()
    obj.logout()
    
    return res, len(deleted), emailRsult