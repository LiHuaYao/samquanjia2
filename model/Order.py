from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Order(db.Model):
    __tablename__ = 'order'  # 如果不指定表名，会默认以这个类名的小写为表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(64), nullable=False)
    action_code = db.Column(db.INTEGER, nullable=True,default=0)
    action_msg = db.Column(db.String(64), nullable=True)
    action_type = db.Column(db.String(32), nullable=True)
    bank_type = db.Column(db.String(32), nullable=True,comment='MayBank')
    # user_name = db.Column(db.String(64), nullable=False)
    status = db.Column(db.SMALLINT,nullable=False,default=0,comment='0-未处理，1处理中，2-完成，3-失败，4-取消')

    @staticmethod
    def commit():
        db.session.commit();
        return
    @staticmethod
    def add(order):
        db.session.add(order);
        return