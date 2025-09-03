import socket

def portScanner(host, port):
    try:
      
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        
     
        result = s.connect_ex((host, port))
        
        if result == 0:
            print(f"Port {port} is open")
        else:
            print(f"Port {port} is closed")
            
    except socket.gaierror:
        print(f"Error: Could not resolve hostname {host}")
    except Exception as e:
        print(f"Error scanning port {port}: {e}")
    finally:
        s.close()

host = input("Please enter the IP you want to scan: ")
port = int(input("Please enter the port you would like to scan: "))


portScanner(host, port)
