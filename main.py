import dns.resolver
import tkinter,tkinter.ttk,tkinter.messagebox
import os
import sys
import requests
import threading
import concurrent.futures
import time
import wmi
import ctypes
import copy
import re
needReboot=False
if ctypes.windll.shell32.IsUserAnAdmin():
    pass
else:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()
wmiService = wmi.WMI()
colNetConfigs = wmiService.Win32_NetworkAdapterConfiguration(IPEnabled=True)
netConfigs={}
for i in colNetConfigs:
    netConfigs[i.Caption]=[i.DNSServerSearchOrder,i]
# sercer=dns.resolver.Resolver()
# sercer.nameservers = ["192.168.2.1",""]
# domain = 'www.baidu.com'
# query_object=sercer.resolve(qname=domain, rdtype='A')
# # query_object = dns.resolver.resolve(qname=domain, rdtype='A',)
# print(query_object)
# for query_item in query_object.response.answer:
#     for item in query_item.items:
#         print("{}的A记录解析地址有：{}".format(domain, item))
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        #base_path = os.path.abspath(".")
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class DnsTester():
    def __init__(self,server1,server2=None,num=0,name="unknown"):
        self.num=num
        self.name = name
        self.server1 = server1
        self.server2 = server2
        self.time=-1
        serverList=[server1]
        self.sercer=dns.resolver.Resolver()
        if server2:
            serverList.append(server2)
        self.sercer.nameservers = serverList
        self.lineBox=tkinter.Frame(testScreen)
        self.lineBox.grid(row=num,column=0,stick="W")

        self.otherMenu=tkinter.Menu(tearoff=False,)
        self.otherMenu.add_command(label="测速", command=self._sympleTestBooter)
        self.otherMenu.add_command(label="删除", command=self.delete)

        self.nameBox=tkinter.ttk.Entry(self.lineBox,width=15)
        self.nameBox.insert(0,name)
        self.nameBox.config(state="readonly")
        self.nameBox.grid(row=0,column=0)
        self.nameBox.bind("<Button-3>",self.otherRightClick)

        self.server1Menu = tkinter.Menu(tearoff=False,)
        self.server1Menu.add_command(label="测速", command=self._sympleTestBooter)
        self.server1Menu.add_command(label="设为首选DNS", command=self.server1SetFirstChoice)
        self.server1Menu.add_command(label="设为备选DNS", command=self.server1SetSecondChoice)
        self.server1Menu.add_command(label="删除", command=self.delete)

        self.Server1Box=tkinter.ttk.Entry(self.lineBox,width=20)
        self.Server1Box.insert(0,server1)
        self.Server1Box.config(state="readonly")
        self.Server1Box.grid(row=0,column=1)
        self.Server1Box.bind("<Button-3>",self.server1RightClick)
        
        self.Server2Box=tkinter.ttk.Entry(self.lineBox,width=20)
        if server2:
            self.server2Menu = tkinter.Menu(tearoff=False,)
            self.server2Menu.add_command(label="测速", command=self._sympleTestBooter)
            self.server2Menu.add_command(label="设为首选DNS", command=self.server2SetFirstChoice)
            self.server2Menu.add_command(label="设为备选DNS", command=self.server2SetSecondChoice)
            self.server2Menu.add_command(label="删除", command=self.delete)
            self.Server2Box.insert(0,server2)
            self.Server2Box.bind("<Button-3>",self.server2RightClick)
        else:
            self.Server2Box.bind("<Button-3>",self.otherRightClick)
        self.Server2Box.config(state="readonly")
        self.Server2Box.grid(row=0,column=2)

        self.timeBox=tkinter.ttk.Entry(self.lineBox,width=15)
        self.timeBox.insert(0,"待测试")
        self.timeBox.config(state="readonly")
        self.timeBox.grid(row=0,column=3)
        self.timeBox.bind("<Button-3>",self.otherRightClick)

        self.retsultBox=tkinter.ttk.Entry(self.lineBox,width=15)
        self.retsultBox.insert(0,"待测试")
        self.retsultBox.config(state="readonly")
        self.retsultBox.grid(row=0,column=4)
        self.retsultBox.bind("<Button-3>",self.otherRightClick)
    def _sympleTestBooter(self):
        global onTest
        if onTest:
            tkinter.messagebox.showinfo("检测进行中","有另外一个检测正在进行,请等待上一次检测完成后重试")
            return
        onTest=True
        threading.Thread(target=self._sympleTest,daemon=True).start()
    def _sympleTest(self):
        global onTest
        
        self.clear()
        self.test(aimDomainBox.get(),aimTypeBox.get())
        a=testers.sort()
        for i in range(len(testers)):
            testers[i].resort(i)
        onTest=False
    def delete(self):
        if len(testers)<=1:
            tkinter.messagebox.showerror("错误","不能删除最后一条记录,请先添加其他DNS服务器")
            return
        if tkinter.messagebox.askokcancel("删除本DNS",f"是否确认从列表中删除{self.name}?"):
            self.lineBox.destroy()
            del testers[self.num]
            for i in range(len(testers)):
                testers[i].resort(i)
    def otherRightClick(self,event):
        event.widget.focus_set()
        self.otherMenu.post(event.x_root, event.y_root)
    def server1RightClick(self,event):
        self.Server1Box.focus_set()
        self.server1Menu.post(event.x_root, event.y_root)
    def server1SetFirstChoice(self):
        global nowDNS,nowConfig,netConfigs,needReboot
        arrDNSServers = [self.server1]
        if nowDNS and len(nowDNS)>1:
            arrDNSServers.append(nowDNS[1])
        try:
            retsult=netConfigs[nowConfig][1].SetDNSServerSearchOrder(arrDNSServers)
        except:
            tkinter.messagebox.showerror("错误","设置网络配置时出现错误")
            return
        print(retsult,type(retsult))
        if retsult==(0,):
            tkinter.messagebox.showinfo("DNS变更",f"{nowConfig}\n的首选DNS服务器成功设置为{self.server1}")
            nowDNS=arrDNSServers
            netConfigs[nowConfig][0]=arrDNSServers
            changeNetConfig(configChoice)
        elif retsult==(1,):
            tkinter.messagebox.showwarning("DNS变更",f"{nowConfig}\n的首选DNS服务器成功设置为{self.server1}\n本次更改需要重启")
            nowDNS=arrDNSServers
            netConfigs[nowConfig][0]=arrDNSServers
            needReboot=True
            changeNetConfig(configChoice)
        else:
            tkinter.messagebox.showerror("错误",f"无法设置此网络的DNS,错误码{retsult}")
    def server1SetSecondChoice(self):
        global nowDNS,nowConfig,netConfigs,needReboot
        if not nowDNS or len(nowDNS)<1:
            if tkinter.messagebox.askyesno("首选DNS服务器缺失","当前网络没有首选DNS服务器,无法设置备选DNS服务器\n将本DNS服务器设置为首选?"):
                self.server1SetFirstChoice()
            return
        arrDNSServers = [nowDNS[0],self.server1]
        try:
            retsult=netConfigs[nowConfig][1].SetDNSServerSearchOrder(arrDNSServers)
        except:
            tkinter.messagebox.showerror("错误","设置网络配置时出现错误")
            return
        if retsult==(0,):
            tkinter.messagebox.showinfo("DNS变更",f"{nowConfig}\n的备选DNS服务器成功设置为{self.server1}")
            nowDNS=arrDNSServers
            netConfigs[nowConfig][0]=arrDNSServers
            changeNetConfig(configChoice)
        elif retsult==(1,):
            tkinter.messagebox.showwarning("DNS变更",f"{nowConfig}\n的备选DNS服务器成功设置为{self.server1}\n本次更改需要重启")
            nowDNS=arrDNSServers
            netConfigs[nowConfig][0]=arrDNSServers
            needReboot=True
            changeNetConfig(configChoice)
        else:
            tkinter.messagebox.showerror("错误",f"无法设置此网络的DNS,错误码{retsult}")
    def server2RightClick(self,event):
        self.Server2Box.focus_set()
        self.server2Menu.post(event.x_root, event.y_root)
    def server2SetFirstChoice(self):
        global nowDNS,nowConfig,netConfigs,needReboot
        arrDNSServers = [self.server2]
        if nowDNS and len(nowDNS)>1:
            arrDNSServers.append(nowDNS[1])
        try:
            retsult=netConfigs[nowConfig][1].SetDNSServerSearchOrder(arrDNSServers)
        except:
            tkinter.messagebox.showerror("错误","设置网络配置时出现错误")
            return
        print(retsult,type(retsult))
        if retsult==(0,):
            tkinter.messagebox.showinfo("DNS变更",f"{nowConfig}\n的首选DNS服务器成功设置为{self.server2}")
            nowDNS=arrDNSServers
            netConfigs[nowConfig][0]=arrDNSServers
            changeNetConfig(configChoice)
        elif retsult==(1,):
            tkinter.messagebox.showwarning("DNS变更",f"{nowConfig}\n的首选DNS服务器成功设置为{self.server2}\n本次更改需要重启")
            nowDNS=arrDNSServers
            netConfigs[nowConfig][0]=arrDNSServers
            needReboot=True
            changeNetConfig(configChoice)
        else:
            tkinter.messagebox.showerror("错误",f"无法设置此网络的DNS,错误码{retsult}")
    def server2SetSecondChoice(self):
        global nowDNS,nowConfig,netConfigs,needReboot
        if not nowDNS or len(nowDNS)<1:
            if tkinter.messagebox.askyesno("首选DNS服务器缺失","当前网络没有首选DNS服务器,无法设置备选DNS服务器\n将本DNS服务器设置为首选?"):
                self.server2SetFirstChoice()
            return
        arrDNSServers = [nowDNS[0],self.server2]
        try:
            retsult=netConfigs[nowConfig][1].SetDNSServerSearchOrder(arrDNSServers)
        except:
            tkinter.messagebox.showerror("错误","设置网络配置时出现错误")
            return
        if retsult==(0,):
            tkinter.messagebox.showinfo("DNS变更",f"{nowDNS}\n的备选DNS服务器成功设置为{self.server2}")
            nowDNS=arrDNSServers
            netConfigs[nowConfig][0]=arrDNSServers
            changeNetConfig(configChoice)
        elif retsult==(1,):
            tkinter.messagebox.showwarning("DNS变更",f"{nowDNS}\n的备选DNS服务器成功设置为{self.server2}\n本次更改需要重启")
            nowDNS=arrDNSServers
            netConfigs[nowConfig][0]=arrDNSServers
            needReboot=True
            changeNetConfig(configChoice)
        else:
            tkinter.messagebox.showerror("错误",f"无法设置此网络的DNS,错误码{retsult}")
    def test(self,domain,type):
        
        self.timeBox.config(state="normal")
        self.timeBox.delete(0,tkinter.END)
        self.timeBox.insert(0,"测试中")
        self.timeBox.config(state="readonly")

        
        self.retsultBox.config(state="normal")
        self.retsultBox.delete(0,tkinter.END)
        self.retsultBox.insert(0,"测试中")
        self.retsultBox.config(state="readonly")
        try:
            retsult=self.sercer.resolve(qname=domain, rdtype=type)
        except BaseException as e:
            self.timeBox.config(state="normal")
            self.timeBox.delete(0,tkinter.END)
            self.timeBox.insert(0,"失败")
            self.timeBox.config(state="readonly")

            self.retsultBox.config(state="normal")
            self.retsultBox.delete(0,tkinter.END)
            self.retsultBox.insert(0,"失败")
            self.retsultBox.config(state="readonly")
            self.time=-1
        else:
            self.time=retsult.response.time*1000
            self.timeBox.config(state="normal")
            self.timeBox.delete(0,tkinter.END)
            self.timeBox.insert(0,str(int(self.time+0.5))+"ms")
            self.timeBox.config(state="readonly")

            if type=="A":
                sumAll=0
                sumAccept=0
                for i in retsult.response.answer:
                    for j in i.items:
                        if j.rdtype==1:
                            sumAll+=1
                            try:
                                statusCode=requests.get("http://"+j.address).status_code
                            except:
                                print(j.address)
                                pass
                            else:
                                if statusCode//100 in [2,3]:
                                    sumAccept+=1
                                else:
                                    print(j.address,statusCode)
                if sumAll==0:
                    self.retsultBox.config(state="normal")
                    self.retsultBox.delete(0,tkinter.END)
                    self.retsultBox.insert(0,"空")
                    self.retsultBox.config(state="readonly")
                elif sumAll==sumAccept:
                    self.retsultBox.config(state="normal")
                    self.retsultBox.delete(0,tkinter.END)
                    self.retsultBox.insert(0,"全部成功")
                    self.retsultBox.config(state="readonly")
                elif sumAccept==0:
                    self.retsultBox.config(state="normal")
                    self.retsultBox.delete(0,tkinter.END)
                    self.retsultBox.insert(0,"全部失败")
                    self.retsultBox.config(state="readonly")
                else:
                    self.retsultBox.config(state="normal")
                    self.retsultBox.delete(0,tkinter.END)
                    self.retsultBox.insert(0,f"{sumAccept}/{sumAll}成功")
                    self.retsultBox.config(state="readonly")
            else:
                self.retsultBox.config(state="normal")
                self.retsultBox.delete(0,tkinter.END)
                self.retsultBox.insert(0,"---")
                self.retsultBox.config(state="readonly")
    def clear(self):
        self.timeBox.config(state="normal")
        self.timeBox.delete(0,tkinter.END)
        self.timeBox.insert(0,"待测试")
        self.timeBox.config(state="readonly")

        
        self.retsultBox.config(state="normal")
        self.retsultBox.delete(0,tkinter.END)
        self.retsultBox.insert(0,"待测试")
        self.retsultBox.config(state="readonly")
    def resort(self,num):
        self.num=num
        self.lineBox.grid(row=num,column=0)
    def __lt__(self,other):
        if other.time==-1:
            return True
        if self.time==-1:
            return False
        return self.time < other.time 

            
        

