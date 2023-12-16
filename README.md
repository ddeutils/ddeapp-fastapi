# Data Framework Application: *FastAPI*

**Type**: `DFA` |
**Tag**: `Data Framework` `Web Application` `Python` `FastAPI` `Docker`

Data Framework API App use that routing with FastAPI


## Deployment


This application require run on local intra network (on premise) server. The OS
is Window server 2016. The solution that we found to run this application is,

1) [Directly with command line](#directly-with-command-line)
2) [Docker on WSL](#with-docker-on-wsl)
3) [Window service](#with-window-service)
4) [Window service by NSSM](#with-window-service-wrapped-by-nssm)
5) [Window Container on Hyper-V](#with-window-container-on-hyper-v)
6) ~~[Linux Container on Hyper-V (LCOW)](#with-linux-container-on-hyper-v--lcow-)~~
7) ~~Window task scheduler~~

### Directly with command line

- First, you must install python version `3.9.13` on your server.

- Start create your python virtual environment for this application.

  ```shell
  $ python -m vnev vnev
  $ venv\Scripts\activate
  ```
- Install all of necessary packages from requirement file.

  ```shell
  (venv) $ pip install -r requirements.txt --no-cache-dir
  (venv) $ ren .{demo}.env .env
  ```

  > **Note**: \
  > Make sure for no caching any packages in pip by this command, 
  > ```shell
  > (venv) $ pip cache purge
  > ```

- Run your application local

  ```shell
  (venv) $ uvicorn main:app --reload
  ```

- (Optional) If you want to stop your application, you can use `Ctrl+C` and deactivate
  your virtual environment.

  ```shell
  (venv) $ deactivate
  ```

### With Docker on WSL

