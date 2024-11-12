from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import logging
import threading
import time
from datetime import datetime
import socket
port = 7497
class IBAPI(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.connection_thread = None
        self.last_connection_time = None
        self.connection_attempts = 0
        self.max_reconnect_attempts = 3
        self.reconnect_delay = 5  # seconds
        self.timeout = 20  # socket timeout in seconds
        self.heartbeat_timeout = 60  # seconds without message before considering connection dead
        self.last_message_time = None
        
        # Setup logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        """Handle error messages from TWS"""
        self.logger.error(f"Error {errorCode}: {errorString}")
        self.last_message_time = datetime.now()
        
        # Handle specific error codes
        if errorCode == 502:  # Couldn't connect to TWS
            self.connected = False
            self.logger.error("Couldn't connect to TWS. Make sure TWS/Gateway is running and API connections are enabled.")
        elif errorCode == 504:  # Not connected
            self.connected = False
            self.logger.error("Not connected to TWS.")
            self._attempt_reconnect()
            
    def connectionClosed(self):
        """Handle connection closed event"""
        self.connected = False
        self.logger.warning("Connection closed")
        self._attempt_reconnect()
        
    def _attempt_reconnect(self):
        """Attempt to reconnect with backoff"""
        if self.connection_attempts < self.max_reconnect_attempts:
            self.connection_attempts += 1
            wait_time = self.reconnect_delay * self.connection_attempts
            self.logger.info(f"Attempting reconnection in {wait_time} seconds... (Attempt {self.connection_attempts}/{self.max_reconnect_attempts})")
            time.sleep(wait_time)
            self.connect("127.0.0.1", port, clientId=1)
        else:
            self.logger.error("Max reconnection attempts reached. Please check your connection and restart the application.")
            
    def connect(self, host, port, clientId):
        """Enhanced connect method with connection monitoring and timeout handling"""
        self.logger.info(f"Connecting to {host}:{port} with ID {clientId}")
        
        # Reset connection status
        self.connected = False
        self.last_connection_time = datetime.now()
        self.last_message_time = datetime.now()
        
        # Configure socket timeout
        socket.setdefaulttimeout(self.timeout)
        
        # Start connection monitor thread
        if self.connection_thread is None or not self.connection_thread.is_alive():
            self.connection_thread = threading.Thread(target=self._monitor_connection)
            self.connection_thread.daemon = True
            self.connection_thread.start()
        
        # Attempt connection
        try:
            super().connect(host, port, clientId)
            time.sleep(1)  # Give time for connection to establish
            
            # Start message processing thread
            thread = threading.Thread(target=self._run_with_timeout)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            self._attempt_reconnect()
    
    def _run_with_timeout(self):
        """Wrapper for EClient.run() with timeout handling"""
        while self.isConnected():
            try:
                self.run()
            except socket.timeout:
                self.logger.warning("Socket timeout occurred, checking connection status...")
                if self._check_connection_alive():
                    continue
                else:
                    self.logger.error("Connection appears to be dead, initiating reconnect...")
                    self._attempt_reconnect()
                    break
            except Exception as e:
                self.logger.error(f"Error in message processing: {str(e)}")
                self._attempt_reconnect()
                break
                
    def _check_connection_alive(self):
        """Check if connection is still alive based on last message time"""
        if self.last_message_time is None:
            return False
            
        time_since_last_message = (datetime.now() - self.last_message_time).total_seconds()
        return time_since_last_message < self.heartbeat_timeout
            
    def _monitor_connection(self):
        """Monitor connection status and handle timeouts"""
        while True:
            if self.connected:
                if not self.isConnected() or not self._check_connection_alive():
                    self.logger.warning("Connection lost or timeout occurred!")
                    self.connected = False
                    self._attempt_reconnect()
            time.sleep(1)
            
    def connectAck(self):
        """Handle successful connection"""
        self.connected = True
        self.connection_attempts = 0  # Reset connection attempts
        self.last_message_time = datetime.now()
        self.logger.info("Connection successful!")
        
    def nextValidId(self, orderId):
        """Handle next valid order ID - confirms successful connection"""
        super().nextValidId(orderId)
        self.logger.info(f"Connected with first valid order ID: {orderId}")
        self.connected = True
        self.last_message_time = datetime.now()
        
    def send_ping(self):
        """Send a ping to keep connection alive"""
        if self.connected:
            # reqCurrentTime() is a lightweight way to ping the server
            self.reqCurrentTime()
            self.logger.debug("Ping sent")
            
    def currentTime(self, timestamp):
        """Handle server response to ping"""
        self.last_message_time = datetime.now()
        self.logger.debug("Pong received")

# Usage example with ping mechanism
def main():
    app = IBAPI()
    try:
        app.connect("127.0.0.1", port, clientId=1)
        
        # Keep main thread alive and implement ping
        while True:
            if app.connected:
                # Send ping every 30 seconds to keep connection alive
                app.send_ping()
            time.sleep(30)
            
    except KeyboardInterrupt:
        app.disconnect()
        print("Application terminated by user")
        
if __name__ == "__main__":
    main()