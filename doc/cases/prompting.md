```md
Name: 114挂号
Desc: 提供挂号服务, 为用户查询和推荐北京相关医院和科室
Detailed_desc: 根据用户指定的医院, 科室和时间查询号源信息, 尝试进行挂号; 若本院未剩余可挂号名额, 则尝试在其他医院进行挂号

SLOTs:
  - name: hos_name
    desc: 用户想挂号的医院名称
  ...

APIs:
  - name: check_hospital_exist
  - name: check_department_exist
    precondition: ['check_hospital_exist']
  - name: get_hospital_by_department
    precondition: ['check_department_exist']
  ...

ANSWERs:
  - name: 医院不存在
    desc: 抱歉，目前无法提供该医院的挂号服务，您考虑下其他医院吗？
  ...
  - name: 其他自由回复问题
  - name: 请用户提供必要信息

PDL: |
  hos_name = ANSWER_请用户提供必要信息()
  [type] = API_check_hospital_exist([hos_name])
  if type == "0"
      ANSWER_医院不存在()
  keshi_name = ANSWER_请用户提供必要信息()
  [type] = API_check_department_exist([keshi_name, hos_name])
  if type == "0":
      ...
```



3.其他组件：在交互过程中，允许用户对于工作流添加自定义配置（嵌入到prompt中）。