- First, you must check your server installed WSL

  > **Reference**: \
  > docs: [Use Docker for windows in WSL](https://pscheit.medium.com/use-docker-for-windows-in-wsl-8fc96ece67c8)
  > docs: [Unable to locate package docker-ce on a 64bit Ubuntu](https://unix.stackexchange.com/questions/363048/unable-to-locate-package-docker-ce-on-a-64bit-ubuntu)

- Check Docker service running

  ```shell
  $ sudo service docker start
  ```

- Go to the project directory (in where your Dockerfile is, containing your app directory).

- Build your FastAPI image:

  ```shell
  $ sudo docker build -t dedp-fastapi . --no-cache
  $ sudo docker image ls
  ```

- Run a container based on your image:

  ```shell
  $ cp .{demo}.env .env
  $ sudo docker run -d --env-file ./.env --name dedp-fastapi -p 8000:8000 dedp-fastapi
  ```

  > **Note**:\
  > If you want to clear any storage in Docker,
  >
  > ```shell
  > $ docker system prune -a
  > ```

- Check this container running in background

  ```shell
  $ sudo docker ps
  ```

### With Window service

- Install the latest pywin32.exe and Window Service requirements with pip

  ```shell
  $ pip install pywin32 --upgrade --no-cache
  $ pip install -r requirements.wins.txt --no-cache
  ```
  
- Compile your service.py using pyinstaller
 
  ```shell
  $ pyinstaller --paths "%cd%\venv\Lib\site-packages" \
    --onefile service.py \
    --hidden-import=win32timezone \
    --clean --uac-admin \
    --add-data '.env;.'
  ```
  
  > **Warning**: \
  > In argument `--add-data` on unix systems, you should write `:` instead of `;`

  > **Note**: \
  > After install `service.py`, it will create `/dist` and `/build` folders
  
  > **Note**: \
  > `--paths`: The pyinstaller will search for imports here \ 
  > `--hidden-import`: Which modules should be imported by pyinstaller from the path
  
- Installing service with startup == Automatic
  
  ```shell
  $ .\dist\service.exe --startup=auto install
  ```
  
  ```shell
  $ service.exe start
  $ service.exe stop
  $ service.exe debug
  $ service.exe remove
  ```

  > **Note**: \
  > If you want to set the `StartUp= Manual`, then don't use `--startup=auto`, while installing service \
  > If you want to set the `StartUp= Automatic`, then use `--startup=delayed`, while installing service \
  > Use `--startup` argument before install argument
  
  > **Warning**: \
  > This option has the Bug of `Error 1053: The service did not respond timely`
  > when start the service while debugging did not raise any error
  
  
- (Optional) Add file .exe file to Windows Service directly

  ```shell
  $ sc.exe create "FastAPIServiceName" binPath= "%cd%\dist\service.exe" \
    DisplayName= "FastAPI Service DisplayName" start= auto
  ```
  
  ```shell
  $ sc.exe create "FastAPIServiceName" binPath= "%cd%\venv\Scripts\python.exe %cd%\service.py" \
    DisplayName= "FastAPI Service DisplayName" start= auto
  ```
  
  ```shell
  $ sc.exe start 
  $ sc.exe delete demo_application
  ```
  
- Now your python service is installed as Windows service now. You can see it in Service Manager and registry under:

  `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\FastAPIServiceName`

> **Note**: \
> Another way to install Windows service, `pip install pysc`

> **Reference**: \
> docs: [How do you run a Python script as a Service in Windows](https://stackoverflow.com/questions/32404/how-do-you-run-a-python-script-as-a-service-in-windows)

### With Window service wrapped by NSSM

- Downloads and unzip NSSM package to server from [NSSM Download](https://nssm.cc/release/nssm-2.24.zip)
  
  ```text
  nssm-{version}
    ├─── src
    ├─── win32
    │    └─── nssm.exe
    ├─── win64
    │    └─── nssm.exe      <---- Use this file for run NSSM
    ├─── ChangeLog.txt
    └─── README.txt
  ```

- Install service with NSSM

  ```shell
  $ .\nssm\win64\nssm.exe install "FastAPIService" "%cd%\runserver.bat"
  ```

- (Optional) Set up logging from NSSM `stdout` and `stderr`

  ```shell
  $ .\nssm\win64\nssm.exe set "FastAPIService" AppStdout "%cd%\logs\FastAPIService.log"
  $ .\nssm\win64\nssm.exe set "FastAPIService" AppStderr "%cd%\logs\FastAPIService.log"
  $ .\nssm\win64\nssm.exe set "FastAPIService" AppRotateFiles 1
  $ .\nssm\win64\nssm.exe set "FastAPIService" AppRotateOnline 1
  $ .\nssm\win64\nssm.exe set "FastAPIService" AppRotateSeconds 86400
  $ .\nssm\win64\nssm.exe set "FastAPIService" AppRotateBytes 1048576
  ```

- Start Window service

  ```shell
  $ sc.exe start "FastAPIService"
  ```
  
- (Optional) NSSM command line

  ```shell
  $ .\nssm\win64\nssm.exe restart "FastAPIService"
  $ .\nssm\win64\nssm.exe edit "FastAPIService"
  $ .\nssm\win64\nssm.exe stop "FastAPIService"
  $ .\nssm\win64\nssm.exe remove "FastAPIService"
  ```

- Check all NSSM service

  ```shell
  $ Get-WmiObject win32_service | ?{$_.PathName -like '*nssm*'} | select Name, DisplayName, State, PathName
  ```

> **Reference**: \
> docs: [How to run a Python script Windows service NSSM](https://www.mssqltips.com/sqlservertip/7325/how-to-run-a-python-script-windows-service-nssm/)

### With Window Container on Hyper-V

- Install Docker module on PowerShell

```shell
$ Install-Module DockerMsftProvider -Force
$ Install-Package Docker -ProviderName DockerMsftProvider -Force
$ Restart-Computer
```

### With Linux Container on Hyper-V (LCOW)

- Install Docker module on PowerShell

```shell
$ Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart
```

```shell
$ Install-Module DockerProvider 
$ Install-Package Docker -ProviderName DockerProvider -RequiredVersion preview 
```

Reboot your machine manual once again.

```shell
$ Set-Content -Value "`{`"experimental`":true`}" -Path C:\ProgramData\docker\config\daemon.json
```

- Download [LCOW](https://github.com/linuxkit/lcow/releases) and install in Linux Container folder

```shell
$ [Environment]::SetEnvironmentVariable("LCOW_SUPPORTED", "1", "Machine")
$ Restart-Service docker 
```

### With Window task scheduler

> **Reference**: \
> docs: [How to run Python script in Windows](https://www.mssqltips.com/sqlservertip/7111/how-to-run-python-script-in-windows/) \
> docs: [Linux Containers on Windows server 2016](https://www.bdrsuite.com/blog/linux-containers-on-windows-server-2016-using-linuxkit/)

## Testing

The simple way to test this application running by request directly to hearth check route.

```shell
$ curl http://localhost:8000/health/
```

License
---

This project base on MIT License and depend on dependency package license in requirement file.
