from flask import Flask,render_template,request,jsonify,session
from flask_sqlalchemy import SQLAlchemy
from aip import AipFace
import datetime
import base64
import os
import time
from PIL import Image
import re

app = Flask(__name__)
"""数据库的链接"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@localhost:3306/face_recognition?charset=utf8mb4'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 打开自动提交
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SDFGHJ'
db = SQLAlchemy(app)  # 创建数据库连接对象

class Login(db.Model):
    __tablename__ = 'login'
    user = db.Column('user',db.String(16),primary_key=True)
    password = db.Column('password',db.String(16),nullable=False)
    nickname = db.Column('nickname',db.String(30),nullable=False)

    def __init__(self,user,password,nickname):
        self.user = user
        self.password = password
        self.nickname = nickname

class EmployDdetails(db.Model):
    __tablename__ = "face_feature_usage_details"
    id = db.Column('id',db.Integer,primary_key=True,autoincrement=True)
    user = db.Column('user',db.String(16),nullable=False)
    photo_name = db.Column('photo_name', db.String(50), nullable=False)
    photo_path = db.Column('photo_path', db.String(50), nullable=False)
    source = db.Column('source', db.String(20), nullable=False)
    datetime = db.Column('datetime', db.String(30), nullable=False)

    def __init__(self,user,photo_name,photo_path,source,datetime):

        self.user = user
        self.photo_name = photo_name
        self.photo_path = photo_path
        self.source = source
        self.datetime = datetime

""" 你的 APPID AK SK """
APP_ID = '15991435'
API_KEY = 'tR5941sN1ZwgPGL0QTZuM4KK'
SECRET_KEY = 'YClpTSrH7NLcqoVP0OGSe6f76Ri5UNO8'
#实例化连接对象
client = AipFace(APP_ID, API_KEY, SECRET_KEY)



@app.route('/iphone2')
def ipthone_html():
    userinfo = {'nickname': session['nickname'],'user':session['user']}


    print('nickname',userinfo['nickname'])
    return render_template('iphone2.html',**userinfo)

"""
对照片进行BASE64编码
imageType为base64的类型
"""
def make_base64(image_name):
    image_path = "./static/image/"+image_name
    with open(image_path,'rb') as f:
        # b64encode是编码
        base64_data = base64.b64encode(f.read())
    image = str(base64_data,'utf-8')
    print('11111111111111111')
    return image

"""
imageType为URL类型
"""
def make_url():
    image = "http://youboyu.cn/wp-content/uploads/2018/08/eee.jpg"
    return image

"""
登陆
"""
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        register_user = request.form['user']
        register_pwd = request.form['password']
        register_nickname = request.form['nickname']
        print('11111111111111111111111')
        user_name=Login.query.filter(Login.user == register_user).first()
        print('user,',user_name)
        if user_name:
            message={
                'success':False
            }
        else:
            message={
                'success':True
            }
            register_object = Login(register_user,register_pwd,register_nickname)
            db.session.add(register_object)
            db.session.commit()
        return jsonify(message)
    else:
        return render_template('register.html')

"""
登陆验证
"""
@app.route('/loginfo',methods=['POST'])
def loginfo():
        if request.method == 'POST':
            message=login_core_code(request.form['user'],request.form['password'])
            return jsonify(message)

'''
登录核心代码
'''
def login_core_code(user,pwd):
    login_er = Login.query.filter(Login.user == user,
                                  Login.password ==pwd).first()
    print('login:', login_er)
    if login_er:
        userinfo = db.session.query(Login.nickname, Login.user).filter(Login.user == user).first()
        session['nickname'] = userinfo[0]
        session['user'] = userinfo[1]
        message = {
            'success': True,
            'nickname':session['nickname'],

        }
    else:
        message = {
            'success': False
        }
    return message

"""
人脸搜索,用来登录
"""
@app.route('/login_face',methods=['POST'])
def face_search():
    if request.method == 'POST':
        print(111111111111111111)
        img = request.files['file']
        path=save_img_from_html(img)
        flag = compess_photo(img.filename)
        if flag:
            imageType = "BASE64"
            if imageType == "BASE64":
                '''base64方法'''
                image = make_base64(image_name=img.filename)
            else:
                '''url方法'''
                image = make_url()
                imageType = "URL"

            groupIdList = 'login_face_recognition'
            result = client.search(image, imageType, groupIdList)
            print(result)
            print('sdasdsa')
            user, pwd =user_pwd_spilt(result['result']['user_list'][0]['user_id'])
            message=login_core_code(user, pwd)

            face_feature_usage_details(session['user'],img.filename,path,'人脸搜索')
            return jsonify(message)
        else:
            return jsonify({'result': flag})


"""
人脸识别注册补录
"""
@app.route('/face_collection',methods=['POST'])
def face_collection():
    if request.method == 'POST':
        img = request.files['file']
        path=save_img_from_html(img)
        flag = compess_photo(img.filename)
        if flag:
            imageType = "BASE64"
            if imageType == "BASE64":
                '''base64方法'''
                image = make_base64(image_name=img.filename)
            else:
                '''url方法'''
                image = make_url()
                imageType = "URL"
            groupId = 'login_face_recognition'
            #**执行更新操作，如果该uid不存在时，会返回错误。如果添加了action_type:replace,则不会报错，并自动注册该uid，操作结果等同注册新用户。
            pwd = db.session.query(Login.password).filter(Login.user == session['user']).first()[0]
            userId = session['user']+'_'+pwd
            options={}
            result=client.addUser(image,imageType,groupId,userId)
            print('result',result)
            print(type(result['error_code']))
            if result['error_code'] == 0:
                message = {
                    'success':True
                }
                face_feature_usage_details(session['user'], img.filename, path, '人脸注册')
            else:
                message = {
                    'success': False,
                    'error_msg':result['error_msg']
                }
            return jsonify(message)



"""
检测照片的特性
"""
@app.route('/detection',methods=['POST'])
def face_detection():
    if request.method == 'POST':
        img = request.files['file']
        path=save_img_from_html(img)
        flag = compess_photo(img.filename)
        if flag:
            imageType = "BASE64"
            if imageType == "BASE64":
                '''base64方法'''
                image = make_base64(image_name=img.filename)
            else:
                '''url方法'''
                image = make_url()
                imageType = "URL"
            """ 如果有可选参数 """
            options = {}
            options["face_field"] = "race,age,expression,faceshape,glasses,beauty,gender"
            options["max_face_num"] = 1 #控制人脸识别的最大数目
            options["face_type"] = "LIVE"
            """ 带参数调用人脸检测 检测人脸的一些属相 """
            result=client.detect(image, imageType, options)
            print('收到的结果：',result)
            print('----------------------------------------')
            dict1=analyze_result_face_detection(result)
            print(dict1)
            face_feature_usage_details(session['user'], img.filename, path, '人脸检测')
            return jsonify({'result':dict1})
        else:
            return jsonify({'result': flag})
# #todo:正在写功能
@app.route('/face_show_usage_details',methods=['GET'])
def face_show_usage_details():
    if request.method == 'GET':

        face_search=EmployDdetails.query.filter(EmployDdetails.user == session['user'],
                                               EmployDdetails.source=='人脸搜索').count()
        face_register = EmployDdetails.query.filter(EmployDdetails.user == session['user'],
                                                  EmployDdetails.source == '人脸注册').count()
        face_detection = EmployDdetails.query.filter(EmployDdetails.user == session['user'],
                                                  EmployDdetails.source == '人脸检测').count()
        face_list1 = {'face_search':face_search,
                      'face_register':face_register,
                      'face_detection':face_detection}
        return jsonify(face_list1)




def user_pwd_spilt(str1):
    user,pwd=re.findall(r'(.+)[_](.+)',string=str1)[0]
    return user,pwd
# @app.route('/ceshi',methods=['POST'])
# def hhhhhh():
#     if request.method == 'POST':
#         img = request.files['file']
#         flag = compess_photo(file_name)
#     return jsonify({'result':flag})

"""
将前端接收的图片进行保存
"""
def save_img_from_html(img):
    file_name = img.filename
    path = os.path.join('./static/image/', file_name)
    img.save(path)
    return path


"""
图片压缩函数并保存
"""
def compess_photo(img_name):
    try:
        src_img = os.path.join('./static/image/',img_name)
        fcl_img = Image.open(src_img)
        fcl_img_wide, fcl_img_high = fcl_img.size
        if fcl_img_wide > 960:
            fcl_reimg = fcl_img.resize((int(fcl_img_wide / 2), int(fcl_img_high / 2)), Image.ANTIALIAS)
            fcl_reimg.save(src_img)
        flag = True
    except Exception:
        flag = False
    return flag



"""
人脸功能使用详情
user : 用户名
photo_name : 照片名
photo_path : 照片地址
source : 哪个人脸识别功能
datetime : 时间 
"""
def face_feature_usage_details(user,photo_name,photo_path,source):

    employ_details_object = EmployDdetails(user,photo_name,photo_path,source,get_time_now())
    db.session.add(employ_details_object)
    db.session.commit()



"""
获取当地的时间
"""
def get_time_now():
    time_now= datetime.datetime.now()
    # time_now = re.findall(r'(.+)[.]',str(datetime.datetime.now()))[0]
    return time_now



"""
对人脸检测结果进行分析
result_formal 形参
face_num:人脸数目
face_probability:人脸置信度，范围0-1
expression 表情：    &！&
faceshape{
            type：脸型 square/triangle/oval/heart/round
            probability: 置信度 0-1
            }                                   &！&
glasses  是否带眼镜，    &！&
race 人种 {
        type :yellow、white、black、arabs       
        }                                          &！&
age 年龄                                           &！&
"""
def analyze_result_face_detection(result_formal):
    result_list = result_formal['result']['face_list']
    face_num = int(result_formal['result']['face_num'])
    dict1={}
    for i in range(face_num):
        dict2={}
        dict2['face_probability']=result_list[i]['face_probability']
        dict2['expression'] = result_list[i]['expression']['type']
        dict2['face_shape'] = result_list[i]['face_shape']['type']
        dict2['glasses'] = result_list[i]['glasses']['type']
        dict2['race'] = result_list[i]['race']['type']
        dict2['age'] = result_list[i]['age']
        dict2['gender']=result_list[i]['gender']['type']
        dict2['beauty'] = result_list[i]['beauty']
        dict1['face_'+str(i+1)] = dict2
    return dict1

# """
# 以时间str作为图片名字
# """
# def make_img_name():
#     img_name=time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
#     return img_name



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
