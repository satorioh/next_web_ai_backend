import multiprocessing

# daemon = True  # 守护进程
bind = '0.0.0.0:2096'  # 绑定ip和端口号
backlog = 512  # 可服务的客户端数量
# chdir = '/home/test/server/bin' #gunicorn要切换到的目的工作目录
timeout = 30  # 超时
worker_class = 'uvicorn.workers.UvicornWorker'  # 使用gevent模式，还可以使用sync 模式，默认的是sync模式
# workers = multiprocessing.cpu_count() * 2 + 1  # 进程数
workers = 1  # 进程数
loglevel = 'info'  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
accesslog = "./log/gunicorn_access.log"  # 访问日志文件
errorlog = "./log/gunicorn_error.log"  # 错误日志文件
keyfile = "./cert/key.pem"
certfile = "./cert/cert.pem"
