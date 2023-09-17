FROM ubuntu:18.04 as builder
WORKDIR /app
COPY . .
# 在当前目录安装依赖
RUN pip install -r requirements -t .

FROM pack
WORKDIR /app2
COPY --from=builder /app /app2
EXPOSE 9000
VOLUME [ "/app2" ]
CMD ["python","/app2/main.py"] 

