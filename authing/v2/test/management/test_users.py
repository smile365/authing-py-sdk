from ...management.types import ManagementClientOptions
from ...management.authing import ManagementClient
from ...common.utils import get_random_string
import unittest
import os
from dotenv import load_dotenv
load_dotenv()

management = ManagementClient(ManagementClientOptions(
    user_pool_id=os.getenv('AUTHING_USERPOOL_ID'),
    secret=os.getenv('AUTHING_USERPOOL_SECRET'),
    host=os.getenv('AUTHING_SERVER')
))


class TestUsers(unittest.TestCase):
    pass

    def test_list(self):
        data = management.users.list()
        totalCount = data['totalCount']
        users = data['list']
        self.assertTrue(totalCount)
        self.assertTrue(users)

    def test_create(self):
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )
        self.assertTrue(user)
        self.assertTrue(user['id'])

    def test_update(self):
        username = get_random_string(10)
        password = get_random_string(10)
        user = management.users.create(
            userInfo={
                'username': username,
                'password': password
            }
        )
        nickname = get_random_string(10)
        user = management.users.update(
            userId=user['id'],
            updates={
                'nickname': nickname
            }
        )
        self.assertTrue(nickname == user.get('nickname'))

    def test_detail(self):
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )
        newUser = management.users.detail(userId=user['id'])
        self.assertTrue(user['id'] == newUser['id'])
        self.assertTrue(user['username'] == newUser['username'])

    def test_batch(self):
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )
        users = management.users.batch(
            userIds=[user['id']]
        )
        self.assertTrue(len(users) == 1)

    def test_search(self):
        nickname = get_random_string(10)
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10),
                'nickname': nickname
            }
        )
        data = management.users.search(query=nickname)
        _list = data['list']
        userIds = list(map(lambda x: x['id'], _list))
        self.assertTrue(user['id'] in userIds)

    def test_delete(self):
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )
        data = management.users.delete(userId=user['id'])
        code = data['code']
        self.assertTrue(code == 200)

        newUser = management.users.detail(userId=user['id'])
        self.assertTrue(newUser == None)

    def test_delete_many(self):
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )
        data = management.users.delete_many(
            userIds=[user['id']]
        )
        code = data['code']
        self.assertTrue(code == 200)
        newUser = management.users.detail(userId=user['id'])
        self.assertTrue(newUser == None)

    def test_list_roles(self):
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )
        data = management.users.list_roles(
            userId=user['id']
        )
        totalCount = data['totalCount']
        self.assertTrue(totalCount == 0)

    def test_add_roles(self):
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )
        _, roles = management.roles.list()
        management.users.add_roles(
            userId=user['id'],
            roles=list(map(lambda x: x['code'], roles))
        )
        data = management.users.list_roles(
            userId=user['id']
        )
        totalCount = data['totalCount']
        _list = data['list']
        self.assertTrue(len(_list) == totalCount)

    def test_remove_roles(self):
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )
        _, roles = management.roles.list()
        management.users.add_roles(
            userId=user['id'],
            roles=list(map(lambda x: x['code'], roles))
        )
        management.users.remove_roles(
            userId=user['id'],
            roles=list(map(lambda x: x['code'], roles))
        )
        data = management.users.list_roles(
            userId=user['id']
        )
        totalCount = data['totalCount']
        _list = data['list']
        self.assertTrue(totalCount == 0)
        self.assertTrue(len(_list) == 0)

    def test_refresh_token(self):
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )
        data = management.users.refresh_token(
            userId=user['id']
        )
        token, iat, exp = data['token'], data['iat'], data['exp']
        self.assertTrue(token)
        self.assertTrue(iat)
        self.assertTrue(exp)

        status = management.check_login_status(
            token=token, fetchUserDetail=True)
        self.assertTrue(status)
        self.assertTrue(status['id'] == user['id'])

    def test_add_policies(self):
        policy = management.policies.create(
            code=get_random_string(10),
            statements=[
                {
                    'resource': 'book:123',
                    'actions': ['books:read'],
                    'effect': 'ALLOW'
                }
            ]
        )
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )

        management.users.add_policies(
            userId=user['id'],
            policies=[policy['code']]
        )

        data = management.users.list_policies(
            userId=user['id']
        )
        totalCount = data['totalCount']
        self.assertTrue(totalCount == 1)

    def test_remove_policies(self):
        policy = management.policies.create(
            code=get_random_string(10),
            statements=[
                {
                    'resource': 'book:123',
                    'actions': ['books:read'],
                    'effect': 'ALLOW'
                }
            ]
        )
        user = management.users.create(
            userInfo={
                'username': get_random_string(10),
                'password': get_random_string(10)
            }
        )

        management.users.add_policies(
            userId=user['id'],
            policies=[policy['code']]
        )
        management.users.remove_policies(
            userId=user['id'],
            policies=[policy['code']]
        )
        data = management.users.list_policies(
            userId=user['id']
        )
        totalCount = data['totalCount']
        _list = data['list']
        self.assertTrue(totalCount == 0)
