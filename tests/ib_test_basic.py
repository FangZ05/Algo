from ibapi.client import EClient
from ibapi.wrapper import EWrapper  
import time
class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self) 
        self.connected = False
        
    def connectionClosed(self):
        self.connected = False
        print("Connection closed")
        
    def connect(self, host, port, clientId):
        self.connected = True
        super().connect(host, port, clientId)
        print(f"Connecting to {host}:{port} with ID {clientId}")

app = IBapi()
app.disconnect()
print("debug message1")
app.connect('127.0.0.1', 4001, clientId=771)

time.sleep(2)
print("debug message2")
app.run()


#Uncomment this section if unable to connect
#and to prevent errors on a reconnect

app.disconnect()
