from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from config import get_session
from services import check_value_positive, currency_value_balance

app = Flask(__name__)
engine = get_session(app.config['ENV'])
client = app.test_client()
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

from models import *

Base.metadata.create_all(bind=engine)


@app.route('/balance/', methods=['GET'])
def current_balance():
    ''' Проверка баланса пользователя
    Ожидается GET запрос
    '''
    try:
        currency = request.args.get('currency', default=None, type=None)
        user_id = request.args.get('user_id', default=None, type=None)
        if user_id is None:
            return jsonify({'message': 'Не указан пользователь'}), 400
        else:
            instance = session.query(Balance).filter_by(user_id=user_id).one_or_none()
            if instance and currency is None:
                return jsonify({
                    'id': instance.id,
                    'user_id': instance.user_id,
                    'balance': instance.balance,
                }), 200
            elif instance and currency is not None:
                currency_balance = currency_value_balance(instance.balance, currency)
                if type(currency_balance) == int or type(currency_balance) == float:
                    return jsonify({
                        'id': instance.id,
                        'user_id': instance.user_id,
                        'balance': round(currency_balance, 2),
                        'currency': currency
                    }), 200
                else:
                    raise
            else:
                return jsonify({'message': 'Пользователь ' + user_id + ' не существует'}), 400
    except:
        return jsonify({'message': 'Некорректный запрос'}), 400


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


@app.route('/transactions/', methods=['GET'])
def history_transactions():
    try:
        user_id = request.args.get('user_id', default=None, type=None)
        sort = request.args.get('sort', default=None, type=None)
        reverse = request.args.get('reverse', default=None, type=None)
        instance = session.query(Balance).filter_by(user_id=user_id).one_or_none()
        if instance is None:
            return jsonify({'message': 'Пользователь ' + user_id + ' не существует'}), 400
        user_transaction = session.query(Operations).filter(Operations.user_id == user_id)
        filter_transactions = []
        for i in user_transaction:
            a = {}
            a["id"] = i.id
            a["user_id"] = i.user_id
            a["type"] = i.type
            a["comment"] = i.comment
            a["create_time"] = i.create_time
            a["amount"] = i.amount
            filter_transactions.append(a)
        if sort == 'amount' and reverse is None:
            return jsonify(sorted(filter_transactions, key=lambda d: d['amount'], reverse=False)), 200
        elif sort == 'amount' and reverse.lower() == 'true':
            return jsonify(sorted(filter_transactions, key=lambda d: d['amount'], reverse=True)), 200
        elif sort == 'create_time' and reverse == None:
            return jsonify(sorted(filter_transactions, key=lambda d: d['create_time'], reverse=False)), 200
        elif sort == 'create_time' and reverse.lower() == 'true':
            return jsonify(sorted(filter_transactions, key=lambda d: d['create_time'], reverse=True)), 200
        elif sort is None:
            return jsonify(sorted(filter_transactions, key=lambda d: d['create_time'], reverse=True)), 200
        else:
            raise
    except:
        return jsonify({'message': 'Некорректный запрос'}), 400


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True)
