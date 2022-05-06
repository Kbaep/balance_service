from sqlalchemy import create_engine


def get_session(env):
    print(env)
    if env.lower() == 'production':
        engine = create_engine('sqlite:///db.sqlite')
        print(engine)
    else:
        engine = create_engine('sqlite:///test.sqlite')
        print(engine)
    return engine