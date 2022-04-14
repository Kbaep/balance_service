from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_paginate import Pagination, get_page_parameter

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
    print(instance)
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
            instance_2 = Operations(user_id=user_id, type='Начисление', comment=params['comment'],
                                    amount=params['number'])
            session.add(instance)
            session.add(instance_2)
            session.commit()
            return jsonify({}), 201
        elif instance and params['method'] == 'add' and check_value_positive(params['number']):
            instance.balance += params['number']
            instance_2 = Operations(user_id=user_id, type='Начисление', comment=params['comment'],
                                    amount=params['number'])
            session.add(instance_2)
            session.commit()
            return jsonify({}), 200
        elif instance and params['method'] == 'remove' and instance.balance >= params[
            'number'] and check_value_positive(params['number']):
            instance.balance -= params['number']
            instance_2 = Operations(user_id=user_id, type='Списание', comment=params['comment'],
                                    amount=params['number'])
            session.add(instance_2)
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
            oper_from = Operations(user_id=params['user_id_from'],
                                   type='Списание переводом',
                                   comment=params['comment'],
                                   amount=params['number'])
            oper_to = Operations(user_id=params['user_id_to'],
                                 type='Начисление переводом',
                                 comment=params['comment'],
                                 amount=params['number'])
            session.add(oper_from)
            session.add(oper_to)
            session.commit()
            return jsonify({}), 200
    except:
        return jsonify({'message': 'Некорректный запрос'}), 400


@app.route('/transactions/<string:user_id>', methods=['GET'])
def transactions(user_id: str):
    '''Передача списка транзакций'''
    # try:
    # params: dict = request.json
    user_transaction = session.query(Operations).filter(Operations.user_id == user_id).all()
    # filter_transactions = []
    # for i in user_transaction:
    #     a = {}
    #     a["id"] = i.id
    #     a["user_id"] = i.user_id
    #     a["type"] = i.type
    #     a["comment"] = i.comment
    #     a["create_time"] = i.create_time
    #     a["amount"] = i.amount
    #     filter_transactions.append(a)
    filter_transactions={
        "results": [{"id": m.id, "user_id": m.user_id} for m in user_transaction],
        "pagination": {
            "count": magazines.total,
            "page": page,
            "per_page": per_page,
            "pages": magazines.pages,
        },
    }
    print(type(filter_transactions))
    return jsonify(filter_transactions), 200
    #
    #
    #
    # except:
    #     return jsonify({'message': 'Некорректный запрос'}), 400


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True)
