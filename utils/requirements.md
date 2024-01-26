# Requirements

> [!IMPORTANT]  
> The core requirements for using our simulation framework CARLOS are listed below:
> - [Ubuntu 20.04 LTS Focal](https://ubuntu.com/download/desktop) (or higher) with `sudo` permission
> - enough hard disk storage, which depends on the workshop and use-case (~50 GB are recommended)
> - NVIDIA GPU (at least 8 GB GPU memory are recommended)

> [!NOTE]  
> Make sure to install all prerequisites and that GUI access is available: 
> - [Nvidia Driver](https://ubuntu.com/server/docs/nvidia-drivers-installation) (validate installation with `nvidia-smi`)
> - Docker Installation
>     - [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04)
>     - [Docker Compose](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04)
>     - [Nvidia Docker](https://github.com/NVIDIA/nvidia-docker)

> [!WARNING]  
> Make sure that your machine has access to its X server to enable graphical output.
> ```bash
> xhost +local:
> ```
