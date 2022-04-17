import threading,psutil,time,math,socket,requests,json,platform,os,sys

#
# waynechen251
# client
#

#基本設定與資訊
testMode = True #開發者模式
sleepTime = 1 #執行暫停秒數
threadList = [] #任務清單
jsonString = "" #要發送給主控端的資訊
clientVersion = "1.0"
dateTime = "" #紀錄資訊的時間
run = True #是否繼續執行程式
client = None #連線物件
MoniterIP = "192.168.0.148"
#系統資訊
CpuLoading = 0 #CPU使用率
CpuCount_P = 0 #CPU核心數
CpuCount_L = 0 #CPU執行緒數
RamTotal = 0 #記憶體總容量
RamUsed = 0 #已使用記憶體容量
RamFree = 0 #可用記憶體容量
RamLoading = 0 #記憶體使用率
LocalIP = "" #內網網路位址
InternetIP = "" #外網網路位址
hostName = "" #主機名稱
os_name = os.name #
sys_platform = sys.platform #
platform_system = platform.system() #
bit = "" #系統位元

#蒐集系統資訊
def collectData():
    global jsonString,dateTime

    dateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    infoDict = {
        "OtherInfo" : {
            "clientVersion" : clientVersion,
            "dateTime" : dateTime,
            "hostName" : hostName,
            "os_name" : os_name,
            "sys_platform" : sys_platform,
            "platform_system" : platform_system,
            "bit" : bit
        },
        "CpuInfo" : {
            "CpuCount_P" : CpuCount_P,
            "CpuCount_L" : CpuCount_L,
            "CpuLoading" : CpuLoading
        },
        "RamInfo" : {
            "RamTotal" : RamTotal,
            "RamUsed" : RamUsed,
            "RamFree" : RamFree,
            "RamLoading" : RamLoading
        },
        "NetWorkInfo" : {
            "InternetIP" : InternetIP,
            "LocalIP" : LocalIP,
        }
    }
    jsonString = json.dumps(infoDict)

#傳送系統資訊
def sendData():
    global run,client

    showInfo()

    try:
        client.send(jsonString.encode('utf-8'))
        print("[System]Report Success\n")
    except:
        print("[System]Report Fail, Try to reconnect\n")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((MoniterIP, 666))

#顯示系統資訊
def showInfo():
    print(
        f"{dateTime}: \n" +
        f"主機名稱=\t\t\t\t{hostName} \n" +
        f"CPU使用率=\t\t\t{CpuLoading} \n" +
        f"CPU核心數=\t\t\t{CpuCount_P} \n" +
        f"CPU執行緒數=\t\t\t{CpuCount_L} \n" +
        f"記憶體總容量=\t\t\t{RamTotal} \n" +
        f"已使用記憶體容量=\t\t{RamUsed} \n" +
        f"可用記憶體容量=\t\t{RamFree} \n" +
        f"記憶體使用率=\t\t\t{RamLoading} \n" +
        f"內網網路位址=\t\t\t{LocalIP} \n" +
        f"外網網路位址=\t\t\t{InternetIP} \n" +
        f"系統位元=\t\t\t\t{bit} \n" +
        f"os_name=\t\t\t\t{os_name} \n" +
        f"sys_platform=\t\t{sys_platform} \n" +
        f"platform_system=\t{platform_system} \n" +
        f"jsonString={jsonString} \n"
    )

#取得CPU相關資訊
def getCpuInfo():
    global CpuCount_P,CpuCount_L,CpuLoading

    while(True):
        CpuCount_P = psutil.cpu_count(logical=False)
        CpuCount_L = psutil.cpu_count()
        CpuLoading = psutil.cpu_percent()
        time.sleep(sleepTime)

#取得記憶體相關資訊
def getRamInfo():
    global RamTotal,RamUsed,RamFree,RamLoading

    Memory = psutil.virtual_memory()

    while(True):
        RamTotal = Memory.total / 1024 / 1024 / 1024
        RamTotal = round(RamTotal,1)

        RamUsed = Memory.used / 1024 / 1024 / 1024
        RamUsed = round(RamUsed,1)

        RamFree = Memory.free / 1024 / 1024 / 1024
        RamFree = round(RamFree,1)

        RamLoading = (RamUsed/RamTotal) * 100
        RamLoading = round(RamLoading,1)

        time.sleep(sleepTime)

#取得網路相關資訊
def getNetWorkInfo():
    global LocalIP,InternetIP

    while(True):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        LocalIP = s.getsockname()[0]
        s.close()
        InternetIP = requests.get("http://ifconfig.me/ip",timeout=1).text.strip()
        time.sleep(sleepTime)

#取得未定義類別之系統資訊
def getOtherInfo():
    global hostName,bit

    hostName = socket.gethostname()
    if('PROGRAMFILES(X86)' in os.environ):
        bit = "64"
    else:
        bit = "32"

#定義任務清單
def initThread():
    global threadList

    taskList = [getNetWorkInfo,getCpuInfo,getRamInfo,getOtherInfo,sendInfo]
    for task in taskList:
        t = threading.Thread(target=task,args=())
        threadList.append(t)

#啟動任務
def startThread():
    for i in threadList:
        i.start()
    for i in threadList:
        i.join()

def sendInfo():
    while(run):
        try:
            collectData()
            sendData()
            #checkConnection()
            time.sleep(sleepTime)
        except:
            pass

def checkConnection():
    global client

    print("type is =",type(client))
    print(type(client)!="socket.socket")
    print(type(client)=="socket.socket")
    print(type(client)=="<class 'socket.socket'>")
    if(type(client)!="socket.socket"):
        #print("try reconnect...")
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((MoniterIP, 666))
            #print("reconnect success")
        except:
            #print("reconnect fail")
            client.close()

initThread()
startThread()