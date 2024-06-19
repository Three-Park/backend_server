# backend_API
**백엔드 API요청을 처리하는 코드입니다.**

    image generate, sentiment 분석, 음악추천기능의 경우 아래 주소 레포지토리의 GPU서버에서 동작합니다.(cuda필수)
    https://github.com/Three-Park/genimg_server


<div align=left>
 <img src="https://img.shields.io/badge/Amazon%20EC2-FF9900?style=for-the-badge&logo=Amazon%20EC2&logoColor=white"> 
 <br>
 <img src="https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge&logo=Amazon%20S3&logoColor=white">
 <img src="https://img.shields.io/badge/Amazon%20RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white">
 <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=MySQL&logoColor=white">
 <br>
 <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=Django&logoColor=white">
    <br>
  <img src="https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white">
 <img src="https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=Gunicorn&logoColor=white">
 <img src="https://img.shields.io/badge/Let's%20Encrypt-003A70?style=for-the-badge&logo=letsencrypt&logoColor=white">
</div>

![image](https://github.com/Three-Park/backend_server/assets/96293444/1374a8ec-e310-41f6-9457-67c71eb7aa6c)



---
## Local

로컬에서 runserver로 돌리려면 

    1. git clone this repository
    2. set environment (+ activate env)
    3. python manage.py runserver

### set environment
    chmod +x install_packages_be.sh
    ./install_packages_be.sh

### activate environment (if you use virtual env)
virtual environment : be_env

    to activate: source be_env/bin/activate
    to deactivate: deactivate