defaultDNSList=[("114.114.114.114","114.114.114.115","114DNS"),
    ("223.5.5.5","223.6.6.6","阿里DNS"),
    ("8.8.8.8","8.8.4.4","Google DNS"),
    ("208.67.222.222","208.67.220.220","OpenDNS"),
    ("180.76.76.76","","百度DNS"),
    ("1.2.4.8","202.98.0.6","CNNIC SDNS"),
    ("119.29.29.29","182.254.116.116","DNSPod DNS+"),
    ("4.4.4.2","4.4.4.1","Microsoft DNS")
]

mainScreen=tkinter.Tk()
mainScreen.resizable(width=False,height=False)
mainScreen.iconbitmap(resource_path(os.path.join("logo.ico")))
mainScreen.title("DNS测速")

titleBox=tkinter.Frame(mainScreen)
titleBox.grid(row=0,column=0,stick="W",padx=2,pady=0)

nameBox=tkinter.ttk.Entry(titleBox,width=15)
nameBox.insert(0,"DNS服务器")
nameBox.config(state="readonly")
nameBox.grid(row=0,column=0)

Server1Box=tkinter.ttk.Entry(titleBox,width=20)
Server1Box.insert(0,"IP地址1")
Server1Box.config(state="readonly")
Server1Box.grid(row=0,column=1)


