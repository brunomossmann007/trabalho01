# Relatorio - Laboratório de Sistema Operacionais
## Bruno Mossmann Almeida Matricula: 22180462

<hr>

### <strong>1. Preparar o Buildroot para compilar para alvo específico</strong>

O comando abaixo deve ser executado para configurar o Buildroot para gerar uma emulação com o QEMU:

`$ make qemu_x86_defconfig`

<hr>

### <strong>2. Entre no menu de configurações:</strong>
Sequência de comandos para instalar o cpio:

`$ sudo apt update`

`$ sudo apt-get install cpio`

`$ make linux-menuconfig`

Habilite o driver Ethernet e1000 Intel(R) PRO/1000 Gigabit Ethernet support.

````
Device Drivers  --->
  	[*] Network device support  --->
  		[*]   Ethernet driver support  ---> 
  		<*>     Intel(R) PRO/1000 Gigabit Ethernet support 
````

<hr>

### <strong>3. Compilação:</strong>

`$ make MAKEINFO=false`
<hr>

### <strong>4. Emulando com QEMU:</strong>

`$ sudo apt-get install qemu-system`

Para emular a distribuição execute:

````
sudo qemu-system-i386 --device e1000,netdev=eth0,mac=aa:bb:cc:dd:ee:ff \
    --netdev tap,id=eth0,script=custom-scripts/qemu-ifup.sh \
    --kernel output/images/bzImage \
    --hda output/images/rootfs.ext2 \
    --nographic \
    --append "console=ttyS0 root=/dev/sda"
````
Se pedir buildroot login, o usuário é "root"
Se pedir senha é só apertar a tecla "enter"

Para encerrar o QEMU execute:

`# poweroff`

<hr>

### <strong>5. Configurando a rede:</strong>

 Agora para ter uma comunicação por rede emulada, entre o sistema operacional guest e a máquina host.

Rode o comando a seguir para dar permissão de execução ao arquivo qemu-ifup.sh, que está dentro da pasta *custom-scripts*

`$ chmod +x custom-scripts/qemu-ifup`

Execute o seguinte comando: 

````
sudo qemu-system-i386 --device e1000,netdev=eth0,mac=aa:bb:cc:dd:ee:ff \
    --netdev tap,id=eth0,script=custom-scripts/qemu-ifup.sh \
    --kernel output/images/bzImage \
    --hda output/images/rootfs.ext2 \
    --nographic \
    --append "console=ttyS0 root=/dev/sda"
````

O usuário é: "root"

Para definir uma senha, use o comando:

`# passwd`

Depois de definir a senha, quando for executar a emulação você deverá digitar o usuário "root".

Para sair da emulação, basta digitar:

`$ poweroff`

<hr>

### <strong>6. Testando com PING:</strong>
Agora chegou o momento de configurar o roteamente da rede no "gues", para considerar o "host" como seu roteador principal. 

Na "máquina guest" e execute:

`$ ifconfig eth0 192.168.1.10 up`

 Já no guest, precisamos definir uma rota padrão para o IP do host:

````
$ route add -host <IP-DO-HOST> dev eth0
$ route add default gw <IP-DO-HOST>
````

Para saber o IP do host:

`$ ifconfig`

No guest, tente pingar o IP do host:

`$ ping <IP-DO-HOST>`

No host, tente pingar o IP do guest:

`$ ping 192.168.1.10`

Se o comando "ping" não for encontrado, execute na máquina host:

`$ sudo apt-get install iputils-ping`

<hr>

### <strong>7. Tornar configurações no GUEST fixo:</strong>

Para tornar as configurações no GUEST fixas, foram criados os arquivos *pre-build.sh* e *S41network-config*, que estão na pasta *custom-scripts*.

Para conceder acesso de execução ao arquivo *pre-build.sh*, execute:

`$ chmod +x custom-scripts/pre-build.sh`

<hr>



### <strong>8. Adicionando Iperf no target</strong>

Precisamos adicionar suporte ao compilador C++ na toolchain para poder adicionarmos o Iperf.

Na host, execute:

`$ make menuconfig`

Faça as seguintes configurações:

````
Toolchain  --->
  	 [*] Enable C++ support
````

````
Target packages  --->
  	 Networking applications  --->
  		 [*] iperf
````
A modificação na *toolchain* irá exigir a recompilação de toda a distribuição:

`$ make clean`

Depois realizar o comando acima, precisamos assegurar que ainda estamos com as configurações do kernel relacionadas a device drivers configuradas. Portanto, execute:

`$ make linux-menuconfig`

E habilite o driver Ethernet e1000

````
Device Drivers  ---> 
  	[*] Network device support  --->    
  		[*]   Ethernet driver support  ---> 
  		<*>     Intel(R) PRO/1000 Gigabit Ethernet support
````

Salve as configurações e recompile:

`$ make`


<hr>

### <strong>9. Executando testes com Iperf:</strong>
Iperf: opera como um cliente/servidor. 

No diretório "iperf/iperf-2.1.8", configure e compile o iperf:


````
$ ./configure
$ make
````

BANDWIDTH:

Na máquina "target", execute o comando a seguir:

`$ iperf -s`

Isso fará on iperf escutar conexões na porta 5001

Na máquina "host", execute o iperf compilado:

`$ iperf/iperf-2.1.8/src/iperf -c 192.168.1.10 -i 1 -t 5`

JITTER:
variação do atraso da rede enter 2 hosts

Execute na target:

`$ iperf -s -u`

Execute no host:

`$ iperf/iperf-2.1.8/src/iperf -c 192.168.1.10 -i 1 -t 5 -u`


<hr>

### <strong>10. Comunicação:</strong>

Instalar o pacote "netcat" na distribuição, no menuconfig:

`$ make menuconfig`

````
Target packages  --->
  	[*]   Show packages that are also provided by busybox
  	Networking applications  --->
  		[*] netcat
````

Recompile

`$ make`

Na "target", usar o programa "nc" para escutar o tráfego na porta 8000:

`$ nc -l -p 8000`

No "host", use o "nc" para enviar a mensagem digitada no terminal:

`$ nc 192.168.1.10 8000`


<hr>

### <strong>11. Executando o servidor feito em python:</strong>

Na máquina "hos", instale:
Adicionar o arquivo python que vai ser rodado na máquina target.

````
$ sudo apt install ssh
$ sudo apt-get install lynx

$ scp server.py root@192.168.1.10:/

````

Na máquina "target", depois que o arquivo *server.py* for copiada, entre no arquivo usando `vi server.py` e altere a constante "HOST_NAME" para o IP da máquina target (192.168.1.10).

Na máquina "target", rode o arquivo "server.py" para iniciar o servidor.

`$ python server.py`

Página HTML que acabamos de rodar, na máquina host, execute:

`$ lynx 192.168.1.10`

**Final**