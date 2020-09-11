# school-toolbox
**some scripts, which make me easy to get school service.**

### Campus Network Tool

- origin :  学校周一到周五每天晚上11点半都会断电，隔天起来还得先给路由器弄个上网认证才能用，太麻烦了。所以便有了这个工具，将它部署在树莓派上，树莓派连接路由器WiFi，这样每天早上就免去手动认证的麻烦了。宿舍如果有多余的网线接口，也可以直接接到树莓派上，通过这个脚本自动认证。`注：并非一定要用树莓派，路由器、PC都可以只要能运行Python3`
- usage : `python3 conn.py -i 学号 -p 密码 -s 网络服务商(默认是联通)`
- detail : `python3 conn.py -h` 查看使用帮助
- 如果刚好这么巧，你的校园网登录界面和下面的长得一模一样，后台IP地址是`10.100.1.5`的话可以试试看。

![campusnetwork](CampusNetwork/imgs/campusnetwork.png)