Server2Box=tkinter.ttk.Entry(titleBox,width=20)
Server2Box.insert(0,"IP地址2")
Server2Box.config(state="readonly")
Server2Box.grid(row=0,column=2)

timeBox=tkinter.ttk.Entry(titleBox,width=15)
timeBox.insert(0,"延时")
timeBox.config(state="readonly")
timeBox.grid(row=0,column=3)

retsultBox=tkinter.ttk.Entry(titleBox,width=15)
retsultBox.insert(0,"http可连接性")
retsultBox.config(state="readonly")
retsultBox.grid(row=0,column=4)

testScreen=tkinter.Frame(mainScreen,width=800,background="white")
testScreen.grid(row=1,column=0,sticky="W",padx=2,pady=0)

nowConfig=""
nowDNS=[]

dnsFrame=tkinter.Frame(mainScreen,)
dnsFrame.grid(row=4,column=0,sticky="WE")
        

dns1Box=tkinter.ttk.Entry(dnsFrame,width=44)
dns1Box.config(state="readonly")
dns1Box.grid(row=0,column=0,sticky="W",padx=2,pady=2)
dns2Box=tkinter.ttk.Entry(dnsFrame,width=43)
dns2Box.config(state="readonly")
dns2Box.grid(row=0,column=1,sticky="E",padx=2,pady=2)

