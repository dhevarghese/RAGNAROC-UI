# Steps to generate the cythonized binary file

Cython is used to achieve a performance gain over Python. The compiler generates very efficient code from Cython. On a Windows system, running `setup.py` generates a dll file optimized for Windows. Our AWS Elastic Beanstalk server uses a Linux environment, which requires a `.so` file. Therefore, in order to generate it, we must follow these steps.

- Install Docker on your device
- Make required changes to the .pyx file
- In the command line, run the following commands after navigating to this folder, where name is a name you chose for the docker image that you will make
    - `docker build -t <name> .`
- In the command line, then run this, which will create a container from the image you just created.   name will be the same in the previous command
    - `docker run <name>`
- In Docker desktop, find the container that was just created, and copy the container ID, which is a list of random letters and numbers
- Then run the following command
    - `docker cp <containerID>:/ragnaroc.cpython-38-x86_64-linux-gnu.so .`
- Replace the newly generated `.so` file for the existing one in the zip file that you have from Elastic Beanstalk and re-upload it, and you've successfully updated the model. Congratulations! :tada:


