# Steps to generate the Cython file (for any updates to the RAGNAROC model):

- Make required changes to the .pyx file
- In the docker command line, run the following commands after navigating to this folder
    - docker build -t <name> .
    - docker run <name>
- Check the name of the container generated (can be viewed on docker desktop). Then run the following command
    - docker export <suspect-container> > <suspect-container>.tar
    - Replace the name of the container in <suspect-container>. 
- Extract ragnaroc.so file present in the tar folder.
- Replace the newly generated so file for the existing one, and you've successfully updated the model. Congratulations! :tada:

We have to follow this process because the Cython generates dll file on a windows machine, whereas linux systems (such as the AWS server) generate an SO file.