testValueFrame=tkinter.Frame(mainScreen)
aimDomainBox=tkinter.ttk.Entry(testValueFrame,width=64)
aimDomainBox.insert(0,"www.baidu.com")
aimDomainBox.grid(row=0,column=0,sticky="W",padx=2,pady=2)
aimTypeBox=tkinter.ttk.Combobox(testValueFrame,width="20")
aimTypeBox["value"] = ["A","MX","CNAME","NS","PTR","SOA"]
aimTypeBox.config(state="readonly")
aimTypeBox.current(0)
aimTypeBox.grid(row=0,column=1,sticky="E",padx=2,pady=2)
testValueFrame.grid(row=5,column=0,sticky="WE")

def changeNetConfig(newConfig):
    global nowConfig,nowDNS
    nowConfig=newConfig.get()
    nowDNS=netConfigs[nowConfig][0]
    print(nowDNS)
    dns1Box.config(state="normal")
    dns1Box.delete(0,tkinter.END)
    dns2Box.config(state="normal")
    dns2Box.delete(0,tkinter.END)
    if nowDNS:
        dns1Box.insert(0,nowDNS[0])
        if len(nowDNS)>1:
            dns2Box.insert(0,nowDNS[1])
    dns1Box.config(state="readonly")
    dns2Box.config(state="readonly")



