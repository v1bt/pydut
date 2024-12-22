import pydut as dut
import json

# 엔트리 이야기 글쓰기
user = dut.signin('USERNAME', 'PASSWORD')
print(dut.write(user, 'CONTENT'))

# 실시간 변수 설정 및 값 조회
user = dut.signin('USERNAME', 'PASSWORD')
print(dut.set(user, 'PROJECT_ID', 'VARIABLE_ID', 'VALUE'))
print(dut.get(user, 'PROJECT_ID', 'VARIABLE_ID'))

# 로그인 결과 출력
user = dut.signin('USERNAME', 'PASSWORD')
print(f'로그인 결과\nSession: {user.session}\nCsrf_Token: {user.csrf_token}\nX_Token: {user.x_token}')

# 회원가입
user = json.loads(dut.signup())
username = user.get('username')
password = user.get('password')
print(f'계정 생성 결과\n아이디: {username}\n암호: {password}')
