import os
cmcl = os.getcwd()+"\\cmcl.exe"
def command(command):os.system(command)
command(cmcl)
command("cls")
循环 = "开启"

while 循环 == "开启":
    print("--------------------------------------------------------------------------------")
    print("1. 启动游戏")
    print("2. 列出版本")
    print("3. 选择版本")
    print("4. 显示帮助")
    print("5.安装版本")
    print("6. 退出")
    print("7.账号操作")
    print("8.更改启动器配置")
    print("9.模组搜索")
    print("10.整合包搜索")
    命令 = input("请输入命令：")
    if 命令 == "1":
        print("调用启动游戏")
        version = input("请输入版本号：")
        command(cmcl+" "+version)
    if 命令 == "2":
        print("调用列出版本")
        command(cmcl+" install --list")
    if 命令 == "3":
        print("调用选择版本")
        print("1.显示所有可安装版本")
        print("2.显示所有正式版")
        print("3.显示从2020年5月9日到2021年10月23日的快照版本")
        _print_ = input("请输入选择：")
        if _print_ == "1":
            print("显示所有可安装版本")
            command(cmcl+" install --show=all")
        if _print_ == "2":
            print("显示所有正式版")
            command(cmcl+" install --show=r")
        if _print_ == "3":
            print("显示从2020年5月9日到2021年10月23日的快照版本")
            command(cmcl+" install --show=s --time=2020-05-09/2021-10-23")
    if 命令 == "4":
        break
    if 命令 == "5":
        print("调用安装版本")
        version = input("请输入版本号：")
        command(cmcl+" install "+version)
    if 命令 == "6":
        循环 = "关闭"
        command("cls")
        exit(0)
    if 命令 == "7":
        print("调用账号操作")
        command(cmcl+" account "+"--list")
        print("1.删除账号")
        print("2.选择账号")
        print("3.登录离线账号")
        print("4.登录微软账户")
        print("5.外置登录(可能不完善)")
        print("6.统一通行证登录(未开发)")
        print("7.取消")
        print("8.登录mojang账号")
        _print_ = input("请输入选择：")
        if _print_ == "1":
            print("删除账号")
            account = input("请输入账号序号：")
            command(cmcl+" account "+"--delete="+account)
        if _print_ == "2":
            print("切换账号")
            account = input("请输入账号序号：")
            command(cmcl+" account "+"-s"+account)
        if _print_ == "3":
            print("登录离线账号")
            account = input("请输入账号名：")
            command(cmcl+" account "+"--login=offline --name="+account)
        if _print_ == "4":
            print("登录微软账户")
            print("等待中")
            command(cmcl+" account "+"--login=microsoft")
        if _print_ == "5":
            print("外置登录")
            account = input("请输入服务器地址：")
            command(cmcl+" account "+"--login=authlib --address="+account)
        if _print_ == "8":
            print("登录mojang账号")
            account = input("回车继续。")
            command("start https://vdse.bdstatic.com/192d9a98d782d9c74c96f09db9378d93.mp4")
            # 单行原始字符串，用\n替代换行，双引号包裹避免单引号冲突
            print(" ....................„-~~'''''''~~--„„_\n..............„-~''-,::::::::::::::::::: ''-„\n..........,~''::::::::',:::::::::::::::: ::::|',\n.....::::::,-~'''¯¯¯''''~~--~'''¯''',:|\n.........'|:::::|: : : : : : : : : : : ::: : |,'\n........|:::::|: : :-~~---: : : -----: |\n.......(¯''~-': : : :'¯°: ',: :|: :°-: :|\n.....'....''~-,|: : : : : : ~---': : : :,'\n...............|,: : : : : :-~~--: : ::/\n......,-''\\':\\: :'~„„_: : : : : _,-'\n__„-';;;;;\\:''-,: : : :'~---~''/|\n;;;;;/;;;;;;\\: :\\: : :____/: :',__\n;;;;;;;;;;;;;;',. .''-,:|:::::::|. . |;;;;''-„__\n;;;;;;,;;;;;;;;;\\. . .''|::::::::|. .,';;;;;;;;;;''-„\n;;;;;;;|;;;;;;;;;;;\\. . .\\:::::,'. ./|;;;;;;;;;;;;|\n;;;;;;;\;;;;;;;;;;;',: : :|¯¯|. . .|;;;;;;;;;,';;|\n;;;;;;;;;',;;;;;;;;;;;\\. . |:::|. . .'',;;;;;;;;|;;/\n;;;;;;;;;;\;;;;;;;;;;;\\. .|:::|. . . |;;;;;;;;|/\n;;;;;;;;;;;;,;;;;;;;;;;|. .\\:/. . . .|;;;;;;;;|")
    if 命令 == "8":
        print("调用更改启动器配置")
        command(cmcl+" config -v")
        _print_ = input("回车继续")
        command("cls")
    if 命令 == "9":
        print("调用模组搜索")
        command("start https://www.mcmod.cn/")
        _print_ = input("回车继续")
        command("cls")
    if 命令 == "10":
        print("调用整合包搜索")
        command("start https://www.mcmod.cn/modpack.html")
        _print_ = input("回车继续")
        command("cls")
    if 命令 != "1" and 命令 != "2" and 命令 != "3" and 命令 != "4" and 命令 != "5" and 命令 != "6" and 命令 != "7" and 命令 != "8" and 命令 != "9" and 命令 != "10":
        print("无效命令")
        command("cls")
    