from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os

HOST_NAME = "127.0.0.1" # mudar depois pro IP do target
PORT_NUMBER = 8080

class Server(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    
    def do_GET(self):
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        self.wfile.write(bytes("<html><head><title>TRABALHO1 LABORATORIO DE SISTEMA OPERACIONAIS</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<h1>Trabalho 01 - Laboratorio de Sistemas Operacionais</h1>", "utf-8"))
        self.wfile.write(bytes("<h2>Bruno Mossmann Almeida</h2>", "utf-8"))
        self.wfile.write(bytes("<p>Dados do servidor:</p>", "utf-8"))
        self.wfile.write(bytes(f"<li><strong>Data e hora do sistema:</strong> {self.getDataEHora()}</li>", "utf-8"))
        self.wfile.write(bytes(f"<li><strong>Uptime em segundos:</strong> {self.getUptime()} </li>", "utf-8"))
        self.wfile.write(bytes(f"<li><strong>Modelo do processador:</strong> {self.getModelName()} </li>", "utf-8"))
        self.wfile.write(bytes(f"<li><strong>Velocidade do processador:</strong> {self.getVelocity()} MHz</li>", "utf-8"))
        self.wfile.write(bytes(f"<li><strong>Capacidade ocupada do processador:</strong> {self.getProcessorCapacity()} </li>", "utf-8"))
        self.wfile.write(bytes(f"<li><strong>Quantidade de memoria RAM Total:</strong> {self.getTotalRAM()} MB </li>", "utf-8"))
        self.wfile.write(bytes(f"<li><strong>Quantidade de memoria RAM Utilizada:</strong> {self.getUsedRAM()} MB </li>", "utf-8"))
        self.wfile.write(bytes(f"<li><strong>Versao do SO:</strong> {self.getSystemVersion()} </li>", "utf-8"))
        
        self.wfile.write(bytes(f"<li><strong>LISTA DE PROCESSOS:</strong></li>", "utf-8"))
        
        processes = self.getRunningProcesses()
        for name, pid in processes:
            self.wfile.write(bytes(f"<ul>Process PID: {pid} | Process name: {name}</ul>", "utf-8"))


    # Modelo do processador
    def getModelName(self):
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'model name' in line:
                    model_name = line.strip().split(':')[1]
                    return model_name
                
    # Velocidade do processador
    def getVelocity(self):
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'cpu MHz' in line:
                    cpu_speed = float(line.strip().split(':')[1])
                    return cpu_speed
                
    # Capacidade ocupada pelo processador
    def getProcessorCapacity(self):
        start = self.getCPUTime()
        #wait a second
        time.sleep(1)
        stop = self.getCPUTime()

        cpu_load = {}

        for cpu in start:
            Total = stop[cpu]['total']
            PrevTotal = start[cpu]['total']

            Idle = stop[cpu]['idle']
            PrevIdle = start[cpu]['idle']
            CPU_Percentage=((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)*100
            cpu_load.update({cpu: CPU_Percentage})
        return cpu_load
        

    # Versao do sistema
    def getSystemVersion(self):
        with open('/proc/version', 'r') as f:
            version_info = f.readline().strip()
            return version_info
    
    # Uptime
    def getUptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return uptime_seconds

    # RAM total
    def getTotalRAM(self):
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal'):
                    total_memory = int(line.split()[1]) / 1024  # convert to MB
                    return total_memory
    
    # RAM usada
    def getUsedRAM(self):
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal'):
                    total_mem = int(line.split()[1])
                elif line.startswith('MemAvailable'):
                    available_mem = int(line.split()[1])

        # Calculate used memory
        used_mem = total_mem - available_mem
        return used_mem


    # Data e hora do sistema
    def getDataEHora(self):
        dateAndHour = os.popen('date').read()
        return dateAndHour
    
    # Processos em execucao
    def getRunningProcesses(self):
        processes = []
        for pid in os.listdir('/proc'):
            if pid.isdigit():
                try:
                    with open(f"/proc/{pid}/comm", 'r') as f:
                        name = f.read().strip()
                        processes.append((name, pid))
                except IOError:
                    continue
        return processes

    # metodo auxiliar para getProcessorCapacity()
    def getCPUTime(self):
        cpu_infos = {} #collect here the information
        with open('/proc/stat','r') as f_stat:
            lines = [line.split(' ') for content in f_stat.readlines() for line in content.split('\n') if line.startswith('cpu')]

            #compute for every cpu
            for cpu_line in lines:
                if '' in cpu_line: cpu_line.remove('')#remove empty elements
                cpu_line = [cpu_line[0]]+[float(i) for i in cpu_line[1:]]#type casting
                cpu_id,user,nice,system,idle,iowait,irq,softrig,steal,guest,guest_nice = cpu_line

                Idle=idle+iowait
                NonIdle=user+nice+system+irq+softrig+steal

                Total=Idle+NonIdle
                #update dictionionary
                cpu_infos.update({cpu_id:{'total':Total,'idle':Idle}})
            return cpu_infos



if __name__ == "__main__":              
    server = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
    print("Server in: http://%s:%s" % (HOST_NAME, PORT_NUMBER))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
    print("Server stopped.")


