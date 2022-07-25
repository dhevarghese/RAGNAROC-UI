# Steps to generate the cython file

Cython is used to achieve a performance gain over Python. The compiler generates very efficient code from Cython. On a Windows system, running `setup.py` generates a dll file optimized for Windows. Our AWS Elastic Beanstalk server uses a Linux environment, which requires a `.so` file. Therefore, in order to generate it, we must follow these steps.

- Install Docker on your device
- Make required changes to the .pyx file
- In the command line, run the following commands after navigating to this folder
    - `docker build -t <name> .`
    - `docker run <name>`
- Check the name of the container generated (can be viewed on docker desktop). Then run the following command
    - `docker export <suspect-container> > <suspect-container>.tar`
- Extract ragnaroc.so file present in the tar folder.
- Replace the newly generated `.so` file for the existing one, and you've successfully updated the model. Congratulations! :tada:


