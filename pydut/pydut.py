import requests
from bs4 import BeautifulSoup
from TempMail import TempMail

import json
import websocket
import random
import string
import re
import time

from .graphql import queries

class signin_session:
    def __init__(self, session, x_token, csrf_token, user_id):
        self.session = session
        self.x_token = x_token
        self.csrf_token = csrf_token
        self.user_id = user_id

def version():
    return '2025-01-27'

def signin(username, password):
    session = requests.Session()
    page = session.get('https://playentry.org/signin')
    soup = BeautifulSoup(page.text, 'html.parser')
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

    headers = {
        'CSRF-Token': csrf_token,
        'Content-Type': 'application/json'
    }

    query = queries.signin()

    variables = {
        'username': username,
        'password': password,
        'rememberme': False
    }

    response = session.post('https://playentry.org/graphql',
                            headers=headers,
                            json={'query': query, 'variables': variables})
    data = response.json()
    user_id = data.get('data', {}).get('signinByUsername', {}).get('id')

    if 'errors' in data:
        return None

    page = session.get('https://playentry.org')
    soup = BeautifulSoup(page.text, 'html.parser')
    next_data = json.loads(soup.select_one('#__NEXT_DATA__').get_text())
    x_token = next_data['props']['initialState']['common']['user']['xToken']

    return signin_session(session, x_token, csrf_token, user_id)

def ws_query(signin_session, project_id):
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'csrf-token': signin_session.csrf_token,
        'x-token': signin_session.x_token
    }

    query = queries.cloud_server_info()

    variables = {'id': project_id}
    response = signin_session.session.post('https://playentry.org/graphql',
                            headers=headers,
                            json={'query': query, 'variables': variables})

    cloud_server_info = response.json()['data']['cloudServerInfo']
    query_token = cloud_server_info['query']

    return f'wss://playentry.org/cv/?type=undefined&q={query_token}&EIO=3&transport=websocket'

def write(signin_session, content, text=None, image=None, sticker=None, stickerItem=None, cursor=None):
    if not signin_session:
        return {"status": "failed", "message": "로그인 실패: 아이디나 비밀번호를 확인하세요.", "status_code": 401}

    headers = {
        'X-Token': signin_session.x_token,
        'x-client-type': 'Client',
        'CSRF-Token': signin_session.csrf_token,
        'Content-Type': 'application/json'
    }

    query = queries.create_entry_story()

    variables = {
        key: value for key, value in {
            'content': content,
            'text': text,
            'image': image,
            'sticker': sticker,
            'stickerItem': stickerItem,
            'cursor': cursor
        }.items() if value is not None
    }

    response = signin_session.session.post('https://playentry.org/graphql',
                            headers=headers,
                            json={'query': query, 'variables': variables})

    if response.status_code == 200:
        response_data = response.json()
        errors = response_data.get("errors", [])
        if errors:
            status_code = errors[0].get("statusCode")
            
            error_messages = {
                400: '타인에게 불쾌감을 주는 욕설, 비하 등의 부적절한 단어는 작성할 수 없습니다.',
                406: '제한된 URL이 포함되어 작성할 수 없습니다.',
                429: '도배 방지를 위해 댓글 작성이 제한되었습니다.',
                401: '이메일을 인증해 주세요.',
                2000: '첫 작품을 공유한 후 24시간이 지나야 글을 쓸 수 있습니다.',
                2001: '첫 작품을 공유한 지 24시간이 지나지 않았습니다.',
                2002: '첫 작품을 공유한 다음 날부터 7일 동안은 하루에 한 개씩만 글을 쓸 수 있습니다.',
                2003: '동일한 내용은 반복해서 업로드할 수 없습니다.'
            }

            message = error_messages.get(status_code, '알 수 없는 오류가 발생했습니다.')
            result = {'status': 'failed', 'message': message, 'status_code': status_code}
        else:
            result = {'status': 'success', 'message': '글이 성공적으로 작성되었습니다.', 'status_code': 200}
    else:
        result = {'status': 'failed', 'message': '글 작성에 실패했습니다.', 'status_code': response.status_code}

    return json.dumps(result, ensure_ascii=False)

def set(signin_session, project_id, v_id, value):
    if not signin_session or not project_id or not v_id or not value:
        return json.dumps({'error': '필수 정보가 누락되었습니다.'}, ensure_ascii=False), 400

    ws_url = ws_query(signin_session, project_id)

    ws = websocket.create_connection(ws_url)

    ws.send(f'420["action",{{"_id":"{project_id}","id":"{v_id}","variableType":"variable","type":"set","value":"{value}"}}]')
    ws.close()

    return json.dumps({'message': f'{project_id}의 {v_id}가 {value} 로 변경되었습니다.'}, ensure_ascii=False)


def get(signin_session, project_id, v_id):
    if not signin_session or not project_id or not v_id:
        return json.dumps({'error': '필수 정보가 누락되었습니다.'}, ensure_ascii=False), 400

    ws_url = ws_query(signin_session, project_id)

    ws = websocket.create_connection(ws_url)

    value = None
    while True:
        message = ws.recv()
        if message.startswith('42'):
            try:
                data = json.loads(message[2:])[1]
                variables = data.get('variables', [])
                for variable in variables:
                    if variable['id'] == v_id:
                        value = variable['value']
                        break
            except Exception as e:
                value = '값 가져오기 실패'
            break

    ws.close()

    if value is not None:
        return json.dumps({'value': value}, ensure_ascii=False)
    else:
        return json.dumps({'error': '변수를 찾을 수 없습니다.'}, ensure_ascii=False), 404

def random_string(length=8):
    letters = ''.join(random.choices(string.ascii_letters, k=length-2))
    digits = ''.join(random.choices(string.digits, k=2))
    combined = list(letters + digits)
    random.shuffle(combined)
    return ''.join(combined)

def check_username_exists(username, session, csrf_token):
    query = """
    query CHECK_EXISTS_USERNAME($username: String) {
        existsUser(username: $username) {
            exists
        }
    }
    """
    variables = {
        "username": username
    }
    
    response = session.post('https://playentry.org/graphql/', headers={
        "Content-Type": "application/json",
        "csrf-token": csrf_token,
    }, json={
        "query": query,
        "variables": variables
    })
    
    if response.status_code == 200:
        return response.json().get('data', {}).get('existsUser', {}).get('exists', False)
    return False

def check_prohibited_word(word, session, csrf_token):
    query = """
    query CHECK_PROHIBITED_WORD($type: String, $word: String) {
        prohibitedWord(type: $type, word: $word) {
            status
            result
        }
    }
    """
    variables = {
        "type": "user",
        "word": word
    }
    
    response = session.post('https://playentry.org/graphql/', headers={
        "Content-Type": "application/json",
        "csrf-token": csrf_token,
    }, json={
        "query": query,
        "variables": variables
    })
    
    if response.status_code == 200:
        return response.json().get('data', {}).get('prohibitedWord', {}).get('result', False)
    return False


def check_email_exists(email, session, csrf_token):
    query = """
    query CHECK_EXISTS_EMAIL($email: String) {
        existsUser(email: $email) {
            exists
        }
    }
    """
    variables = {
        "email": email
    }
    
    response = session.post('https://playentry.org/graphql/', headers={
        "Content-Type": "application/json",
        "csrf-token": csrf_token,
    }, json={
        "query": query,
        "variables": variables
    })
    
    if response.status_code == 200:
        return response.json().get('data', {}).get('existsUser', {}).get('exists', False)
    return False

