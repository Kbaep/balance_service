from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from config import engine
from services import check_value_positive

app = Flask(__name__)
client = app.test_client()
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

from models import *


Base.metadata.create_all(bind=engine)

@app.route('/balance/<string:user_id>', methods=['GET'])
def current_balance(user_id: str):

    ''' Проверка баланса пользователя
    Ожидается GET запрос, в котором вместо поля user_id ожидается наименование пользователя
    '''

    instance = session.query(Balance).filter_by(user_id=user_id).one_or_none()
    if instance:
        return jsonify({
            'id': instance.id,
            'user_id': instance.user_id,
            'balance': instance.balance,
        }), 200
    else:
        return jsonify({'message': 'Пользователь ' + user_id + ' не существует'}), 400


@app.route('/balance/<string:user_id>', methods=['POST'])
def update_balance(user_id: str):

    ''' Изменения баланса пользователя'''


    try:
        params: dict = request.json
        instance = session.query(Balance).filter_by(user_id=user_id).one_or_none()
        if not instance and params['method'] == 'add' and check_value_positive(params['number']):
            instance = Balance(user_id=user_id, balance=params['number'])
            session.add(instance)
            session.commit()
            return jsonify({}), 201
        elif instance and params['method'] == 'add' and check_value_positive(params['number']):
            instance.balance += params['number']
            session.commit()
            return jsonify({}), 200
        elif instance and params['method'] == 'remove' and instance.balance >= params[
            'number'] and check_value_positive(params['number']):
            instance.balance -= params['number']
            session.commit()
            return jsonify({}), 200
        elif instance and params['method'] == 'remove' and check_value_positive(params['number']):
            return jsonify({'message': 'Недостаточно средств'}), 400
        else:
            raise
    except:
        return jsonify({'message': 'Некорректный запрос'}), 400


@app.route('/transfer', methods=['POST'])
def transfer():

    ''' Передача средств пользователю'''


    try:
        params: dict = request.json
        user_from = session.query(Balance).filter_by(user_id=params['user_id_from']).one_or_none()
        user_to = session.query(Balance).filter_by(user_id=params['user_id_to']).one_or_none()
        if not user_from or not user_to:
            return jsonify({'message': 'Таких пользователей нет'}), 400
        elif user_from.balance < params['number']:
            return jsonify({'message': 'Недостаточно средств'}), 400
        elif not check_value_positive(params['number']):
            return jsonify({'message': 'Некорректное значение'}), 400
        else:
            user_from.balance -= params['number']
            user_to.balance += params['number']
            session.commit()
            return jsonify({}), 200
    except:
        return jsonify({'message': 'Некорректный запрос'}), 400




@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True)
