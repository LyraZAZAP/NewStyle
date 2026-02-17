from db import DB
print('create:', DB.create_user('tmp_user3','Tmp3','secret123',None))
print('auth:', DB.authenticate('tmp_user3','secret123'))
