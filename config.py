from sqlalchemy import create_engine


def get_session(env):

    print(type(env))
    production = 'production'
    print(id(env))
    print(id(production))
    print(type(production))
    print(tuple(env) == tuple(production))
    if env == 'production':
        engine = create_engine('sqlite:///db.sqlite')
        print(engine)
    else:
        engine = create_engine('sqlite:///test1.sqlite')
        print(engine)
    return engine
