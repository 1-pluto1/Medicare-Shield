import mimetypes

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
import os
from flask import request
from flask import flash
import sys
import click
import pandas as pd
from flask_cors import CORS
import numpy as np
import torch

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__, static_folder='../dist/assets', template_folder='../dist')
# 跨域问题
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# sqlalchemy 的配置
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config["SECRET_KEY"] = "123456"
# 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它。
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# 查询时显示原始SQL语句
app.config["SQLALCHEMY_ECHO"] = True
# 初始化数据库
db = SQLAlchemy(app)


# 跨域请求
@app.after_request
def after(resp):
    '''
    被after_request钩子函数装饰过的视图函数
    ，会在请求得到响应后返回给用户前调用，也就是说，这个时候，
    请求已经被app.route装饰的函数响应过了，已经形成了response，这个时
    候我们可以对response进行一些列操作，我们在这个钩子函数中添加headers，所有的url跨域请求都会允许！！！
    '''
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp


# 数据库对象
class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Number_of_medical_visits_SUM = db.Column(db.Integer)
    Monthly_pooled_amount_MAX = db.Column(db.Float)
    ALL_SUM = db.Column(db.Float)
    Monthly_drug_amount_AVG = db.Column(db.Float)
    Available_account_reimbursement_amount_SUM = db.Column(db.Float)

    def __init__(self, Number_of_medical_visits_SUM, Monthly_pooled_amount_MAX, ALL_SUM, Monthly_drug_amount_AVG,
                 Available_account_reimbursement_amount_SUM):
        self.Number_of_medical_visits_SUM = Number_of_medical_visits_SUM
        self.Monthly_pooled_amount_MAX = Monthly_pooled_amount_MAX
        self.ALL_SUM = ALL_SUM
        self.Monthly_drug_amount_AVG = Monthly_drug_amount_AVG
        self.Available_account_reimbursement_amount_SUM = Available_account_reimbursement_amount_SUM


# 模型加载
clf = torch.load('./clf.pth')
xgb = torch.load('./xgb.pth')
mlp = torch.load('./mlp.pth')
meta_model = torch.load('./meta_model.pth')


@app.route('/')
def index():
    return render_template('index.html')


# 数据库命令
@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


# 上传文件并进行处理，实现主要功能
@app.route('/', methods=['GET', 'POST'])
def upload_data():
    if request.method == 'POST':
        # 检查是否提交了文件
        if 'file' not in request.files:
            return render_template('index.html', message='No file part')

        file = request.files['file']

        # 如果用户没有选择文件，浏览器可能会发送一个没有文件名的空文件
        if file.filename == '':
            return render_template('index.html', message='No selected file')

        # 如果文件类型不是 CSV
        if file.filename.split('.')[-1].lower() != 'csv':
            return render_template('index.html', message='File type not supported')

        # 读取上传的 CSV 文件
        data = pd.read_csv(file)
        data = data[['就诊次数_SUM', '月统筹金额_MAX', 'ALL_SUM', '月药品金额_AVG', '可用账户报销金额_SUM']]
        # db
        db.drop_all()  # 清除数据库里的所有数据
        db.create_all()  # 创建所有表
        for index, row in data.iterrows():
            new_user = User(row['就诊次数_SUM'],
                            row['月统筹金额_MAX'], row['ALL_SUM'],
                            row['月药品金额_AVG'],
                            row['可用账户报销金额_SUM'])
            db.session.add(new_user)  # 添加到数据库
        db.session.commit()  # 提交数据库
        flash('Item created.')  # 显示成功创建的提示

        # 模型预测
        test_prediction = np.zeros((data.shape[0], 3))
        # lightgbm
        y_pred_prob = clf.predict(data)
        y_pred = [1 if x > 0.5 else 0 for x in y_pred_prob]
        test_prediction[:, 0] = y_pred
        # xgb
        y_pred_prob = xgb.predict(data)
        test_prediction[:, 1] = y_pred_prob
        # mlp
        y_pred_prob = torch.argmax(mlp(torch.tensor(data.values, dtype=torch.float32)), dim=1)
        test_prediction[:, 2] = y_pred_prob
        # 使用元模型进行预测
        y_pred = meta_model.predict(test_prediction)
        y_pred = [1 if x > 0.5 else 0 for x in y_pred]

        # 转换为json格式
        rows = []
        for i in y_pred:
            if i == 1:
                # rows.append(User.query.get(i))
                user = User.query.get(i)
                user_data = {
                    'Number_of_medical_visits_SUM': user.Number_of_medical_visits_SUM,
                    'Monthly_pooled_amount_MAX': user.Monthly_pooled_amount_MAX,
                    'ALL_SUM': user.ALL_SUM,
                    'Monthly_drug_amount_AVG': user.Monthly_drug_amount_AVG,
                    'Available_account_reimbursement_amount_SUM': user.Available_account_reimbursement_amount_SUM
                }
                rows.append(user_data)
        df = pd.DataFrame(rows)
        json_data = df.to_json(orient='split', force_ascii=False)

        return json_data, 200
    # 如果是 GET 请求，直接返回上传表单页面
    return render_template('index.html')


if __name__ == "__main__":
    # 让app在本地运行，定义了host和port
    app.run(debug=True, host='172.21.192.28', port=5000)