def signup(username=None, password=None, email=None):
    userid = username if username else random_string(8)
    passwd = password if password else random_string(15)
    nickname = userid

    tmp = TempMail()

    if not email:
        inb = tmp.createInbox()
        email = inb.address

    session = requests.Session()
    page = session.get('https://playentry.org/signin')
    soup = BeautifulSoup(page.text, 'html.parser')
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

    get = session.post('https://playentry.org/graphql/', json={
        "query":"query SELECT_WHITELIST_TARGET($target: ID) {whiteListTarget(target: $target) {id}}","variables":{"target":"53eef21dce8dd2c54f0cb721"}
    })
    ecui = get.cookies.get('_ecui')

    sturl = session.get('https://playentry.org/signup/1')
    sturl = sturl.text.split('buildId')[1][3:-1].split('"')[0]

    st = session.get(f'https://playentry.org/_next/data/{sturl}/ko/signup/3.json?id=3')
    st = st.text.split('signupToken":"')[1].split('"')[0]

    requests.get('https://playentry.org/signup/1',cookies={"_ecui": ecui})
    requests.get('https://playentry.org/signup/2',cookies={"_ecui": ecui})
    requests.get('https://playentry.org/signup/3',cookies={"_ecui": ecui})

    if username:
        if not (4 <= len(username) <= 20):
            return json.dumps({'status': 'failed', 'message': '아이디는 4자 이상 20자 이하이어야 합니다.'}, ensure_ascii=False)
        
        if check_prohibited_word(username, session, csrf_token):
            return json.dumps({'status': 'failed', 'message': '아이디에 금지된 단어가 포함되어 있습니다.'}, ensure_ascii=False)

        exists = check_username_exists(username, session, csrf_token)
        if exists:
            return json.dumps({'status': 'failed', 'message': '이미 존재하는 아이디입니다.'}, ensure_ascii=False)

    if password:
        if len(password) < 5:
            return json.dumps({'status': 'failed', 'message': '비밀번호는 5자 이상의 길이여야 합니다.'}, ensure_ascii=False)
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            return json.dumps({'status': 'failed', 'message': '비밀번호는 영문과 숫자가 모두 포함되어야 합니다.'}, ensure_ascii=False)

    if email and check_email_exists(email, session, csrf_token):
        return json.dumps({'status': 'failed', 'message': '이미 존재하는 이메일입니다.'}, ensure_ascii=False)

    signup = session.post('https://playentry.org/graphql/', headers={
        "Content-Type": "application/json",
        "csrf-token": csrf_token,
    }, json={
        'query': ' mutation SIGNUP_BY_USERNAME( $role: String!, $grade: String, $gender: String!, $nickname: String!, $email: String, $username: String!, $password: String!, $passwordConfirm: String!, $mobileKey: String, $signupToken: String, $bornYear: String, $parentName: String, $parentMobileKey: String ) { signupByUsername( role: $role, grade: $grade , gender: $gender , nickname: $nickname , email: $email , username: $username , password: $password, passwordConfirm: $passwordConfirm, mobileKey: $mobileKey, signupToken: $signupToken, bornYear: $bornYear, parentName: $parentName, parentMobileKey: $parentMobileKey ) { id username nickname role isEmailAuth isSnsAuth isPhoneAuth studentTerm status { userStatus } profileImage { id name label { ko en ja vn } filename imageType dimension { width height } trimmed { filename width height } } banned { username nickname reason bannedCount bannedType projectId startDate userReflect { status endDate } } isProfileBlocked created } }',
        "variables": {
            "username": userid,
            "passwordConfirm": passwd,
            "password": passwd,
            "role": "member",
            "grade": None,
            "gender": "male",
            "bornYear": "2000",
            "nickname": nickname,
            "email": email,
            "mobileKey": None,
            "signupToken": st
        }
    })

    session.close()

    result = {
        'status': 'failed',
        'message': None
    }

    if signup.status_code == 200:
        response_data = signup.json()
        if "errors" in response_data:
            result['message'] = f"오류발생: {response_data['errors'][0]['statusCode']}"
            result['response'] = response_data
        else:
            emails = None
            while not emails:
                emails = tmp.getEmails(inb)
                if not emails:
                    time.sleep(1)

            if emails:
                emailhtml = emails[0].html
                if not emailhtml:
                    result['message'] = "이메일 본문이 비어 있습니다."
                else:
                    soup = BeautifulSoup(emailhtml, 'html.parser')
                    authurl = soup.find('a', href=re.compile(r'https://playentry\.org/api/email/.*'))
                    if authurl:
                        authurl = authurl['href']
                        headers = {
                            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                            "accept-language": "ko,en;q=0.9,ko-KR;q=0.8"
                        }
                        res = session.get(authurl, headers=headers, allow_redirects=False)

                        if res.status_code == 302:
                            rd_url = res.headers['Location']
                            final = session.get(f'https://playentry.org{rd_url}', headers=headers)
                            result['status'] = 'success'
                            result['message'] = '계정이 성공적으로 생성되었습니다.'
                            result['username'] = userid
                            result['password'] = passwd
                            result['email'] = email
                        else:
                            result['message'] = "URL을 찾을 수 없습니다."
                    else:
                        result['message'] = "이메일 내에서 인증 URL을 찾을 수 없습니다."
            else:
                result['message'] = "이메일을 찾을 수 없습니다."
    else:
        result['message'] = f"오류발생: {signup.status_code}"

    rjson = json.dumps(result, ensure_ascii=False)

    return rjson