configChoice=tkinter.StringVar()
configChoice.trace("w", lambda name, index, mode, configChoice=configChoice: changeNetConfig(configChoice))
netConfig=tkinter.ttk.Combobox(mainScreen,font=('microsoft yahei', 10, 'bold'),textvariable=configChoice)
netConfig["value"] = list(netConfigs.keys())
netConfig.config(state="readonly")
netConfig.current(0)
netConfig.grid(row=3,column=0,sticky="WE",padx=2,pady=5)

testers=[]

onTest=False

def startTest():
    global onTest
    for i in range(len(testers)):
        testers[i].clear()
    pool=concurrent.futures.ThreadPoolExecutor(max_workers=5)
    for i in range(len(testers)):
        end=pool.submit(testers[i].test,aimDomainBox.get(),aimTypeBox.get())
    while not end.done():
        time.sleep(0.3)
    testers.sort()
    for i in range(len(testers)):
        testers[i].resort(i)
    onTest=False
def startTestBooter():
    global onTest
    if onTest:
        tkinter.messagebox.showinfo("检测进行中","有另外一个检测正在进行,请等待上一次检测完成后重试")
        return
    onTest=True
    threading.Thread(target=startTest,daemon=True).start()
onAddScreen=False
def addDNS():
    global addScreen,onAddScreen
    addScreen=tkinter.Toplevel(mainScreen)
    addScreen.resizable(width=False,height=False)
    addScreen.iconbitmap(resource_path(os.path.join("logo.ico")))
    addScreen.title("添加")
    addScreen.grab_set()

    inputFrame=tkinter.Frame(addScreen)
    inputFrame.grid(row=0,column=0)

    nameTitle=tkinter.Label(inputFrame,text="标识:*")
    nameTitle.grid(row=0,column=0,sticky="W",padx=2,pady=5)
    nameBox=tkinter.ttk.Entry(inputFrame,width=20)
    nameBox.grid(row=0,column=1,sticky="W",padx=2,pady=5)

    server1Title=tkinter.Label(inputFrame,text="首选地址:*")
    server1Title.grid(row=1,column=0,sticky="W",padx=2,pady=5)
    server1Box=tkinter.ttk.Entry(inputFrame,width=20)
    server1Box.grid(row=1,column=1,sticky="W",padx=2,pady=5)

    server2Title=tkinter.Label(inputFrame,text="备选地址:")
    server2Title.grid(row=2,column=0,sticky="W",padx=0,pady=5)
    server2Box=tkinter.ttk.Entry(inputFrame,width=20)
    server2Box.grid(row=2,column=1,sticky="W",padx=2,pady=5)

    buttonFrame=tkinter.Frame(addScreen)
    buttonFrame.grid(row=1,column=0,sticky="E",padx=2,pady=5)

    def save():
        ret1=re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        name=nameBox.get()
        server1=server1Box.get()
        server2=server2Box.get()
        if not name:
            tkinter.messagebox.showwarning("标识为空","标识是必填字段")
            nameBox.focus_set()
            return
        elif not server1:
            tkinter.messagebox.showwarning("首选DNS为空","首选DNS是必填字段")
            server1Box.focus_set()
            return
        elif ret1.match(server1)==None:
            tkinter.messagebox.showwarning("首选DNS错误","首选DNS内容不是一个正确的IPv4地址")
            server1Box.focus_set()
            return
        elif not server2:
            testers.append(DnsTester(server1=server1,server2="",num=len(testers),name=name))
        else:
            if ret1.match(server2)==None:
                tkinter.messagebox.showwarning("备选DNS错误","备选DNS内容不是一个正确的IPv4地址")
                server2Box.focus_set()
                return
            testers.append(DnsTester(server1=server1,server2=server2,num=len(testers),name=name))
        addScreen.destroy()
        

    saveButton=tkinter.ttk.Button(buttonFrame,text="确定",command=save)
    saveButton.grid(row=0,column=0,sticky="E",padx=2,pady=0)

    cancleButton=tkinter.ttk.Button(buttonFrame,text="取消",command=addScreen.destroy)
    cancleButton.grid(row=0,column=1,sticky="E",padx=2,pady=0)


buttonBox=tkinter.Frame(mainScreen)
testButton=tkinter.ttk.Button(buttonBox,text="检测全部",command=startTestBooter,state="disabled")
testButton.grid(row=0,column=1,stick="E",padx=2,pady=5)
addButton=tkinter.ttk.Button(buttonBox,text="添加",command=addDNS,state="disabled")
addButton.grid(row=0,column=0,stick="E",padx=2,pady=5)
buttonBox.grid(row=2,column=0,stick="E")

def loadDNSList():
    for i in range(len(defaultDNSList)):
        testers.append(DnsTester(server1=defaultDNSList[i][0],server2=defaultDNSList[i][1],name=defaultDNSList[i][2],num=i))
    addButton.config(state="normal")
    testButton.config(state="normal")

threading.Thread(target=loadDNSList,daemon=True).start()

mainScreen.mainloop()