import config
import pytest
import bcrypt
import json


from sqlalchemy import create_engine,text
from app import create_app

database = create_engine(config.test_config['DB_URL'],convert_unicode=True)

@pytest.fixture
def api():
    app =create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()

    return api


def setup_function():
    ## Create user
    hashed_password = bcrypt.hashpw(
        b'test password',
        bcrypt.gensalt()
    )

    new_users = [
        {
            'id': 1,
            'name': '송은우',
            'email': 'songew@gmail.com',
            'profile': 'test test',
            'hashed_password':hashed_password
        },
        {
            'id': 2,
            'name': '송하윤',
            'email': 'tet@gmail.com',
            'profile': 'test test profile 2',
            'hashed_password': hashed_password
        }
    ]

    database.execute(text("""
        INSERT INTO users(
            id,
            name,
            email,
            profile,
            hashed_password
        ) VALUES (
            :id,
            :name,
            :email,
            :profile,
            :hashed_password
        )
    """), new_users)

    ## user2 트윗 미리 생성
    database.execute(text("""
        INSERT INTO tweets(
            user_id,
            tweet
        ) VALUES (
            2,
            "i am id 2"
        )
    """))

def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))


def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data

def test_login(api):
    resp = api.post(
        '/login',
        data = json.dumps({
            'email' : 'songew@gmail.com',
            'password' : 'test password'
        }),
        content_type = 'application/json'
    )

    assert b'access_token' in resp.data


def test_unauthorized(api):
    # access_token 없이 401응답을 리턴하는가??
    resp = api.post(
        '/tweet',
        data = json.dumps({
            'tweet':"hello world"
        }),
        content_type= 'application/json'
    )
    assert resp.status_code == 401

    resp = api.post(
        '/follow',
        data = json.dumps({
            'follow':2
        }),
        content_type= 'application/json'
    )

    assert resp.status_code==401

    resp = api.post(
        '/unfollow',
        data = json.dumps({
            'unfollow':2
        }),
        content_type= 'application/json'
    )

    assert resp.status_code==401

def test_tweet(api):
    ## login
    resp = api.post(
        '/login',
        data=json.dumps({
            'email':'songew@gmail.com',
            'password':'test password'
        }),
        content_type='application/json'
    )

    resp_json = json.loads(resp.data.decode('UTF-8'))
    access_token = resp_json['access_token']

    ## tweet
    resp = api.post(
        '/tweet',
        data=json.dumps({
            'tweet':"Hi world"
        }),
        content_type='application/json',
        headers={'Authorization':access_token}
    )

    assert resp.status_code==200

    ## tweet 확인하기

    resp = api.get(
        f'/timeline/1'
    )
    tweets = json.loads(resp.data.decode('UTF-8'))
    assert resp.status_code==200
    assert tweets == {
        'user_id':1,
        'timeline' : [
            {
                'user_id':1,
                'tweet':'Hi world'
            }
        ]
    }

def test_follow(api):
    ## login
    resp = api.post(
        '/login',
        data=json.dumps({
            'email':'songew@gmail.com',
            'password':'test password'
        }),
        content_type='application/json'
    )

    resp_json = json.loads(resp.data.decode('UTF-8'))
    access_token = resp_json['access_token']

    ## 먼저 사용자1의 트위트를 확인해서 비어있는지 확인하기
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('UTF-8'))
    assert resp.status_code==200
    assert tweets == {
        'user_id':1,
        'timeline': []
    }

    #follow 사용자 아이디=2

    resp = api.post(
        '/follow',
        data=json.dumps({'follow':2}),
        content_type='application/json',
        headers={'Authorization':access_token}
    )

    assert resp.status_code==200

    # 사용자1의 tweet 타임라인에 2번의 트윗이 있는가??

    resp = api.get(f'timeline/1')
    tweets = json.loads(resp.data.decode('UTF-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id':1,
        'timeline':[
            {
                'user_id':2,
                'tweet' :"i am id 2"
            }
        ]
    }

def test_unfollow(api):
    ## login
    resp = api.post(
        '/login',
        data=json.dumps({
            'email': 'songew@gmail.com',
            'password': 'test password'
        }),
        content_type='application/json'
    )

    resp_json = json.loads(resp.data.decode('UTF-8'))
    access_token = resp_json['access_token']

    # follow 사용자 아이디=2
    resp = api.post(
        '/follow',
        data=json.dumps({'follow':2}),
        content_type='application/json',
        headers={'Authorization':access_token}
    )
    assert resp.status_code==200

    ## 이제 사용자 1의 tweet을 확인해서 사용자2의 트윗이 있는가?
    resp = api.get(f'timeline/1')
    tweets = json.loads(resp.data.decode('UTF-8'))

    assert resp.status_code==200
    assert tweets == {
        'user_id':1,
        'timeline':[
            {
                'user_id':2,
                'tweet':'i am id 2'
            }
        ]
    }

    # unfollow 사용자 아이디2

    resp = api.post(
        '/unfollow',
        data=json.dumps({'unfollow':2}),
        content_type='application/json',
        headers={'Authorization':access_token}
    )

    assert resp.status_code==200

    resp = api.get(f'timeline/1')
    tweets = json.loads(resp.data.decode('UTF-8'))

    assert resp.status_code==200
    assert tweets=={
        'user_id':1,
        'timeline':[]
    }

    